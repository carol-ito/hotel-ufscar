from fastapi import APIRouter, Depends

from app.core.dependencies import GESTAO, RECEPCAO, get_catalogo_service, require_role
from app.dtos.acomodacaoDTO import CaracteristicaIn, CaracteristicaOut, CategoriaIn, CategoriaOut

router = APIRouter(tags=["Acomodações"])
equipe, gestao = require_role(GESTAO, RECEPCAO), require_role(GESTAO)


@router.get("/categorias", response_model=list[CategoriaOut])
def listar_categorias(_=Depends(equipe), service=Depends(get_catalogo_service)):
    return service.listar_categorias()


@router.post("/categorias", response_model=CategoriaOut, status_code=201)
def criar_categoria(dados: CategoriaIn, _=Depends(gestao), service=Depends(get_catalogo_service)):
    return service.criar_categoria(dados)


@router.put("/categorias/{categoria_id}", response_model=CategoriaOut)
def atualizar_categoria(categoria_id: int, dados: CategoriaIn, _=Depends(gestao),
                        service=Depends(get_catalogo_service)):
    return service.atualizar_categoria(categoria_id, dados)


@router.get("/caracteristicas", response_model=list[CaracteristicaOut])
def listar_caracteristicas(_=Depends(equipe), service=Depends(get_catalogo_service)):
    return service.listar_caracteristicas()


@router.post("/caracteristicas", response_model=CaracteristicaOut, status_code=201)
def criar_caracteristica(dados: CaracteristicaIn, _=Depends(gestao), service=Depends(get_catalogo_service)):
    return service.criar_caracteristica(dados)


@router.put("/caracteristicas/{caracteristica_id}", response_model=CaracteristicaOut)
def atualizar_caracteristica(caracteristica_id: int, dados: CaracteristicaIn, _=Depends(gestao),
                             service=Depends(get_catalogo_service)):
    return service.atualizar_caracteristica(caracteristica_id, dados)
