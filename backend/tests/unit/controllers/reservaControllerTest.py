from datetime import date
from unittest.mock import Mock

import pytest

from app.controllers import reservaController as c
from app.dtos.reservaDTO import AlterarReservaIn, CancelarIn, NovaReservaIn
from tests.unit.fakes import reserva_obj

NOVA = NovaReservaIn(hospede_id=1, acomodacao_id=1, data_entrada=date(2026, 12, 10), data_saida=date(2026, 12, 12), qtd_hospedes=2)


class ReservaControllerTest:
    @pytest.mark.parametrize("status,acoes", [
        ("PENDENTE", ["alterar", "confirmar", "cancelar"]), ("CONFIRMADA", ["alterar", "cancelar"]),
        ("EM_ANDAMENTO", []), ("ENCERRADA", []), ("CANCELADA", [])])
    def test_saida_informa_as_acoes_permitidas_pelo_estado(self, status, acoes):
        assert c._saida(reserva_obj(status=status)).acoes_permitidas == acoes

    def test_criar_registra_o_usuario_que_criou(self):
        service = Mock(criar=Mock(return_value=reserva_obj()))
        r = c.criar(NOVA, usuario=Mock(id=5), service=service)
        service.criar.assert_called_once_with(NOVA, 5)
        assert r.status == "PENDENTE" and r.hospede.nome == "Ana Lima"

    def test_listar_repassa_filtros_e_monta_pagina(self):
        service = Mock(listar=Mock(return_value=([reserva_obj(1), reserva_obj(2, "CONFIRMADA")], 9)))
        pagina = c.listar(status="PENDENTE", hospede_id=1, acomodacao_id=2, entrada_de=date(2026, 12, 1),
                          entrada_ate=None, limite=2, offset=2, _=None, service=service)
        service.listar.assert_called_once_with(status="PENDENTE", hospede_id=1, acomodacao_id=2,
                                               entrada_de=date(2026, 12, 1), entrada_ate=None, limite=2, offset=2)
        assert (pagina.total, pagina.limite, pagina.offset) == (9, 2, 2)
        assert pagina.itens[1].acoes_permitidas == ["alterar", "cancelar"]

    def test_obter_confirmar_e_alterar_delegam(self):
        service = Mock(obter=Mock(return_value=reserva_obj()), confirmar=Mock(return_value=reserva_obj(status="CONFIRMADA")),
                       alterar=Mock(return_value=reserva_obj()))
        c.obter(1, _=None, service=service)
        assert c.confirmar(1, _=None, service=service).status == "CONFIRMADA"
        dados = AlterarReservaIn(data_entrada=date(2026, 12, 10), data_saida=date(2026, 12, 11), qtd_hospedes=1)
        c.alterar(1, dados, _=None, service=service)
        service.obter.assert_called_once_with(1)
        service.confirmar.assert_called_once_with(1)
        service.alterar.assert_called_once_with(1, dados)

    def test_cancelar_com_e_sem_corpo(self):
        service = Mock(cancelar=Mock(return_value=reserva_obj(status="CANCELADA")))
        c.cancelar(1, CancelarIn(motivo="desistiu"), _=None, service=service)
        c.cancelar(2, None, _=None, service=service)
        assert [x.args for x in service.cancelar.call_args_list] == [(1, "desistiu"), (2, None)]
