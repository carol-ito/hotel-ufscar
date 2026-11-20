from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.errors import DuplicidadeError, NaoEncontradoError, RegraDeNegocioError
from app.models import Acomodacao, Caracteristica
from app.services.acomodacaoService import AcomodacaoService
from tests.conftest import RelogioFixo


class FakeAcomodacoes:
    def __init__(self, *itens):
        self.itens = {a.id: a for a in itens}
        self._seq = max(self.itens, default=0)

    def get(self, id_):
        return self.itens.get(id_)

    def get_por_numero(self, numero):
        return next((a for a in self.itens.values() if a.numero == numero), None)

    def listar(self, ativo=None, categoria_id=None, status=None):
        return list(self.itens.values())

    def add(self, a):
        self._seq += 1
        a.id = self._seq
        self.itens[a.id] = a
        return a

    def salvar(self, a):
        return a


class FakeCategorias:
    def get(self, id_):
        return SimpleNamespace(id=id_) if id_ in (1, 2) else None


class FakeCaracteristicas:
    def por_ids(self, ids):
        return [Caracteristica(id=i, nome=f"c{i}") for i in ids if i in (1, 2)]


class FakeReservasVivas:
    def __init__(self, *reservas):
        self.reservas = list(reservas)

    def vivas_a_partir_de(self, acomodacao_id, hoje):
        return self.reservas


def quarto(id_=1, numero="101", capacidade=2):
    return SimpleNamespace(id=id_, numero=numero, categoria_id=1, capacidade=capacidade, valor_diaria=Decimal("100"),
                           ativo=True, status="LIVRE", caracteristicas=[])


def dados(**kw):
    base = dict(numero="301", categoria_id=1, capacidade=2, valor_diaria=Decimal("200"), caracteristica_ids=[1, 2, 2])
    return SimpleNamespace(**{**base, **kw})


def service(acomodacoes=(), reservas=()):
    return AcomodacaoService(FakeAcomodacoes(*acomodacoes), FakeCategorias(), FakeCaracteristicas(),
                             FakeReservasVivas(*reservas), RelogioFixo())


class AcomodacaoServiceTest:
    def test_criar_comeca_livre_e_ativa_e_remove_caracteristicas_repetidas(self):
        a = service().criar(dados())
        assert isinstance(a, Acomodacao) and (a.status, a.ativo) == ("LIVRE", True)
        assert sorted(c.id for c in a.caracteristicas) == [1, 2]

    def test_criar_numero_duplicado_409(self):
        with pytest.raises(DuplicidadeError):
            service([quarto(numero="301")]).criar(dados())

    @pytest.mark.parametrize("kw", [dict(categoria_id=99), dict(caracteristica_ids=[1, 99])])
    def test_criar_com_categoria_ou_caracteristica_inexistente_404(self, kw):
        with pytest.raises(NaoEncontradoError):
            service().criar(dados(**kw))

    def test_obter_inexistente_404(self):
        with pytest.raises(NaoEncontradoError):
            service().obter(1)

    def test_atualizar_aceita_o_proprio_numero_mas_nao_o_de_outro(self):
        s = service([quarto(1, "101"), quarto(2, "102")])
        assert s.atualizar(1, dados(numero="101")).numero == "101"
        with pytest.raises(DuplicidadeError):
            s.atualizar(1, dados(numero="102"))

    def test_nao_reduz_capacidade_abaixo_de_reserva_ativa(self):
        s = service([quarto(1, capacidade=4)], reservas=[SimpleNamespace(qtd_hospedes=3)])
        with pytest.raises(RegraDeNegocioError, match="capacidade"):
            s.atualizar(1, dados(numero="101", capacidade=2))
        assert s.atualizar(1, dados(numero="101", capacidade=3)).capacidade == 3

    def test_inativar_bloqueado_com_reserva_ativa(self):
        s = service([quarto(1)], reservas=[SimpleNamespace(qtd_hospedes=1)])
        with pytest.raises(RegraDeNegocioError, match="reservas ativas"):
            s.definir_ativo(1, False)
        assert s.definir_ativo(1, True).ativo is True      # reativar nunca é bloqueado

    def test_inativar_sem_reservas_funciona(self):
        assert service([quarto(1)]).definir_ativo(1, False).ativo is False
