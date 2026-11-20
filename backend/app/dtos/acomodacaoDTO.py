from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.dtos.comumDTO import Saida, texto_ou_none


class CategoriaIn(BaseModel):
    nome: str = Field(min_length=2, max_length=60)
    descricao: str | None = Field(default=None, max_length=255)

    _limpar = field_validator("nome", "descricao", mode="before")(texto_ou_none)


class CategoriaOut(Saida):
    id: int
    nome: str
    descricao: str | None


class CaracteristicaIn(BaseModel):
    nome: str = Field(min_length=2, max_length=60)

    _limpar = field_validator("nome", mode="before")(texto_ou_none)


class CaracteristicaOut(Saida):
    id: int
    nome: str


class AcomodacaoIn(BaseModel):
    numero: str = Field(min_length=1, max_length=10)
    categoria_id: int
    capacidade: int = Field(gt=0, le=20)
    valor_diaria: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    caracteristica_ids: list[int] = Field(default_factory=list)

    _limpar = field_validator("numero", mode="before")(texto_ou_none)


class AtivoIn(BaseModel):
    ativo: bool


class AcomodacaoOut(Saida):
    id: int
    numero: str
    categoria: CategoriaOut
    capacidade: int
    valor_diaria: Decimal
    status: Literal["LIVRE", "RESERVADO", "OCUPADO"]
    ativo: bool
    caracteristicas: list[CaracteristicaOut]


class AcomodacaoResumo(Saida):
    id: int
    numero: str
    capacidade: int


class DisponivelOut(BaseModel):
    acomodacao: AcomodacaoOut
    noites: int
    valor_total: Decimal


class ReservaMapaOut(BaseModel):
    id: int
    hospede_nome: str
    data_entrada: date
    data_saida: date
    status: str


class MapaLinhaOut(BaseModel):
    acomodacao: AcomodacaoResumo
    reservas: list[ReservaMapaOut]
