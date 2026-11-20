from datetime import date

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import GESTAO, RECEPCAO, get_disponibilidade_service, require_role
from app.dtos.acomodacaoDTO import DisponivelOut, MapaLinhaOut, ReservaMapaOut

router = APIRouter(prefix="/disponibilidade", tags=["Disponibilidade"])
equipe = require_role(GESTAO, RECEPCAO)


@router.get("", response_model=list[DisponivelOut])
def consultar(entrada: date, saida: date, hospedes: int = Query(1, ge=1, le=20),
              categoria_id: int | None = None, _=Depends(equipe),
              service=Depends(get_disponibilidade_service)):
    """Acomodações livres no período [entrada, saída). Mesmo resultado de GET /acomodacoes/disponiveis."""
    return [DisponivelOut(acomodacao=d.acomodacao, noites=d.noites, valor_total=d.valor_total)
            for d in service.consultar(entrada, saida, hospedes, categoria_id)]


@router.get("/mapa", response_model=list[MapaLinhaOut])
def mapa(ini: date, fim: date, _=Depends(equipe), service=Depends(get_disponibilidade_service)):
    """Mapa de ocupação: reservas vivas por acomodação no período (fim exclusivo, até 62 dias)."""
    return [MapaLinhaOut(
        acomodacao=a,
        reservas=[ReservaMapaOut(id=r.id, hospede_nome=r.hospede.nome, data_entrada=r.data_entrada,
                                 data_saida=r.data_saida, status=r.status) for r in reservas])
        for a, reservas in service.mapa(ini, fim)]
