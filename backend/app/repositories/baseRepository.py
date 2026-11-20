"""Repository genérico. Traduz erros do PostgreSQL em erros de domínio, para que
services e controllers nunca vejam SQL."""
from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflitoReservaError, DuplicidadeError, RegraDeNegocioError

T = TypeVar("T")

_MENSAGENS_UNICO = {
    "ux_hospede_documento": "Já existe um hóspede com este documento",
    "acomodacao_numero_key": "Já existe uma acomodação com este número",
    "categoria_acomodacao_nome_key": "Já existe uma categoria com este nome",
    "caracteristica_nome_key": "Já existe uma característica com este nome",
}


def traduzir_erro_banco(erro: IntegrityError) -> Exception:
    sqlstate = getattr(erro.orig, "sqlstate", None)
    constraint = getattr(getattr(erro.orig, "diag", None), "constraint_name", None)
    if sqlstate == "23P01":     # exclusion_violation: o anti-overbooking decidiu
        return ConflitoReservaError()
    if sqlstate == "23505":     # unique_violation
        return DuplicidadeError(_MENSAGENS_UNICO.get(constraint or "", "Já existe um registro com esses dados"))
    if sqlstate in ("23503", "23514"):   # foreign_key_violation, check_violation
        return RegraDeNegocioError("Os dados violam uma regra de integridade do banco")
    return erro


class SqlRepository(Generic[T]):
    model: type[T]

    def __init__(self, session: Session):
        self.session = session

    def get(self, id_: int) -> T | None:
        return self.session.get(self.model, id_)

    def add(self, entidade: T) -> T:
        self.session.add(entidade)
        return self.salvar(entidade)

    def salvar(self, entidade: T) -> T:
        """flush: envia ao banco agora, para que as restrições disparem dentro do caso de uso."""
        try:
            self.session.flush()
        except IntegrityError as erro:
            traduzido = traduzir_erro_banco(erro)
            if traduzido is erro:
                raise
            raise traduzido from erro
        self.session.refresh(entidade)
        return entidade
