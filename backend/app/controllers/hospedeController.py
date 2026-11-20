from fastapi import APIRouter, Depends, Query

from app.core.dependencies import GESTAO, RECEPCAO, get_hospede_service, require_role
from app.dtos.comumDTO import Pagina
from app.dtos.hospedeDTO import HospedeIn, HospedeOut

router = APIRouter(prefix="/hospedes", tags=["Hóspedes"])
equipe = require_role(GESTAO, RECEPCAO)


@router.get("", response_model=Pagina[HospedeOut])
def listar(q: str | None = Query(None, max_length=120, description="nome ou documento"),
           limite: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
           _=Depends(equipe), service=Depends(get_hospede_service)):
    itens, total = service.listar(q, limite, offset)
    return Pagina[HospedeOut](itens=itens, total=total, limite=limite, offset=offset)


@router.post("", response_model=HospedeOut, status_code=201)
def criar(dados: HospedeIn, _=Depends(equipe), service=Depends(get_hospede_service)):
    return service.criar(dados)


@router.get("/{hospede_id}", response_model=HospedeOut)
def obter(hospede_id: int, _=Depends(equipe), service=Depends(get_hospede_service)):
    return service.obter(hospede_id)


@router.put("/{hospede_id}", response_model=HospedeOut)
def atualizar(hospede_id: int, dados: HospedeIn, _=Depends(equipe), service=Depends(get_hospede_service)):
    return service.atualizar(hospede_id, dados)
