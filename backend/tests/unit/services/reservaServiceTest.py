from datetime import date
from types import SimpleNamespace

import pytest

from app.core.errors import (ConflitoReservaError, NaoEncontradoError, RegraDeNegocioError,
                             TransicaoInvalidaError)
from app.domain.reservaObserver import (EVENTOS_QUE_ATUALIZAM_STATUS, AtualizarStatusAcomodacao, EventBus,
                                ReservaAlterada, ReservaCancelada, ReservaConfirmada, ReservaCriada)
from app.services.reservaService import ReservaService
from tests.conftest import RelogioFixo
from tests.unit.fakes import (Capturador, FakeAcomodacaoRepository, FakeHospedeRepository,
                              FakeReservaRepository, acomodacao)


@pytest.fixture
def ctx():
    hospedes, reservas = FakeHospedeRepository(), FakeReservaRepository()
    acomodacoes = FakeAcomodacaoRepository(acomodacao(1, capacidade=2, valor="100.00"),
                                           acomodacao(2, capacidade=4, ativo=False))
    hospedes.add(SimpleNamespace(nome="Ana"))
    bus = EventBus()
    cap = Capturador(bus, *EVENTOS_QUE_ATUALIZAM_STATUS)
    service = ReservaService(reservas, hospedes, acomodacoes, bus, RelogioFixo())
    return SimpleNamespace(service=service, reservas=reservas, acomodacoes=acomodacoes, eventos=cap.eventos, bus=bus)


def dados(entrada=date(2026, 12, 10), saida=date(2026, 12, 12), qtd=2, acomodacao_id=1, hospede_id=1):
    return SimpleNamespace(hospede_id=hospede_id, acomodacao_id=acomodacao_id, data_entrada=entrada,
                           data_saida=saida, qtd_hospedes=qtd)


class ReservaServiceTest:
    def test_criar_publica_evento_depois_de_gravar(self, ctx):
        r = ctx.service.criar(dados(), usuario_id=5)
        assert r.id == 1 and r.status == "PENDENTE" and r.criada_por == 5
        assert [type(e) for e in ctx.eventos] == [ReservaCriada]
        assert ctx.eventos[0].reserva_id == 1 and ctx.eventos[0].acomodacao_id == 1


    @pytest.mark.parametrize("kwargs,erro", [
        (dict(hospede_id=99), NaoEncontradoError),
        (dict(acomodacao_id=99), NaoEncontradoError),
        (dict(acomodacao_id=2), RegraDeNegocioError),                       # inativa
        (dict(qtd=3), RegraDeNegocioError),                                 # acima da capacidade
        (dict(entrada=date(2026, 11, 5), saida=date(2026, 11, 7)), RegraDeNegocioError),   # passado
    ])
    def test_criar_validacoes_sem_efeito_colateral(self, ctx, kwargs, erro):
        with pytest.raises(erro):
            ctx.service.criar(dados(**kwargs), 1)
        assert ctx.reservas.itens == {} and ctx.eventos == []


    def test_entrada_hoje_e_permitida(self, ctx):
        assert ctx.service.criar(dados(entrada=date(2026, 11, 6), saida=date(2026, 11, 7)), 1).id == 1


    def test_conflito_na_precheckagem_nao_grava_nem_publica(self, ctx):
        ctx.service.criar(dados(), 1)
        ctx.eventos.clear()
        with pytest.raises(ConflitoReservaError):
            ctx.service.criar(dados(entrada=date(2026, 12, 11), saida=date(2026, 12, 13)), 1)
        assert len(ctx.reservas.itens) == 1 and ctx.eventos == []


    def test_conflito_decidido_pelo_banco_na_corrida(self, ctx):
        ctx.reservas.add_forcando_corrida = True      # passa na pré-checagem, o banco recusa
        with pytest.raises(ConflitoReservaError):
            ctx.service.criar(dados(), 1)
        assert ctx.eventos == []


    def test_saida_no_dia_da_entrada_nao_conflita(self, ctx):
        ctx.service.criar(dados(entrada=date(2026, 12, 10), saida=date(2026, 12, 12)), 1)
        assert ctx.service.criar(dados(entrada=date(2026, 12, 12), saida=date(2026, 12, 14)), 1).id == 2


    def test_cancelar_libera_o_periodo_e_publica(self, ctx):
        r = ctx.service.criar(dados(), 1)
        ctx.service.cancelar(r.id, "desistiu")
        assert r.status == "CANCELADA" and r.motivo_cancelamento == "desistiu" and r.cancelada_em
        assert type(ctx.eventos[-1]) is ReservaCancelada
        assert ctx.service.criar(dados(), 1).id == 2


    def test_confirmar_publica_e_nao_repete(self, ctx):
        r = ctx.service.criar(dados(), 1)
        ctx.service.confirmar(r.id)
        assert r.status == "CONFIRMADA" and type(ctx.eventos[-1]) is ReservaConfirmada
        with pytest.raises(TransicaoInvalidaError):
            ctx.service.confirmar(r.id)


    def test_confirmar_periodo_encerrado_422(self, ctx):
        r = ctx.service.criar(dados(entrada=date(2026, 11, 6), saida=date(2026, 11, 7)), 1)
        r.data_saida = date(2026, 11, 6)       # simula reserva pendente esquecida
        with pytest.raises(RegraDeNegocioError):
            ctx.service.confirmar(r.id)


    def test_alterar_ignora_a_propria_reserva_e_publica(self, ctx):
        r = ctx.service.criar(dados(), 1)
        ctx.service.alterar(r.id, SimpleNamespace(data_entrada=date(2026, 12, 10), data_saida=date(2026, 12, 15), qtd_hospedes=2))
        assert r.valor_total == 500 and type(ctx.eventos[-1]) is ReservaAlterada


    def test_alterar_conflito_nao_muda_a_reserva(self, ctx):
        a = ctx.service.criar(dados(), 1)
        ctx.service.criar(dados(entrada=date(2026, 12, 20), saida=date(2026, 12, 22)), 1)
        with pytest.raises(ConflitoReservaError):
            ctx.service.alterar(a.id, SimpleNamespace(data_entrada=date(2026, 12, 10), data_saida=date(2026, 12, 21), qtd_hospedes=2))
        assert a.data_saida == date(2026, 12, 12)


    def test_obter_inexistente(self, ctx):
        with pytest.raises(NaoEncontradoError):
            ctx.service.obter(42)


    def test_ordem_dos_eventos(self, ctx):
        r = ctx.service.criar(dados(), 1)
        ctx.service.confirmar(r.id)
        ctx.service.cancelar(r.id, None)
        assert [type(e) for e in ctx.eventos] == [ReservaCriada, ReservaConfirmada, ReservaCancelada]


    def test_assinante_recalcula_status_do_quarto(self, ctx):
        assinante = AtualizarStatusAcomodacao(ctx.acomodacoes, ctx.reservas, RelogioFixo().hoje)
        for tipo in EVENTOS_QUE_ATUALIZAM_STATUS:
            ctx.bus.subscribe(tipo, assinante)
        r = ctx.service.criar(dados(entrada=date(2026, 11, 6), saida=date(2026, 11, 8)), 1)
        assert ctx.acomodacoes.get(1).status == "LIVRE"
        ctx.service.confirmar(r.id)
        assert ctx.acomodacoes.get(1).status == "RESERVADO"
        ctx.service.cancelar(r.id, None)
        assert ctx.acomodacoes.get(1).status == "LIVRE"
