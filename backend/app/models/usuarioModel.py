from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.baseModel import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    email: Mapped[str]
    senha_hash: Mapped[str]
    perfil: Mapped[str]
    ativo: Mapped[bool] = mapped_column(default=True)
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())
