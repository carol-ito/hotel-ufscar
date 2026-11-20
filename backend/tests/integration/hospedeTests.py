from app.activities.hospedeActivity import dados_hospede


class HospedeTests:
    def test_cria_normaliza_cpf_e_busca(self, hospede_api):
        r = hospede_api.criar()
        assert r.status_code == 201
        assert r.json()["documento_numero"] == "52998224725"
        achou_nome = hospede_api.listar(q="joão").json()
        achou_doc = hospede_api.listar(q="529.982").json()
        assert achou_nome["total"] == achou_doc["total"] == 1

    def test_documento_duplicado_409(self, hospede_api):
        assert hospede_api.criar().status_code == 201
        r = hospede_api.criar(dados_hospede(nome="Outro Nome", documento_numero="52998224725"))
        assert r.status_code == 409 and "documento" in r.json()["erro"]

    def test_cpf_invalido_422(self, hospede_api):
        r = hospede_api.criar(dados_hospede(documento_numero="111.111.111-11"))
        assert r.status_code == 422 and r.json()["erro"] == "CPF inválido"

    def test_exige_ao_menos_um_contato(self, hospede_api):
        r = hospede_api.criar({"nome": "Sem Contato", "documento_tipo": "RG", "documento_numero": "12345"})
        assert r.status_code == 422 and "contato" in r.json()["erro"]

    def test_email_invalido_422_com_campo(self, hospede_api):
        r = hospede_api.criar(dados_hospede(email="nao-e-email"))
        assert r.status_code == 422 and "email" in r.json()["campos"]

    def test_atualizar_e_obter(self, hospede_api):
        id_ = hospede_api.criar().json()["id"]
        r = hospede_api.atualizar(id_, dados_hospede(nome="João S. Silva"))
        assert r.status_code == 200 and r.json()["nome"] == "João S. Silva"
        assert hospede_api.obter(id_).json()["nome"] == "João S. Silva"

    def test_atualizar_para_documento_de_outro_409(self, hospede_api):
        hospede_api.criar()
        outro = hospede_api.criar(dados_hospede(nome="Pedro", documento_tipo="RG", documento_numero="MG123", email="p@x.com")).json()
        assert hospede_api.atualizar(outro["id"], dados_hospede(nome="Pedro")).status_code == 409

    def test_inexistente_404(self, hospede_api):
        assert hospede_api.obter(999).status_code == 404

    def test_paginacao(self, hospede_api):
        for i in range(5):
            hospede_api.criar({"nome": f"Hospede {i}", "documento_tipo": "OUTRO", "documento_numero": f"D{i}", "email": f"{i}@x.com"})
        p = hospede_api.listar(limite=2, offset=2).json()
        assert p["total"] == 5 and len(p["itens"]) == 2
