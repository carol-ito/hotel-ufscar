from app.activities.baseActivity import BaseActivity


class ReservaActivity(BaseActivity):
    def criar(self, hospede_id: int, acomodacao_id: int = 1, entrada: str = "2026-12-10", saida: str = "2026-12-15",
              qtd: int = 2):
        return self._post("/reservas", {"hospede_id": hospede_id, "acomodacao_id": acomodacao_id,
                                        "data_entrada": entrada, "data_saida": saida, "qtd_hospedes": qtd})

    def obter(self, id_: int):
        return self._get(f"/reservas/{id_}")

    def listar(self, **filtros):
        return self._get("/reservas", **filtros)

    def alterar(self, id_: int, entrada: str, saida: str, qtd: int):
        return self._put(f"/reservas/{id_}", {"data_entrada": entrada, "data_saida": saida, "qtd_hospedes": qtd})

    def confirmar(self, id_: int):
        return self._post(f"/reservas/{id_}/confirmar")

    def cancelar(self, id_: int, motivo: str | None = None, com_corpo: bool = True):
        return self._post(f"/reservas/{id_}/cancelar", ({"motivo": motivo} if motivo else {}) if com_corpo else None)
