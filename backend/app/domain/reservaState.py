"""State: cada status é uma classe que implementa só as operações permitidas nele.
As demais caem na classe base e levantam TransicaoInvalidaError (HTTP 409)."""
from datetime import date, datetime
from decimal import Decimal

from app.core.errors import RegraDeNegocioError, TransicaoInvalidaError
from app.domain.reservaFactory import calcular_valor_total


class EstadoReserva:
    nome = "?"
    permite: frozenset[str] = frozenset()

    def exigir(self, operacao: str):
        """Confere a transição sem alterar nada (usado antes de consultar o banco)."""
        if operacao not in self.permite:
            raise TransicaoInvalidaError(self.nome, operacao)

    def confirmar(self, reserva, agora: datetime):
        raise TransicaoInvalidaError(self.nome, "confirmar")

    def cancelar(self, reserva, motivo: str | None, agora: datetime):
        raise TransicaoInvalidaError(self.nome, "cancelar")

    def alterar(self, reserva, entrada: date, saida: date, qtd_hospedes: int, capacidade: int):
        raise TransicaoInvalidaError(self.nome, "alterar")

    def checkin(self, reserva, agora: datetime):
        raise TransicaoInvalidaError(self.nome, "checkin")

    def checkout(self, reserva, agora: datetime):
        raise TransicaoInvalidaError(self.nome, "checkout")


def _cancelar(reserva, motivo: str | None, agora: datetime):
    reserva.status = "CANCELADA"
    reserva.cancelada_em = agora
    reserva.motivo_cancelamento = (motivo or "").strip() or None


def _alterar(reserva, entrada: date, saida: date, qtd_hospedes: int, capacidade: int):
    if saida <= entrada:
        raise RegraDeNegocioError("A data de saída deve ser posterior à de entrada")
    if qtd_hospedes > capacidade:
        raise RegraDeNegocioError(f"A acomodação comporta no máximo {capacidade} hóspede(s)")
    reserva.data_entrada, reserva.data_saida, reserva.qtd_hospedes = entrada, saida, qtd_hospedes
    # a diária copiada na criação é mantida: mudar o preço do quarto não reprecifica a reserva
    reserva.valor_total = calcular_valor_total(Decimal(reserva.valor_diaria), entrada, saida)


class Pendente(EstadoReserva):
    nome = "PENDENTE"
    permite = frozenset({"alterar", "confirmar", "cancelar"})

    def confirmar(self, reserva, agora):
        reserva.status = "CONFIRMADA"
        reserva.confirmada_em = agora

    def cancelar(self, reserva, motivo, agora):
        _cancelar(reserva, motivo, agora)

    def alterar(self, reserva, entrada, saida, qtd_hospedes, capacidade):
        _alterar(reserva, entrada, saida, qtd_hospedes, capacidade)


class Confirmada(EstadoReserva):
    nome = "CONFIRMADA"
    permite = frozenset({"alterar", "checkin", "cancelar"})

    def cancelar(self, reserva, motivo, agora):
        _cancelar(reserva, motivo, agora)

    def alterar(self, reserva, entrada, saida, qtd_hospedes, capacidade):
        _alterar(reserva, entrada, saida, qtd_hospedes, capacidade)

    def checkin(self, reserva, agora):
        reserva.status = "EM_ANDAMENTO"
        reserva.checkin_em = agora


class EmAndamento(EstadoReserva):
    nome = "EM_ANDAMENTO"
    permite = frozenset({"checkout"})

    def checkout(self, reserva, agora):
        reserva.status = "ENCERRADA"
        reserva.checkout_em = agora


class Encerrada(EstadoReserva):
    nome = "ENCERRADA"


class Cancelada(EstadoReserva):
    nome = "CANCELADA"


_ESTADOS = {e.nome: e() for e in (Pendente, Confirmada, EmAndamento, Encerrada, Cancelada)}


def estado_de(reserva) -> EstadoReserva:
    return _ESTADOS[reserva.status]
