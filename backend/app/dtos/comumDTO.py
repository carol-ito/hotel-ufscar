from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class Saida(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Pagina(BaseModel, Generic[T]):
    itens: list[T]
    total: int
    limite: int
    offset: int


def texto_ou_none(v):
    """Campos opcionais de formulário chegam como "" — viram None."""
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v
