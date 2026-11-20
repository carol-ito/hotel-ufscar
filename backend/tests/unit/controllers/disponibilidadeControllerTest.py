from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from app.controllers import disponibilidadeController as c
from tests.unit.fakes import acomodacao_obj, hospede_obj


class DisponibilidadeControllerTest:
    def test_consultar_devolve_acomodacoes_livres_com_total(self):
        disp = SimpleNamespace(acomodacao=acomodacao_obj(), noites=2, valor_total=Decimal("300.00"))
        service = Mock(consultar=Mock(return_value=[disp]))
        r = c.consultar(entrada=date(2026, 12, 1), saida=date(2026, 12, 3), hospedes=1, categoria_id=1,
                        _=None, service=service)
        service.consultar.assert_called_once_with(date(2026, 12, 1), date(2026, 12, 3), 1, 1)
        assert [(d.noites, d.valor_total) for d in r] == [(2, Decimal("300.00"))]

    def test_mapa_monta_linhas_com_o_nome_do_hospede(self):
        reserva = SimpleNamespace(id=9, hospede=hospede_obj(nome="Maria"), data_entrada=date(2026, 12, 10),
                                  data_saida=date(2026, 12, 12), status="CONFIRMADA")
        service = Mock(mapa=Mock(return_value=[(acomodacao_obj(1), [reserva]), (acomodacao_obj(2, "102"), [])]))
        linhas = c.mapa(ini=date(2026, 12, 1), fim=date(2026, 12, 31), _=None, service=service)
        service.mapa.assert_called_once_with(date(2026, 12, 1), date(2026, 12, 31))
        assert linhas[0].reservas[0].hospede_nome == "Maria" and linhas[0].reservas[0].status == "CONFIRMADA"
        assert linhas[1].reservas == [] and linhas[1].acomodacao.numero == "102"
