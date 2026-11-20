from app.activities.baseActivity import BaseActivity

SENHA_PADRAO = "senha123"


class AuthActivity(BaseActivity):
    def login(self, email: str, senha: str = SENHA_PADRAO):
        return self.client.post("/auth/login", json={"email": email, "senha": senha})

    def me(self):
        return self._get("/auth/me")

    def cabecalho_de(self, email: str, senha: str = SENHA_PADRAO) -> dict:
        """Faz o login e devolve o cabeçalho Authorization pronto para as outras Activities."""
        r = self.login(email, senha)
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}
