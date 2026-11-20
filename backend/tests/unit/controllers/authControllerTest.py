from types import SimpleNamespace
from unittest.mock import Mock

from app.controllers import authController
from app.dtos.authDTO import LoginIn


class AuthControllerTest:
    def test_login_devolve_token_validade_e_usuario(self):
        usuario = SimpleNamespace(id=1, nome="Gestora", email="g@h.local", perfil="GESTAO")
        service = Mock(login=Mock(return_value=("tok", 3600, usuario)))
        saida = authController.login(LoginIn(email="g@h.local", senha="x"), service)
        service.login.assert_called_once_with("g@h.local", "x")
        assert (saida.access_token, saida.token_type, saida.expires_in) == ("tok", "bearer", 3600)
        assert saida.usuario.perfil == "GESTAO" and not hasattr(saida.usuario, "senha_hash")

    def test_me_devolve_o_usuario_da_sessao(self):
        usuario = object()
        assert authController.me(usuario) is usuario
