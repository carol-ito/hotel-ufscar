from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import (GESTAO, RECEPCAO, get_acomodacao_service, get_disponibilidade_service,
                                   require_role)
from app.dtos.acomodacaoDTO import AcomodacaoIn, AcomodacaoOut, AtivoIn, DisponivelOut

router = APIRouter(prefix="/acomodacoes", tags=["Acomodações"])
equipe, gestao = require_role(GESTAO, RECEPCAO), require_role(GESTAO)


@router.get("", response_model=list[AcomodacaoOut])
def listar(ativo: bool | None = None, categoria_id: int | None = None,
           status: Literal["LIVRE", "RESERVADO", "OCUPADO"] | None = None,
           _=Depends(equipe), service=Depends(get_acomodacao_service)):
    return service.listar(ativo, categoria_id, status)


# declarada antes de /{acomodacao_id}, senão "disponiveis" seria lido como id
@router.get("/disponiveis", response_model=list[DisponivelOut])
def disponiveis(entrada: date, saida: date, hospedes: int = Query(1, ge=1, le=20),
                categoria_id: int | None = None, _=Depends(equipe),
                service=Depends(get_disponibilidade_service)):
    return [DisponivelOut(acomodacao=d.acomodacao, noites=d.noites, valor_total=d.valor_total)
            for d in service.consultar(entrada, saida, hospedes, categoria_id)]


@router.get("/{acomodacao_id}", response_model=AcomodacaoOut)
def obter(acomodacao_id: int, _=Depends(equipe), service=Depends(get_acomodacao_service)):
    return service.obter(acomodacao_id)


@router.post("", response_model=AcomodacaoOut, status_code=201)
def criar(dados: AcomodacaoIn, _=Depends(gestao), service=Depends(get_acomodacao_service)):
    return service.criar(dados)


@router.put("/{acomodacao_id}", response_model=AcomodacaoOut)
def atualizar(acomodacao_id: int, dados: AcomodacaoIn, _=Depends(gestao),
              service=Depends(get_acomodacao_service)):
    return service.atualizar(acomodacao_id, dados)


@router.patch("/{acomodacao_id}/ativo", response_model=AcomodacaoOut)
def definir_ativo(acomodacao_id: int, dados: AtivoIn, _=Depends(gestao),
                  service=Depends(get_acomodacao_service)):
    return service.definir_ativo(acomodacao_id, dados.ativo)
