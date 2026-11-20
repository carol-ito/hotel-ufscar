from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.dtos.acomodacaoDTO import AcomodacaoResumo
from app.dtos.comumDTO import Saida, texto_ou_none
from app.dtos.hospedeDTO import HospedeResumo


class _Periodo(BaseModel):
    data_entrada: date
    data_saida: date

    @model_validator(mode="after")
    def saida_depois_da_entrada(self):
        if self.data_saida <= self.data_entrada:
            raise ValueError("A data de saída deve ser posterior à data de entrada")
        return self


class NovaReservaIn(_Periodo):
    hospede_id: int
    acomodacao_id: int
    qtd_hospedes: int = Field(gt=0, le=20)


class AlterarReservaIn(_Periodo):
    qtd_hospedes: int = Field(gt=0, le=20)


class CancelarIn(BaseModel):
    motivo: str | None = Field(default=None, max_length=255)

    _limpar = field_validator("motivo", mode="before")(texto_ou_none)


class ReservaOut(Saida):
    id: int
    hospede: HospedeResumo
    acomodacao: AcomodacaoResumo
    data_entrada: date
    data_saida: date
    noites: int
    qtd_hospedes: int
    status: str
    valor_diaria: Decimal
    valor_total: Decimal
    motivo_cancelamento: str | None
    criada_em: datetime
    confirmada_em: datetime | None
    cancelada_em: datetime | None
    checkin_em: datetime | None
    checkout_em: datetime | None
    acoes_permitidas: list[str] = []
