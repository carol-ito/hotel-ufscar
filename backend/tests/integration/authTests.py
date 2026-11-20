from pathlib import Path

from sqlalchemy import text

from app.activities.hospedeActivity import HospedeActivity


class AuthTests:
    def test_login_ok_devolve_token_e_perfil(self, auth_api):
        r = auth_api.login("GESTAO@hotel.test")        # e-mail sem diferenciar maiúsculas
        assert r.status_code == 200
        corpo = r.json()
        assert corpo["usuario"]["perfil"] == "GESTAO" and corpo["expires_in"] > 0
        assert "senha_hash" not in str(corpo)

    def test_login_invalido_tem_sempre_a_mesma_mensagem(self, auth_api):
        a = auth_api.login("gestao@hotel.test", "errada")
        b = auth_api.login("ninguem@hotel.test")
        assert a.status_code == b.status_code == 401
        assert a.json() == b.json() == {"erro": "E-mail ou senha inválidos"}

    def test_rota_protegida_sem_token_401(self, client):
        r = HospedeActivity(client).listar()
        assert r.status_code == 401 and "erro" in r.json()

    def test_token_invalido_401(self, client):
        assert HospedeActivity(client, {"Authorization": "Bearer lixo"}).listar().status_code == 401

    def test_me(self, auth_api, recepcao):
        assert auth_api.como(recepcao).me().json()["perfil"] == "RECEPCAO"

    def test_usuario_inativo_nao_entra(self, auth_api, banco):
        with banco.begin() as conn:
            conn.execute(text("UPDATE usuario SET ativo = false WHERE perfil = 'GESTAO'"))
        assert auth_api.login("gestao@hotel.test").status_code == 401

    def test_admin_do_script_sql_entra_como_gestao_e_o_script_e_idempotente(self, auth_api, banco):
        sql = (Path(__file__).resolve().parents[3] / "db" / "admin.sql").read_text()
        for _ in range(2):                       # rodar duas vezes não pode duplicar nem falhar
            with banco.begin() as conn:
                conn.execute(text(sql))
        r = auth_api.login("CarolIneito18@gmail.com", "18062002")
        assert r.status_code == 200
        assert r.json()["usuario"]["perfil"] == "GESTAO" and r.json()["usuario"]["nome"] == "carol-ito"
        with banco.connect() as conn:
            assert conn.scalar(text("SELECT count(*) FROM usuario WHERE lower(email) = 'carolineito18@gmail.com'")) == 1
        assert auth_api.login("carolineito18@gmail.com", "errada").status_code == 401
