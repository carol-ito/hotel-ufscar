from app.activities.acomodacaoActivity import dados_acomodacao


class AcomodacaoTests:
    def test_gestao_cria_com_caracteristicas(self, acomodacao_api, gestao):
        r = acomodacao_api.como(gestao).criar()
        assert r.status_code == 201
        corpo = r.json()
        assert corpo["status"] == "LIVRE" and corpo["ativo"] is True
        assert {c["nome"] for c in corpo["caracteristicas"]} == {"Ar-condicionado", "Frigobar"}
        assert corpo["categoria"]["nome"] == "Luxo"

    def test_recepcao_nao_edita_catalogo_403(self, acomodacao_api):
        assert acomodacao_api.criar().status_code == 403
        assert acomodacao_api.atualizar(1, dados_acomodacao()).status_code == 403
        assert acomodacao_api.definir_ativo(1, False).status_code == 403

    def test_recepcao_consulta(self, acomodacao_api):
        assert len(acomodacao_api.listar().json()) == 3
        assert acomodacao_api.obter(1).status_code == 200

    def test_numero_duplicado_409(self, acomodacao_api, gestao):
        assert acomodacao_api.como(gestao).criar(dados_acomodacao(numero="101")).status_code == 409

    def test_categoria_inexistente_404(self, acomodacao_api, gestao):
        assert acomodacao_api.como(gestao).criar(dados_acomodacao(categoria_id=99)).status_code == 404

    def test_valores_invalidos_422(self, acomodacao_api, gestao):
        api = acomodacao_api.como(gestao)
        assert api.criar(dados_acomodacao(valor_diaria="0")).status_code == 422
        assert api.criar(dados_acomodacao(capacidade=0)).status_code == 422

    def test_atualizar_preco_nao_altera_reserva_existente(self, acomodacao_api, reserva_api, gestao, hospede):
        reserva = reserva_api.criar(hospede["id"]).json()
        r = acomodacao_api.como(gestao).atualizar(1, dados_acomodacao(numero="101", categoria_id=1, valor_diaria="999.00", caracteristica_ids=[]))
        assert r.status_code == 200 and r.json()["valor_diaria"] == "999.00"
        depois = reserva_api.obter(reserva["id"]).json()
        assert depois["valor_diaria"] == "150.00" and depois["valor_total"] == "750.00"

    def test_nao_reduz_capacidade_abaixo_de_reserva_ativa(self, acomodacao_api, reserva_api, gestao, hospede):
        reserva_api.criar(hospede["id"], acomodacao_id=2, qtd=3)
        r = acomodacao_api.como(gestao).atualizar(2, dados_acomodacao(numero="102", categoria_id=1, capacidade=2,
                                                                      valor_diaria="180.00", caracteristica_ids=[]))
        assert r.status_code == 422

    def test_inativar_bloqueado_com_reserva_ativa_e_liberado_depois(self, acomodacao_api, reserva_api, gestao, hospede):
        reserva = reserva_api.criar(hospede["id"]).json()
        api = acomodacao_api.como(gestao)
        assert api.definir_ativo(1, False).status_code == 422
        reserva_api.cancelar(reserva["id"], "desistiu")
        r = api.definir_ativo(1, False)
        assert r.status_code == 200 and r.json()["ativo"] is False

    def test_acomodacao_inativa_nao_aceita_reserva(self, acomodacao_api, reserva_api, gestao, hospede):
        acomodacao_api.como(gestao).definir_ativo(1, False)
        r = reserva_api.criar(hospede["id"])
        assert r.status_code == 422 and "inativa" in r.json()["erro"]

    def test_disponiveis_ordenadas_por_diaria_com_total(self, acomodacao_api):
        r = acomodacao_api.disponiveis("2026-12-10", "2026-12-12")
        assert [d["acomodacao"]["numero"] for d in r.json()] == ["101", "102", "201"]
        assert r.json()[0]["noites"] == 2 and r.json()[0]["valor_total"] == "300.00"
