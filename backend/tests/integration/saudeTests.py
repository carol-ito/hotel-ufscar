class SaudeTests:
    def test_api_e_banco_no_ar(self, saude_api):
        assert saude_api.api().json() == {"status": "ok"}
        assert saude_api.banco().json()["banco"] == "conectado"

    def test_erro_de_rota_segue_o_formato_unico(self, saude_api):
        r = saude_api.rota_inexistente()
        assert r.status_code == 404 and r.json() == {"erro": "Not Found"}
