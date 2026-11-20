from app.activities.baseActivity import BaseActivity


class CatalogoActivity(BaseActivity):
    def listar_categorias(self):
        return self._get("/categorias")

    def criar_categoria(self, nome: str, descricao: str | None = None):
        return self._post("/categorias", {"nome": nome, **({"descricao": descricao} if descricao else {})})

    def atualizar_categoria(self, id_: int, nome: str):
        return self._put(f"/categorias/{id_}", {"nome": nome})

    def listar_caracteristicas(self):
        return self._get("/caracteristicas")

    def criar_caracteristica(self, nome: str):
        return self._post("/caracteristicas", {"nome": nome})

    def atualizar_caracteristica(self, id_: int, nome: str):
        return self._put(f"/caracteristicas/{id_}", {"nome": nome})
