"""State: Pendente, Confirmada, EmAndamento, Encerrada e Cancelada (hierarquia de EstadoReserva)."""
from datetime import date
from decimal import Decimal

import pytest

from app.core.errors import RegraDeNegocioError, TransicaoInvalidaError
from app.domain.reservaState import Cancelada, Confirmada, EmAndamento, Encerrada, EstadoReserva, Pendente, estado_de
from tests.unit.fakes import AGORA, reserva


class EstadoReservaTest:
    @pytest.mark.parametrize("status,classe", [
        ("PENDENTE", Pendente), ("CONFIRMADA", Confirmada), ("EM_ANDAMENTO", EmAndamento),
        ("ENCERRADA", Encerrada), ("CANCELADA", Cancelada)])
    def test_estado_de_devolve_a_classe_do_status(self, status, classe):
        assert type(estado_de(reserva(status))) is classe and isinstance(estado_de(reserva(status)), EstadoReserva)

    def test_pendente_confirma_e_cancela(self):
        r = reserva("PENDENTE")
        estado_de(r).confirmar(r, AGORA)
        assert r.status == "CONFIRMADA" and r.confirmada_em == AGORA
        r2 = reserva("PENDENTE")
        estado_de(r2).cancelar(r2, " motivo ", AGORA)
        assert r2.status == "CANCELADA" and r2.cancelada_em == AGORA and r2.motivo_cancelamento == "motivo"

    def test_confirmada_faz_checkin_e_checkout_encerra(self):
        r = reserva("CONFIRMADA")
        estado_de(r).checkin(r, AGORA)
        assert r.status == "EM_ANDAMENTO" and r.checkin_em == AGORA
        estado_de(r).checkout(r, AGORA)
        assert r.status == "ENCERRADA" and r.checkout_em == AGORA

    @pytest.mark.parametrize("status,operacao", [
        ("PENDENTE", "checkin"), ("PENDENTE", "checkout"),
        ("CONFIRMADA", "confirmar"), ("CONFIRMADA", "checkout"),
        ("EM_ANDAMENTO", "confirmar"), ("EM_ANDAMENTO", "cancelar"), ("EM_ANDAMENTO", "alterar"), ("EM_ANDAMENTO", "checkin"),
        ("ENCERRADA", "confirmar"), ("ENCERRADA", "cancelar"), ("ENCERRADA", "alterar"), ("ENCERRADA", "checkin"),
        ("ENCERRADA", "checkout"),
        ("CANCELADA", "confirmar"), ("CANCELADA", "cancelar"), ("CANCELADA", "alterar"), ("CANCELADA", "checkin"),
    ])
    def test_transicoes_invalidas_levantam_409(self, status, operacao):
        r = reserva(status)
        args = {"confirmar": (AGORA,), "cancelar": (None, AGORA), "checkin": (AGORA,), "checkout": (AGORA,),
                "alterar": (date(2026, 12, 10), date(2026, 12, 11), 1, 2)}[operacao]
        with pytest.raises(TransicaoInvalidaError) as e:
            getattr(estado_de(r), operacao)(r, *args)
        assert e.value.status_code == 409
        with pytest.raises(TransicaoInvalidaError):
            estado_de(r).exigir(operacao)
        assert r.status == status    # nada mudou

    def test_exigir_nao_altera_a_reserva_quando_permitido(self):
        r = reserva("PENDENTE")
        estado_de(r).exigir("confirmar")
        assert r.status == "PENDENTE"

    def test_alterar_recalcula_total_com_a_diaria_copiada(self):
        r = reserva("CONFIRMADA", diaria="80.00")
        estado_de(r).alterar(r, date(2026, 12, 10), date(2026, 12, 14), 2, capacidade=2)
        assert r.valor_total == Decimal("320.00") and r.qtd_hospedes == 2

    def test_alterar_rejeita_periodo_e_capacidade_invalidos(self):
        r = reserva()
        with pytest.raises(RegraDeNegocioError):
            estado_de(r).alterar(r, date(2026, 12, 10), date(2026, 12, 10), 1, 2)
        with pytest.raises(RegraDeNegocioError):
            estado_de(r).alterar(r, date(2026, 12, 10), date(2026, 12, 11), 3, 2)
