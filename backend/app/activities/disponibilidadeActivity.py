from app.activities.baseActivity import BaseActivity


class DisponibilidadeActivity(BaseActivity):
    def consultar(self, entrada: str, saida: str, hospedes: int = 1, **extra):
        return self._get("/disponibilidade", entrada=entrada, saida=saida, hospedes=hospedes, **extra)

    def mapa(self, ini: str, fim: str):
        return self._get("/disponibilidade/mapa", ini=ini, fim=fim)
