"""Base das classes <api>Activity: cada Activity conhece as rotas de UMA API e esconde o HTTP dos testes."""


class BaseActivity:
    def __init__(self, client, headers: dict | None = None):
        self.client, self.headers = client, headers or {}

    def como(self, headers: dict):
        """Mesma API, chamada por outro usuário (ex.: .como(gestao))."""
        return type(self)(self.client, headers)

    def _get(self, caminho, **params):
        return self.client.get(caminho, headers=self.headers, params=params or None)

    def _post(self, caminho, json=None):
        return self.client.post(caminho, headers=self.headers, json=json)

    def _put(self, caminho, json):
        return self.client.put(caminho, headers=self.headers, json=json)

    def _patch(self, caminho, json):
        return self.client.patch(caminho, headers=self.headers, json=json)
