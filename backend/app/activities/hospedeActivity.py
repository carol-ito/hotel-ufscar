from app.activities.baseActivity import BaseActivity

CPF_VALIDO = "529.982.247-25"


def dados_hospede(**alteracoes) -> dict:
    return {"nome": "João da Silva", "documento_tipo": "CPF", "documento_numero": CPF_VALIDO,
            "telefone": "(16) 99999-0000", **alteracoes}


class HospedeActivity(BaseActivity):
    def criar(self, dados: dict | None = None):
        return self._post("/hospedes", dados or dados_hospede())

    def listar(self, **filtros):
        return self._get("/hospedes", **filtros)

    def obter(self, id_: int):
        return self._get(f"/hospedes/{id_}")

    def atualizar(self, id_: int, dados: dict):
        return self._put(f"/hospedes/{id_}", dados)
