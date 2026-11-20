from types import SimpleNamespace

import pytest

from app.core.errors import NaoAutenticadoError
from app.core.security import gerar_hash, ler_token
from app.services.authService import AuthService
from tests.unit.fakes import FakeUsuarioRepository


class AuthServiceTest:
    @pytest.fixture(scope="class")
    def usuario(self):
        return SimpleNamespace(id=3, perfil="GESTAO", ativo=True, senha_hash=gerar_hash("segredo"))   # bcrypt é lento: 1x

    def test_login_valido_emite_token_com_id_e_perfil(self, usuario):
        token, expira_em, quem = AuthService(FakeUsuarioRepository(usuario)).login("a@b.c", "segredo")
        dados = ler_token(token)
        assert dados["sub"] == "3" and dados["perfil"] == "GESTAO" and expira_em > 0 and quem is usuario

    def test_senha_errada_email_inexistente_e_inativo_tem_a_mesma_resposta(self, usuario):
        inativo = SimpleNamespace(**{**usuario.__dict__, "ativo": False})
        mensagens = set()
        for quem, senha in [(usuario, "errada"), (None, "segredo"), (inativo, "segredo")]:
            with pytest.raises(NaoAutenticadoError) as e:
                AuthService(FakeUsuarioRepository(quem)).login("a@b.c", senha)
            mensagens.add(e.value.mensagem)
        assert mensagens == {"E-mail ou senha inválidos"}
