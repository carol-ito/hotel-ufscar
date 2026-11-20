from datetime import datetime, timedelta, timezone

import pytest

from app.core.errors import NaoAutenticadoError
from app.core.security import emitir_token, gerar_hash, ler_token, verificar_senha


class SecurityTest:
    def test_hash_nao_guarda_a_senha_e_confere(self):
        h = gerar_hash("18062002")
        assert "18062002" not in h and h.startswith("$2") and verificar_senha("18062002", h)
        assert not verificar_senha("outra", h)

    def test_hash_invalido_nao_estoura(self):
        assert not verificar_senha("x", "hash-invalido")

    def test_senha_vazia_ou_curta_tambem_funciona(self):
        assert verificar_senha("1", gerar_hash("1"))      # o sistema não impõe tamanho mínimo

    def test_token_ida_e_volta(self):
        token, segundos = emitir_token(7, "RECEPCAO")
        dados = ler_token(token)
        assert dados["sub"] == "7" and dados["perfil"] == "RECEPCAO" and segundos > 0

    def test_token_expirado(self):
        token, _ = emitir_token(1, "GESTAO", agora=datetime.now(timezone.utc) - timedelta(days=1))
        with pytest.raises(NaoAutenticadoError, match="expirada"):
            ler_token(token)

    def test_token_adulterado(self):
        token, _ = emitir_token(1, "GESTAO")
        with pytest.raises(NaoAutenticadoError):
            ler_token(token[:-3] + "abc")
