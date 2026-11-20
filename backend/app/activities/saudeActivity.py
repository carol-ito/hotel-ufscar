from app.activities.baseActivity import BaseActivity


class SaudeActivity(BaseActivity):
    def api(self):
        return self._get("/health")

    def banco(self):
        return self._get("/health/db")

    def rota_inexistente(self):
        return self._get("/rota-que-nao-existe")
