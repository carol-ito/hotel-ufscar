from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Computed, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.acomodacaoModel import Acomodacao
from app.models.baseModel import Base
from app.models.hospedeModel import Hospede

STATUS_VIVOS = ("PENDENTE", "CONFIRMADA", "EM_ANDAMENTO")


class Reserva(Base):
    __tablename__ = "reserva"

    id: Mapped[int] = mapped_column(primary_key=True)
    hospede_id: Mapped[int] = mapped_column(ForeignKey("hospede.id"))
    acomodacao_id: Mapped[int] = mapped_column(ForeignKey("acomodacao.id"))
    data_entrada: Mapped[date]
    data_saida: Mapped[date]
    noites: Mapped[int] = mapped_column(Computed("data_saida - data_entrada", persisted=True))
    qtd_hospedes: Mapped[int]
    status: Mapped[str] = mapped_column(default="PENDENTE")
    valor_diaria: Mapped[Decimal]
    valor_total: Mapped[Decimal]
    motivo_cancelamento: Mapped[str | None]
    criada_por: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    criada_em: Mapped[datetime] = mapped_column(server_default=func.now())
    atualizada_em: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    confirmada_em: Mapped[datetime | None]
    cancelada_em: Mapped[datetime | None]
    checkin_em: Mapped[datetime | None]
    checkout_em: Mapped[datetime | None]

    hospede: Mapped[Hospede] = relationship(lazy="joined")
    acomodacao: Mapped[Acomodacao] = relationship(lazy="joined")

    @property
    def viva(self) -> bool:
        return self.status in STATUS_VIVOS
