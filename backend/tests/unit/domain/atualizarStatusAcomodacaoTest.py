from datetime import date
from types import SimpleNamespace

from app.domain.reservaObserver import AtualizarStatusAcomodacao, ReservaConfirmada
from tests.unit.fakes import FakeAcomodacaoRepository, FakeReservaRepository, HOJE, acomodacao, reserva


class AtualizarStatusAcomodacaoTest:
    def _montar(self, *reservas):
        acomodacoes = FakeAcomodacaoRepository(acomodacao(1))
        repo = FakeReservaRepository()
        for i, r in enumerate(reservas, 1):
            r.id, r.acomodacao_id = i, 1
            repo.itens[i] = r
        return AtualizarStatusAcomodacao(acomodacoes, repo, lambda: HOJE), acomodacoes

    def test_confirmada_cobrindo_hoje_marca_reservado(self):
        assinante, acomodacoes = self._montar(reserva("CONFIRMADA", date(2026, 11, 6), date(2026, 11, 8)))
        assinante(ReservaConfirmada(1, 1))
        assert acomodacoes.get(1).status == "RESERVADO"

    def test_sem_reservas_vivas_marca_livre(self):
        assinante, acomodacoes = self._montar(reserva("CANCELADA", date(2026, 11, 6), date(2026, 11, 8)))
        acomodacoes.get(1).status = "RESERVADO"
        assinante(ReservaConfirmada(1, 1))
        assert acomodacoes.get(1).status == "LIVRE"

    def test_usa_o_hoje_injetado_e_nao_a_data_real(self):
        acomodacoes = FakeAcomodacaoRepository(acomodacao(1))
        repo = FakeReservaRepository()
        r = reserva("CONFIRMADA", date(2030, 1, 1), date(2030, 1, 3)); r.id, r.acomodacao_id = 1, 1
        repo.itens[1] = r
        AtualizarStatusAcomodacao(acomodacoes, repo, lambda: date(2030, 1, 2))(ReservaConfirmada(1, 1))
        assert acomodacoes.get(1).status == "RESERVADO"
