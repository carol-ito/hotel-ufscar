from sqlalchemy import func, select

from app.models import Usuario
from app.repositories.baseRepository import SqlRepository


class UsuarioRepository(SqlRepository[Usuario]):
    model = Usuario

    def get_por_email(self, email: str) -> Usuario | None:
        return self.session.scalar(select(Usuario).where(func.lower(Usuario.email) == email.strip().lower()))
