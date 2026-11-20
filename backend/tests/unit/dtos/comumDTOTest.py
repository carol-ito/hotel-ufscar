from types import SimpleNamespace

import pytest

from app.dtos.comumDTO import Pagina, Saida, texto_ou_none


class ComumDTOTest:
    @pytest.mark.parametrize("entrada,esperado", [("  x ", "x"), ("", None), ("   ", None), (None, None), (5, 5)])
    def test_texto_ou_none(self, entrada, esperado):
        assert texto_ou_none(entrada) == esperado

    def test_pagina_guarda_itens_e_totais(self):
        p = Pagina[int](itens=[1, 2], total=10, limite=2, offset=0)
        assert p.itens == [1, 2] and p.total == 10

    def test_saida_le_atributos_de_objetos(self):
        class Dto(Saida):
            a: int
        assert Dto.model_validate(SimpleNamespace(a=3)).a == 3
