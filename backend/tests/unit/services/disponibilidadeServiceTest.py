from datetime import date
from types import SimpleNamespace

import pytest

from app.core.errors import RegraDeNegocioError
from app.services.disponibilidadeService import DisponibilidadeService
from tests.conftest import RelogioFixo
from tests.unit.fakes import FakeAcomodacoesDisponiveis, FakeReservasNoPeriodo, acomodacao


class DisponibilidadeServiceTest:
    def test_consultar_calcula_noites_e_total_e_filtra_capacidade(self):
        s = DisponibilidadeService(FakeAcomodacoesDisponiveis(acomodacao(1, 2, "100.00"), acomodacao(2, 4, "250.00")),
                                   FakeReservasNoPeriodo(), RelogioFixo())
        r = s.consultar(date(2026, 12, 1), date(2026, 12, 4), 3)
        assert [(d.acomodacao.id, d.noites, str(d.valor_total)) for d in r] == [(2, 3, "750.00")]

    @pytest.mark.parametrize("entrada,saida,hospedes", [
        (date(2026, 12, 4), date(2026, 12, 4), 1), (date(2026, 12, 5), date(2026, 12, 4), 1),
        (date(2026, 11, 5), date(2026, 11, 8), 1), (date(2026, 12, 1), date(2026, 12, 2), 0)])
    def test_consultar_valida_entrada(self, entrada, saida, hospedes):
        s = DisponibilidadeService(FakeAcomodacoesDisponiveis(), FakeReservasNoPeriodo(), RelogioFixo())
        with pytest.raises(RegraDeNegocioError):
            s.consultar(entrada, saida, hospedes)

    def test_consultar_aceita_entrada_hoje(self):
        s = DisponibilidadeService(FakeAcomodacoesDisponiveis(acomodacao(1)), FakeReservasNoPeriodo(), RelogioFixo())
        assert len(s.consultar(date(2026, 11, 6), date(2026, 11, 7), 1)) == 1

    def test_mapa_agrupa_por_acomodacao(self):
        r1 = SimpleNamespace(acomodacao_id=1, id=1)
        s = DisponibilidadeService(FakeAcomodacoesDisponiveis(acomodacao(1), acomodacao(2)), FakeReservasNoPeriodo([r1]), RelogioFixo())
        mapa = s.mapa(date(2026, 12, 1), date(2026, 12, 31))
        assert [(a.id, len(rs)) for a, rs in mapa] == [(1, 1), (2, 0)]

    def test_mapa_limita_o_periodo_a_62_dias_e_exige_fim_depois_do_inicio(self):
        s = DisponibilidadeService(FakeAcomodacoesDisponiveis(), FakeReservasNoPeriodo(), RelogioFixo())
        with pytest.raises(RegraDeNegocioError):
            s.mapa(date(2026, 1, 1), date(2026, 12, 31))
        with pytest.raises(RegraDeNegocioError):
            s.mapa(date(2026, 12, 2), date(2026, 12, 1))
        s.mapa(date(2026, 12, 1), date(2027, 1, 31))      # exatamente 61 dias: ok
