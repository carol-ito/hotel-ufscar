from unittest.mock import Mock

import pytest

from app.controllers import catalogoController as c
from app.dtos.acomodacaoDTO import CaracteristicaIn, CategoriaIn


class CatalogoControllerTest:
    @pytest.mark.parametrize("funcao,metodo", [(c.listar_categorias, "listar_categorias"),
                                               (c.listar_caracteristicas, "listar_caracteristicas")])
    def test_listagens_delegam(self, funcao, metodo):
        service = Mock(**{metodo: Mock(return_value=["x"])})
        assert funcao(_=None, service=service) == ["x"]

    def test_categoria_criar_e_atualizar(self):
        dados, service = CategoriaIn(nome="Luxo"), Mock()
        c.criar_categoria(dados, _=None, service=service)
        c.atualizar_categoria(3, dados, _=None, service=service)
        service.criar_categoria.assert_called_once_with(dados)
        service.atualizar_categoria.assert_called_once_with(3, dados)

    def test_caracteristica_criar_e_atualizar(self):
        dados, service = CaracteristicaIn(nome="Varanda"), Mock()
        c.criar_caracteristica(dados, _=None, service=service)
        c.atualizar_caracteristica(4, dados, _=None, service=service)
        service.criar_caracteristica.assert_called_once_with(dados)
        service.atualizar_caracteristica.assert_called_once_with(4, dados)
