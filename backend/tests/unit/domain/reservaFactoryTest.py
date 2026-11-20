from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.domain.reservaFactory import ReservaFactory, calcular_valor_total


class ReservaFactoryTest:
    def test_valor_total_uma_noite_e_varias(self):
        assert calcular_valor_total(Decimal("150"), date(2026, 12, 1), date(2026, 12, 2)) == Decimal("150.00")
        assert calcular_valor_total(Decimal("150.50"), date(2026, 12, 1), date(2026, 12, 4)) == Decimal("451.50")

    def test_cria_pendente_copiando_a_diaria_da_acomodacao(self):
        dados = SimpleNamespace(hospede_id=1, data_entrada=date(2026, 12, 1), data_saida=date(2026, 12, 3), qtd_hospedes=2)
        quarto = SimpleNamespace(id=7, valor_diaria=Decimal("200.00"))
        r = ReservaFactory.criar(dados, quarto, criada_por=9)
        assert (r.status, r.valor_diaria, r.valor_total, r.acomodacao_id, r.criada_por) == \
               ("PENDENTE", Decimal("200.00"), Decimal("400.00"), 7, 9)

    def test_mudar_a_diaria_do_quarto_depois_nao_altera_a_reserva_criada(self):
        dados = SimpleNamespace(hospede_id=1, data_entrada=date(2026, 12, 1), data_saida=date(2026, 12, 3), qtd_hospedes=2)
        quarto = SimpleNamespace(id=7, valor_diaria=Decimal("200.00"))
        r = ReservaFactory.criar(dados, quarto, criada_por=9)
        quarto.valor_diaria = Decimal("999.00")
        assert r.valor_diaria == Decimal("200.00") and r.valor_total == Decimal("400.00")
