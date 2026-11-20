from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.baseModel import Base

acomodacao_caracteristica = Table(
    "acomodacao_caracteristica", Base.metadata,
    Column("acomodacao_id", ForeignKey("acomodacao.id", ondelete="CASCADE"), primary_key=True),
    Column("caracteristica_id", ForeignKey("caracteristica.id"), primary_key=True),
)


class Categoria(Base):
    __tablename__ = "categoria_acomodacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    descricao: Mapped[str | None]


class Caracteristica(Base):
    __tablename__ = "caracteristica"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]


class Acomodacao(Base):
    __tablename__ = "acomodacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str]
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categoria_acomodacao.id"))
    capacidade: Mapped[int]
    valor_diaria: Mapped[Decimal]
    status: Mapped[str] = mapped_column(default="LIVRE")
    ativo: Mapped[bool] = mapped_column(default=True)
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    categoria: Mapped[Categoria] = relationship(lazy="joined")
    caracteristicas: Mapped[list[Caracteristica]] = relationship(
        secondary=acomodacao_caracteristica, lazy="selectin", order_by=Caracteristica.nome)
