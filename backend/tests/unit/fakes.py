"""Fakes em memória dos repositories: os services são testados sem HTTP e sem banco."""
from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from app.core.errors import ConflitoReservaError
from app.domain.reservaObserver import EventBus
from app.models.reservaModel import STATUS_VIVOS


class FakeHospedeRepository:
    def __init__(self):
        self.itens: dict[int, SimpleNamespace] = {}
        self._seq = 0

    def get(self, id_):
        return self.itens.get(id_)

    def get_por_documento(self, tipo, numero):
        return next((h for h in self.itens.values()
                     if h.documento_tipo == tipo and h.documento_numero == numero), None)

    def add(self, h):
        self._seq += 1
        h.id = self._seq
        self.itens[h.id] = h
        return h

    def salvar(self, h):
        return h

    def buscar(self, q, limite, offset):
        itens = list(self.itens.values())
        return itens[offset:offset + limite], len(itens)


class FakeAcomodacaoRepository:
    def __init__(self, *acomodacoes):
        self.itens = {a.id: a for a in acomodacoes}

    def get(self, id_):
        return self.itens.get(id_)


class FakeReservaRepository:
    def __init__(self):
        self.itens: dict[int, SimpleNamespace] = {}
        self._seq = 0
        self.add_forcando_corrida = False

    def get(self, id_):
        return self.itens.get(id_)

    def existe_conflito(self, acomodacao_id, entrada, saida, ignorar_id=None):
        return any(r.acomodacao_id == acomodacao_id and r.status in STATUS_VIVOS and r.id != ignorar_id
                   and r.data_entrada < saida and entrada < r.data_saida for r in self.itens.values())

    def vivas_da_acomodacao(self, acomodacao_id):
        return [r for r in self.itens.values() if r.acomodacao_id == acomodacao_id and r.status in STATUS_VIVOS]

    def add(self, r):
        if self.add_forcando_corrida:
            raise ConflitoReservaError()      # o que o repository real faz ao receber 23P01
        self._seq += 1
        r.id = self._seq
        self.itens[r.id] = r
        return r

    def salvar(self, r):
        return r


def acomodacao(id_=1, capacidade=2, valor="100.00", ativo=True):
    return SimpleNamespace(id=id_, numero=str(100 + id_), capacidade=capacidade, valor_diaria=Decimal(valor),
                           ativo=ativo, status="LIVRE")


class Capturador:
    """Assinante que guarda os eventos publicados, na ordem."""

    def __init__(self, bus: EventBus, *tipos):
        self.eventos = []
        for t in tipos:
            bus.subscribe(t, self.eventos.append)


AGORA = datetime(2026, 11, 6, 12, tzinfo=timezone.utc)
HOJE = date(2026, 11, 6)


def reserva(status="PENDENTE", entrada=date(2026, 12, 10), saida=date(2026, 12, 12), diaria="100.00"):
    """Reserva em memória (sem banco) para testar State, política de status e controllers."""
    return SimpleNamespace(status=status, data_entrada=entrada, data_saida=saida, qtd_hospedes=1,
                           valor_diaria=Decimal(diaria), valor_total=Decimal("200.00"),
                           confirmada_em=None, cancelada_em=None, motivo_cancelamento=None,
                           checkin_em=None, checkout_em=None)


class FakeUsuarioRepository:
    def __init__(self, usuario=None):
        self.usuario = usuario

    def get_por_email(self, email):
        return self.usuario


class FakeAcomodacoesDisponiveis:
    """Repository de acomodações para DisponibilidadeService."""

    def __init__(self, *itens):
        self.itens = list(itens)

    def disponiveis(self, entrada, saida, hospedes, categoria_id):
        return [a for a in self.itens if a.capacidade >= hospedes]

    def listar(self, ativo=None):
        return self.itens


class FakeReservasNoPeriodo:
    def __init__(self, reservas=()):
        self.reservas = list(reservas)

    def no_periodo(self, ini, fim):
        return self.reservas


# ---- objetos "saída" completos, para os testes de controller (sem banco)
def hospede_obj(id_=1, nome="Ana Lima"):
    return SimpleNamespace(id=id_, nome=nome, documento_tipo="CPF", documento_numero="52998224725",
                           email="ana@x.com", telefone=None, criado_em=AGORA)


def acomodacao_obj(id_=1, numero="101", status="LIVRE"):
    return SimpleNamespace(id=id_, numero=numero, categoria=SimpleNamespace(id=1, nome="Standard", descricao=None),
                           capacidade=2, valor_diaria=Decimal("150.00"), status=status, ativo=True,
                           caracteristicas=[SimpleNamespace(id=1, nome="Wi-Fi")])


def reserva_obj(id_=1, status="PENDENTE"):
    base = reserva(status)
    return SimpleNamespace(**{**base.__dict__, "id": id_, "hospede": hospede_obj(),
                              "acomodacao": SimpleNamespace(id=1, numero="101", capacidade=2),
                              "acomodacao_id": 1, "noites": 2, "criada_em": AGORA})
