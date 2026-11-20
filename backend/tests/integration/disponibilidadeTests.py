from app.activities.disponibilidadeActivity import DisponibilidadeActivity


def numeros(resp):
    return [d["acomodacao"]["numero"] for d in resp.json()]


class DisponibilidadeTests:
    def test_todas_livres_ordenadas_por_diaria_com_total(self, disponibilidade_api):
        r = disponibilidade_api.consultar("2026-12-10", "2026-12-12")
        assert r.status_code == 200 and numeros(r) == ["101", "102", "201"]
        assert r.json()[0]["noites"] == 2 and r.json()[0]["valor_total"] == "300.00"

    def test_filtra_por_capacidade_e_categoria(self, disponibilidade_api):
        assert numeros(disponibilidade_api.consultar("2026-12-10", "2026-12-12", hospedes=4)) == ["201"]
        assert numeros(disponibilidade_api.consultar("2026-12-10", "2026-12-12", categoria_id=1)) == ["101", "102"]

    def test_reserva_viva_remove_do_resultado_e_cancelar_devolve(self, disponibilidade_api, reserva_api, hospede):
        reserva = reserva_api.criar(hospede["id"], 1, "2026-12-10", "2026-12-15").json()
        assert "101" not in numeros(disponibilidade_api.consultar("2026-12-12", "2026-12-14"))
        reserva_api.cancelar(reserva["id"])
        assert "101" in numeros(disponibilidade_api.consultar("2026-12-12", "2026-12-14"))

    def test_datas_limite_saida_no_dia_libera_entrada(self, disponibilidade_api, reserva_api, hospede):
        reserva_api.criar(hospede["id"], 1, "2026-12-10", "2026-12-15")
        assert "101" in numeros(disponibilidade_api.consultar("2026-12-15", "2026-12-17"))   # entra no dia da saída
        assert "101" in numeros(disponibilidade_api.consultar("2026-12-08", "2026-12-10"))   # sai no dia da entrada
        assert "101" not in numeros(disponibilidade_api.consultar("2026-12-14", "2026-12-16"))
        assert "101" not in numeros(disponibilidade_api.consultar("2026-12-09", "2026-12-11"))

    def test_inativa_nao_aparece(self, disponibilidade_api, acomodacao_api, gestao):
        acomodacao_api.como(gestao).definir_ativo(2, False)
        assert "102" not in numeros(disponibilidade_api.consultar("2026-12-10", "2026-12-12"))

    def test_validacoes_de_periodo(self, disponibilidade_api):
        assert disponibilidade_api.consultar("2026-12-12", "2026-12-12").status_code == 422
        assert disponibilidade_api.consultar("2026-12-12", "2026-12-10").status_code == 422
        r = disponibilidade_api.consultar("2026-11-01", "2026-11-03")
        assert r.status_code == 422 and "passado" in r.json()["erro"]

    def test_rota_alternativa_em_acomodacoes_devolve_o_mesmo(self, disponibilidade_api, acomodacao_api):
        a = disponibilidade_api.consultar("2026-12-10", "2026-12-12")
        b = acomodacao_api.disponiveis("2026-12-10", "2026-12-12")
        assert a.status_code == 200 and a.json() == b.json()

    def test_mapa_de_ocupacao(self, disponibilidade_api, reserva_api, hospede):
        reserva_api.criar(hospede["id"], 1, "2026-12-10", "2026-12-15")
        r = disponibilidade_api.mapa("2026-12-01", "2026-12-31")
        assert r.status_code == 200
        linha = {l["acomodacao"]["numero"]: l["reservas"] for l in r.json()}
        assert len(linha["101"]) == 1 and linha["101"][0]["hospede_nome"] == "Maria Souza"
        assert linha["102"] == []
        assert disponibilidade_api.mapa("2026-01-01", "2026-12-31").status_code == 422

    def test_exige_login(self, client):
        assert DisponibilidadeActivity(client).consultar("2026-12-10", "2026-12-12").status_code == 401
