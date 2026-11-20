"""Observer: eventos de domínio entregues de forma síncrona, na mesma transação."""
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class EventoReserva:
    reserva_id: int
    acomodacao_id: int


class ReservaCriada(EventoReserva): pass
class ReservaAlterada(EventoReserva): pass
class ReservaConfirmada(EventoReserva): pass
class ReservaCancelada(EventoReserva): pass
class CheckInRealizado(EventoReserva): pass
class CheckOutRealizado(EventoReserva): pass


class EventBus:
    def __init__(self):
        self._assinantes: dict[type, list[Callable]] = defaultdict(list)

    def subscribe(self, tipo: type, assinante: Callable):
        self._assinantes[tipo].append(assinante)

    def publish(self, evento):
        for assinante in self._assinantes[type(evento)]:
            assinante(evento)


class AtualizarStatusAcomodacao:
    """Recalcula o status do quarto sem que Reserva e Acomodação se conheçam."""

    def __init__(self, acomodacoes, reservas, hoje: Callable):
        self.acomodacoes, self.reservas, self.hoje = acomodacoes, reservas, hoje

    def __call__(self, evento):
        from app.domain.politicaStatus import calcular_status
        acomodacao = self.acomodacoes.get(evento.acomodacao_id)
        vivas = self.reservas.vivas_da_acomodacao(evento.acomodacao_id)
        acomodacao.status = calcular_status(vivas, self.hoje())


EVENTOS_QUE_ATUALIZAM_STATUS = (ReservaCriada, ReservaAlterada, ReservaConfirmada,
                                ReservaCancelada, CheckInRealizado, CheckOutRealizado)
