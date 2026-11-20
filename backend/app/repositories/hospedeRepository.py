from sqlalchemy import func, or_, select

from app.models import Hospede
from app.repositories.baseRepository import SqlRepository


def _escapar_like(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class HospedeRepository(SqlRepository[Hospede]):
    model = Hospede

    def get_por_documento(self, tipo: str, numero: str) -> Hospede | None:
        return self.session.scalar(select(Hospede).where(
            Hospede.documento_tipo == tipo, Hospede.documento_numero == numero))

    def buscar(self, q: str | None, limite: int, offset: int) -> tuple[list[Hospede], int]:
        filtro = []
        if q and q.strip():
            termo = _escapar_like(q.strip().lower())
            digitos = "".join(c for c in q if c.isdigit())
            condicoes = [func.lower(Hospede.nome).like(f"%{termo}%", escape="\\")]
            if digitos:
                condicoes.append(Hospede.documento_numero.like(f"%{digitos}%"))
            else:
                condicoes.append(func.lower(Hospede.documento_numero).like(f"%{termo}%", escape="\\"))
            filtro.append(or_(*condicoes))
        total = self.session.scalar(select(func.count()).select_from(Hospede).where(*filtro)) or 0
        itens = self.session.scalars(
            select(Hospede).where(*filtro).order_by(func.lower(Hospede.nome), Hospede.id)
            .limit(limite).offset(offset)).all()
        return list(itens), total
