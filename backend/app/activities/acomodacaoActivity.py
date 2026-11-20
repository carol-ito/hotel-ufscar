from app.activities.baseActivity import BaseActivity


def dados_acomodacao(**alteracoes) -> dict:
    return {"numero": "301", "categoria_id": 2, "capacidade": 2, "valor_diaria": "410.50",
            "caracteristica_ids": [1, 2], **alteracoes}


class AcomodacaoActivity(BaseActivity):
    def listar(self, **filtros):
        return self._get("/acomodacoes", **filtros)

    def obter(self, id_: int):
        return self._get(f"/acomodacoes/{id_}")

    def criar(self, dados: dict | None = None):
        return self._post("/acomodacoes", dados or dados_acomodacao())

    def atualizar(self, id_: int, dados: dict):
        return self._put(f"/acomodacoes/{id_}", dados)

    def definir_ativo(self, id_: int, ativo: bool):
        return self._patch(f"/acomodacoes/{id_}/ativo", {"ativo": ativo})

    def disponiveis(self, entrada: str, saida: str, hospedes: int = 1, **extra):
        return self._get("/acomodacoes/disponiveis", entrada=entrada, saida=saida, hospedes=hospedes, **extra)

    def status_de(self, id_: int) -> str:
        return self.obter(id_).json()["status"]
