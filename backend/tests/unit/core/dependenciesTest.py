from types import SimpleNamespace

import pytest

from app.core.dependencies import GESTAO, RECEPCAO, get_relogio, require_role
from app.core.errors import AcessoNegadoError
from app.core.relogio import Relogio


class DependenciesTest:
    def test_require_role_deixa_passar_o_perfil_permitido(self):
        usuario = SimpleNamespace(perfil=GESTAO)
        assert require_role(GESTAO)(usuario) is usuario
        assert require_role(GESTAO, RECEPCAO)(SimpleNamespace(perfil=RECEPCAO))

    def test_require_role_barra_perfil_nao_permitido_com_403(self):
        with pytest.raises(AcessoNegadoError) as e:
            require_role(GESTAO)(SimpleNamespace(perfil=RECEPCAO))
        assert e.value.status_code == 403

    def test_get_relogio_devolve_o_relogio_real(self):
        assert isinstance(get_relogio(), Relogio)
