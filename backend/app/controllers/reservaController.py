from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import GESTAO, RECEPCAO, get_reserva_service, require_role
from app.domain.reservaState import estado_de
from app.dtos.comumDTO import Pagina
from app.dtos.reservaDTO import AlterarReservaIn, CancelarIn, NovaReservaIn, ReservaOut

router = APIRouter(prefix="/reservas", tags=["Reservas"])
equipe = require_role(GESTAO, RECEPCAO)
ACOES_NESTE_MODULO = ("alterar", "confirmar", "cancelar")


def _saida(reserva) -> ReservaOut:
    saida = ReservaOut.model_validate(reserva)
    permitidas = estado_de(reserva).permite
    saida.acoes_permitidas = [a for a in ACOES_NESTE_MODULO if a in permitidas]
    return saida


@router.post("", response_model=ReservaOut, status_code=201)
def criar(dados: NovaReservaIn, usuario=Depends(equipe), service=Depends(get_reserva_service)):
    return _saida(service.criar(dados, usuario.id))


@router.get("", response_model=Pagina[ReservaOut])
def listar(status: Literal["PENDENTE", "CONFIRMADA", "EM_ANDAMENTO", "ENCERRADA", "CANCELADA"] | None = None,
           hospede_id: int | None = None, acomodacao_id: int | None = None,
           entrada_de: date | None = None, entrada_ate: date | None = None,
           limite: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
           _=Depends(equipe), service=Depends(get_reserva_service)):
    itens, total = service.listar(status=status, hospede_id=hospede_id, acomodacao_id=acomodacao_id,
                                  entrada_de=entrada_de, entrada_ate=entrada_ate,
                                  limite=limite, offset=offset)
    return Pagina[ReservaOut](itens=[_saida(r) for r in itens], total=total, limite=limite, offset=offset)


@router.get("/{reserva_id}", response_model=ReservaOut)
def obter(reserva_id: int, _=Depends(equipe), service=Depends(get_reserva_service)):
    return _saida(service.obter(reserva_id))


@router.put("/{reserva_id}", response_model=ReservaOut)
def alterar(reserva_id: int, dados: AlterarReservaIn, _=Depends(equipe), service=Depends(get_reserva_service)):
    return _saida(service.alterar(reserva_id, dados))


@router.post("/{reserva_id}/confirmar", response_model=ReservaOut)
def confirmar(reserva_id: int, _=Depends(equipe), service=Depends(get_reserva_service)):
    return _saida(service.confirmar(reserva_id))


@router.post("/{reserva_id}/cancelar", response_model=ReservaOut)
def cancelar(reserva_id: int, dados: CancelarIn | None = None, _=Depends(equipe),
             service=Depends(get_reserva_service)):
    return _saida(service.cancelar(reserva_id, dados.motivo if dados else None))
