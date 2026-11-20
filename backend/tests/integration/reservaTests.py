import threading

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.dependencies import get_relogio
from app.main import create_app
from tests.conftest import RelogioFixo
from app.activities.authActivity import AuthActivity
from app.activities.reservaActivity import ReservaActivity


class ReservaTests:
    def test_cria_pendente_com_valores_copiados(self, reserva_api, hospede):
        r = reserva_api.criar(hospede["id"], 1, "2026-12-10", "2026-12-15")
        assert r.status_code == 201
        corpo = r.json()
        assert corpo["status"] == "PENDENTE" and corpo["noites"] == 5
        assert corpo["valor_diaria"] == "150.00" and corpo["valor_total"] == "750.00"
        assert corpo["hospede"]["nome"] == "Maria Souza" and corpo["acomodacao"]["numero"] == "101"
        assert set(corpo["acoes_permitidas"]) == {"alterar", "confirmar", "cancelar"}

    def test_sobreposicao_409_e_datas_limite(self, reserva_api, hospede):
        h = hospede["id"]
        reserva_api.criar(h, 1, "2026-12-10", "2026-12-15")
        for entrada, saida in [("2026-12-12", "2026-12-18"), ("2026-12-11", "2026-12-13"), ("2026-12-08", "2026-12-11")]:
            assert reserva_api.criar(h, 1, entrada, saida).status_code == 409, (entrada, saida)
        assert reserva_api.criar(h, 1, "2026-12-15", "2026-12-17").status_code == 201
        assert reserva_api.criar(h, 1, "2026-12-08", "2026-12-10").status_code == 201
        assert reserva_api.criar(h, 2, "2026-12-10", "2026-12-15").status_code == 201

    def test_cancelar_libera_periodo(self, reserva_api, hospede):
        r = reserva_api.criar(hospede["id"]).json()
        c = reserva_api.cancelar(r["id"], "  mudou de planos ")
        assert c.status_code == 200
        assert c.json()["status"] == "CANCELADA" and c.json()["motivo_cancelamento"] == "mudou de planos"
        assert c.json()["acoes_permitidas"] == []
        assert reserva_api.criar(hospede["id"]).status_code == 201

    def test_cancelar_sem_corpo(self, reserva_api, hospede):
        r = reserva_api.criar(hospede["id"]).json()
        assert reserva_api.cancelar(r["id"], com_corpo=False).status_code == 200

    def test_validacoes_de_criacao(self, reserva_api, hospede):
        h = hospede["id"]
        assert reserva_api.criar(999).status_code == 404                                   # hóspede
        assert reserva_api.criar(h, 99).status_code == 404                                 # acomodação
        r = reserva_api.criar(h, 1, qtd=3)                                                 # capacidade 2
        assert r.status_code == 422 and "no máximo 2" in r.json()["erro"]
        r = reserva_api.criar(h, 1, "2026-11-01", "2026-11-03")
        assert r.status_code == 422 and "passado" in r.json()["erro"]
        r = reserva_api.criar(h, 1, "2026-12-10", "2026-12-10")
        assert r.status_code == 422 and "saída" in r.json()["erro"]
        assert reserva_api.criar(h, 1, qtd=0).status_code == 422

    def test_confirmar_e_transicoes_invalidas_409(self, reserva_api, hospede):
        r = reserva_api.criar(hospede["id"]).json()
        ok = reserva_api.confirmar(r["id"])
        assert ok.status_code == 200 and ok.json()["status"] == "CONFIRMADA" and ok.json()["confirmada_em"]
        assert set(ok.json()["acoes_permitidas"]) == {"alterar", "cancelar"}
        assert reserva_api.confirmar(r["id"]).status_code == 409
        reserva_api.cancelar(r["id"])
        assert reserva_api.cancelar(r["id"]).status_code == 409
        assert reserva_api.alterar(r["id"], "2026-12-11", "2026-12-12", 1).status_code == 409

    def test_alterar_periodo_recalcula_total_e_mantem_diaria(self, reserva_api, hospede):
        r = reserva_api.criar(hospede["id"], 1, "2026-12-10", "2026-12-15").json()
        a = reserva_api.alterar(r["id"], "2026-12-10", "2026-12-12", 1)
        assert a.status_code == 200
        assert a.json()["noites"] == 2 and a.json()["valor_total"] == "300.00" and a.json()["qtd_hospedes"] == 1

    def test_alterar_para_colidir_409_e_estender_a_si_mesmo_ok(self, reserva_api, hospede):
        a = reserva_api.criar(hospede["id"], 1, "2026-12-10", "2026-12-15").json()
        b = reserva_api.criar(hospede["id"], 1, "2026-12-20", "2026-12-22").json()
        assert reserva_api.alterar(b["id"], "2026-12-14", "2026-12-22", 2).status_code == 409
        assert reserva_api.obter(b["id"]).json()["data_entrada"] == "2026-12-20"      # nada mudou
        assert reserva_api.alterar(a["id"], "2026-12-10", "2026-12-19", 2).status_code == 200

    def test_alterar_validacoes(self, reserva_api, hospede):
        r = reserva_api.criar(hospede["id"]).json()
        assert reserva_api.alterar(r["id"], "2026-12-10", "2026-12-15", 3).status_code == 422
        assert reserva_api.alterar(r["id"], "2026-11-01", "2026-11-03", 1).status_code == 422

    def test_status_do_quarto_acompanha_a_reserva(self, reserva_api, acomodacao_api, hospede):
        # "hoje" é 2026-11-06 no relógio fixo dos testes
        assert reserva_api.criar(hospede["id"], 1, "2026-11-05", "2026-11-08").status_code == 422   # entrada no passado
        r = reserva_api.criar(hospede["id"], 1, "2026-11-06", "2026-11-08").json()
        assert acomodacao_api.status_de(1) == "LIVRE"            # pendente não prende o quarto
        reserva_api.confirmar(r["id"])
        assert acomodacao_api.status_de(1) == "RESERVADO"        # confirmada cobrindo hoje
        reserva_api.cancelar(r["id"])
        assert acomodacao_api.status_de(1) == "LIVRE"

    def test_confirmada_futura_nao_reserva_o_quarto_hoje(self, reserva_api, acomodacao_api, hospede):
        r = reserva_api.criar(hospede["id"], 1, "2026-12-10", "2026-12-12").json()
        reserva_api.confirmar(r["id"])
        assert acomodacao_api.status_de(1) == "LIVRE"

    def test_listagem_com_filtros_e_ordem(self, reserva_api, hospede):
        a = reserva_api.criar(hospede["id"], 1, "2026-12-10", "2026-12-12").json()
        reserva_api.criar(hospede["id"], 2, "2026-12-20", "2026-12-22")
        reserva_api.confirmar(a["id"])
        todas = reserva_api.listar().json()
        assert todas["total"] == 2 and [r["data_entrada"] for r in todas["itens"]] == ["2026-12-20", "2026-12-10"]
        assert reserva_api.listar(status="CONFIRMADA").json()["total"] == 1
        assert reserva_api.listar(acomodacao_id=2).json()["total"] == 1
        assert reserva_api.listar(entrada_de="2026-12-15").json()["total"] == 1
        assert reserva_api.listar(hospede_id=999).json()["total"] == 0
        assert reserva_api.listar(status="XPTO").status_code == 422

    def test_inexistente_404_e_sem_login_401(self, reserva_api, client):
        assert reserva_api.obter(999).status_code == 404
        assert reserva_api.confirmar(999).status_code == 404
        assert ReservaActivity(client).listar().status_code == 401

    def test_banco_barra_a_corrida_entre_dois_atendentes(self, banco, hospede):
        """Duas requisições simultâneas passam pela pré-checagem; a restrição do banco aceita uma só (409 na outra)."""
        atendentes, resultados, barreira = [], [], threading.Barrier(2)
        for _ in range(2):
            app = create_app()
            app.dependency_overrides[get_relogio] = lambda: RelogioFixo()
            c = TestClient(app)
            atendentes.append(ReservaActivity(c, AuthActivity(c).cabecalho_de("recepcao@hotel.test")))

        def disparar(atendente):
            barreira.wait()
            resultados.append(atendente.criar(hospede["id"], 3, "2026-12-20", "2026-12-25").status_code)

        threads = [threading.Thread(target=disparar, args=(a,)) for a in atendentes]
        [t.start() for t in threads]
        [t.join() for t in threads]
        assert sorted(resultados) == [201, 409]
        with banco.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM reserva WHERE acomodacao_id = 3")).scalar() == 1
