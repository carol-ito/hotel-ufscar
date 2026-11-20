from datetime import date

from sqlalchemy import func, select

from app.models import Acomodacao, Hospede, Reserva
from app.models.reservaModel import STATUS_VIVOS
from app.repositories.acomodacaoRepository import periodo, sobrepoe
from app.repositories.baseRepository import SqlRepository


class ReservaRepository(SqlRepository[Reserva]):
    model = Reserva

    def existe_conflito(self, acomodacao_id: int, entrada: date, saida: date,
                        ignorar_id: int | None = None) -> bool:
        """Pré-checagem para dar mensagem rápida; quem decide de verdade é a restrição do banco."""
        consulta = select(Reserva.id).where(
            Reserva.acomodacao_id == acomodacao_id,
            Reserva.status.in_(STATUS_VIVOS),
            sobrepoe(periodo(Reserva.data_entrada, Reserva.data_saida), periodo(entrada, saida)))
        if ignorar_id is not None:
            consulta = consulta.where(Reserva.id != ignorar_id)
        return self.session.scalar(consulta.limit(1)) is not None

    def vivas_da_acomodacao(self, acomodacao_id: int) -> list[Reserva]:
        return list(self.session.scalars(select(Reserva).where(
            Reserva.acomodacao_id == acomodacao_id, Reserva.status.in_(STATUS_VIVOS))))

    def vivas_a_partir_de(self, acomodacao_id: int, hoje: date) -> list[Reserva]:
        """Vivas que ainda não terminaram (impedem inativar a acomodação)."""
        return list(self.session.scalars(select(Reserva).where(
            Reserva.acomodacao_id == acomodacao_id, Reserva.status.in_(STATUS_VIVOS),
            Reserva.data_saida > hoje)))

    def listar(self, *, status: str | None, hospede_id: int | None, acomodacao_id: int | None,
               entrada_de: date | None, entrada_ate: date | None,
               limite: int, offset: int) -> tuple[list[Reserva], int]:
        filtros = []
        if status:
            filtros.append(Reserva.status == status)
        if hospede_id is not None:
            filtros.append(Reserva.hospede_id == hospede_id)
        if acomodacao_id is not None:
            filtros.append(Reserva.acomodacao_id == acomodacao_id)
        if entrada_de:
            filtros.append(Reserva.data_entrada >= entrada_de)
        if entrada_ate:
            filtros.append(Reserva.data_entrada <= entrada_ate)
        total = self.session.scalar(select(func.count()).select_from(Reserva).where(*filtros)) or 0
        itens = self.session.scalars(
            select(Reserva).where(*filtros)
            .order_by(Reserva.data_entrada.desc(), Reserva.id.desc()).limit(limite).offset(offset)).all()
        return list(itens), total

    def no_periodo(self, ini: date, fim: date) -> list[Reserva]:
        """Reservas vivas que tocam o período [ini, fim): alimenta o mapa de ocupação."""
        return list(self.session.scalars(
            select(Reserva).where(
                Reserva.status.in_(STATUS_VIVOS),
                sobrepoe(periodo(Reserva.data_entrada, Reserva.data_saida), periodo(ini, fim)))
            .order_by(Reserva.acomodacao_id, Reserva.data_entrada)))
