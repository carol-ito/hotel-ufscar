from types import SimpleNamespace

import pytest

from app.core.errors import NaoEncontradoError
from app.services.acomodacaoService import CatalogoService


class FakeCatalogoRepository:
    def __init__(self, *itens):
        self.itens = {i.id: i for i in itens}
        self._seq = max(self.itens, default=0)

    def listar(self):
        return list(self.itens.values())

    def get(self, id_):
        return self.itens.get(id_)

    def add(self, item):
        self._seq += 1
        item.id = self._seq
        self.itens[item.id] = item
        return item

    def salvar(self, item):
        return item


class CatalogoServiceTest:
    def _service(self):
        cat = FakeCatalogoRepository(SimpleNamespace(id=1, nome="Standard", descricao=None))
        car = FakeCatalogoRepository(SimpleNamespace(id=1, nome="Wi-Fi"))
        return CatalogoService(cat, car), cat, car

    def test_criar_categoria_e_caracteristica(self):
        s, cat, car = self._service()
        c = s.criar_categoria(SimpleNamespace(nome="Luxo", descricao="Vista"))
        k = s.criar_caracteristica(SimpleNamespace(nome="Frigobar"))
        assert (c.id, c.nome, c.descricao) == (2, "Luxo", "Vista") and (k.id, k.nome) == (2, "Frigobar")
        assert len(s.listar_categorias()) == 2 and len(s.listar_caracteristicas()) == 2

    def test_atualizar_categoria_e_caracteristica(self):
        s, *_ = self._service()
        assert s.atualizar_categoria(1, SimpleNamespace(nome="Suíte", descricao="Sala")).nome == "Suíte"
        assert s.atualizar_caracteristica(1, SimpleNamespace(nome="Wi-Fi 6")).nome == "Wi-Fi 6"

    def test_atualizar_inexistente_404(self):
        s, *_ = self._service()
        with pytest.raises(NaoEncontradoError, match="Categoria"):
            s.atualizar_categoria(99, SimpleNamespace(nome="X", descricao=None))
        with pytest.raises(NaoEncontradoError, match="Característica"):
            s.atualizar_caracteristica(99, SimpleNamespace(nome="X"))
