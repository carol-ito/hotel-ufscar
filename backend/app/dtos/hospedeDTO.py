from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.dtos.comumDTO import Saida, texto_ou_none

TipoDocumento = Literal["CPF", "RG", "PASSAPORTE", "OUTRO"]


class HospedeIn(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    documento_tipo: TipoDocumento
    documento_numero: str = Field(min_length=1, max_length=30)
    email: EmailStr | None = Field(default=None, max_length=160)
    telefone: str | None = Field(default=None, max_length=20)

    _limpar = field_validator("nome", "documento_numero", "email", "telefone", mode="before")(texto_ou_none)

    @model_validator(mode="after")
    def contato_obrigatorio(self):
        if not self.email and not self.telefone:
            raise ValueError("Informe ao menos um contato: e-mail ou telefone")
        return self


class HospedeOut(Saida):
    id: int
    nome: str
    documento_tipo: str
    documento_numero: str
    email: str | None
    telefone: str | None
    criado_em: datetime


class HospedeResumo(Saida):
    id: int
    nome: str
    documento_tipo: str
    documento_numero: str
