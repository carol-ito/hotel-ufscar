from app.core.errors import ConflitoReservaError, NaoEncontradoError, RegraDeNegocioError
from app.domain.reservaState import estado_de
from app.domain.reservaObserver import ReservaAlterada, ReservaCancelada, ReservaConfirmada, ReservaCriada
from app.domain.reservaFactory import ReservaFactory


class ReservaService:
    """Casos de uso de reserva: validar → criar → gravar → publicar evento."""

    def __init__(self, reservas, hospedes, acomodacoes, eventos, relogio):
        self.reservas, self.hospedes, self.acomodacoes = reservas, hospedes, acomodacoes
        self.eventos, self.relogio = eventos, relogio

    # ---- consultas
    def obter(self, reserva_id: int):
        reserva = self.reservas.get(reserva_id)
        if reserva is None:
            raise NaoEncontradoError("Reserva não encontrada")
        return reserva

    def listar(self, **filtros):
        return self.reservas.listar(**filtros)

    # ---- casos de uso
    def criar(self, dados, usuario_id: int):
        if self.hospedes.get(dados.hospede_id) is None:
            raise NaoEncontradoError("Hóspede não encontrado")
        acomodacao = self._acomodacao_reservavel(dados.acomodacao_id, dados.qtd_hospedes, dados.data_entrada)
        if self.reservas.existe_conflito(acomodacao.id, dados.data_entrada, dados.data_saida):
            raise ConflitoReservaError()          # pré-checagem: mensagem rápida
        reserva = ReservaFactory.criar(dados, acomodacao, usuario_id)
        self.reservas.add(reserva)                # o banco decide se houver corrida
        self.eventos.publish(ReservaCriada(reserva.id, acomodacao.id))
        return reserva

    def alterar(self, reserva_id: int, dados):
        reserva = self.obter(reserva_id)
        estado = estado_de(reserva)
        estado.exigir("alterar")
        acomodacao = self.acomodacoes.get(reserva.acomodacao_id)
        if dados.data_entrada != reserva.data_entrada and dados.data_entrada < self.relogio.hoje():
            raise RegraDeNegocioError("A data de entrada não pode estar no passado")
        if dados.qtd_hospedes > acomodacao.capacidade:
            raise RegraDeNegocioError(f"A acomodação comporta no máximo {acomodacao.capacidade} hóspede(s)")
        if self.reservas.existe_conflito(reserva.acomodacao_id, dados.data_entrada, dados.data_saida,
                                         ignorar_id=reserva.id):
            raise ConflitoReservaError()
        estado.alterar(reserva, dados.data_entrada, dados.data_saida, dados.qtd_hospedes, acomodacao.capacidade)
        self.reservas.salvar(reserva)
        self.eventos.publish(ReservaAlterada(reserva.id, reserva.acomodacao_id))
        return reserva

    def confirmar(self, reserva_id: int):
        reserva = self.obter(reserva_id)
        estado = estado_de(reserva)
        estado.exigir("confirmar")
        if reserva.data_saida <= self.relogio.hoje():
            raise RegraDeNegocioError("O período desta reserva já terminou; não é possível confirmar")
        estado.confirmar(reserva, self.relogio.agora())
        self.reservas.salvar(reserva)
        self.eventos.publish(ReservaConfirmada(reserva.id, reserva.acomodacao_id))
        return reserva

    def cancelar(self, reserva_id: int, motivo: str | None):
        reserva = self.obter(reserva_id)
        estado = estado_de(reserva)
        estado.exigir("cancelar")
        estado.cancelar(reserva, motivo, self.relogio.agora())
        self.reservas.salvar(reserva)             # libera o período na restrição do banco
        self.eventos.publish(ReservaCancelada(reserva.id, reserva.acomodacao_id))
        return reserva

    # ---- apoio
    def _acomodacao_reservavel(self, acomodacao_id: int, qtd_hospedes: int, entrada):
        acomodacao = self.acomodacoes.get(acomodacao_id)
        if acomodacao is None:
            raise NaoEncontradoError("Acomodação não encontrada")
        if not acomodacao.ativo:
            raise RegraDeNegocioError("A acomodação está inativa")
        if qtd_hospedes > acomodacao.capacidade:
            raise RegraDeNegocioError(f"A acomodação comporta no máximo {acomodacao.capacidade} hóspede(s)")
        if entrada < self.relogio.hoje():
            raise RegraDeNegocioError("A data de entrada não pode estar no passado")
        return acomodacao
