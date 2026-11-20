from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.baseModel import Base


class Hospede(Base):
    __tablename__ = "hospede"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    documento_tipo: Mapped[str]
    documento_numero: Mapped[str]
    email: Mapped[str | None]
    telefone: Mapped[str | None]
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
