class CatalogoTests:
    def test_recepcao_consulta_mas_nao_edita(self, catalogo_api):
        assert len(catalogo_api.listar_categorias().json()) == 2
        assert len(catalogo_api.listar_caracteristicas().json()) == 2
        assert catalogo_api.criar_categoria("Suíte").status_code == 403
        assert catalogo_api.criar_caracteristica("Varanda").status_code == 403

    def test_gestao_cria_atualiza_e_nao_duplica_categoria(self, catalogo_api, gestao):
        api = catalogo_api.como(gestao)
        r = api.criar_categoria("Suíte", "Com sala")
        assert r.status_code == 201
        assert api.criar_categoria("Suíte").status_code == 409
        assert api.atualizar_categoria(r.json()["id"], "Suíte Master").status_code == 200

    def test_gestao_cria_caracteristica_sem_duplicar_e_404_ao_atualizar_inexistente(self, catalogo_api, gestao):
        api = catalogo_api.como(gestao)
        assert api.criar_caracteristica("Varanda").status_code == 201
        assert api.criar_caracteristica("Varanda").status_code == 409
        assert api.atualizar_caracteristica(999, "Xis").status_code == 404
