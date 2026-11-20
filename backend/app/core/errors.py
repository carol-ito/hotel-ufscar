"""Erros de domínio. Cada um carrega o código HTTP; um único handler em main.py
os converte em {"erro": "mensagem"}."""


class DominioError(Exception):
    status_code = 400
    mensagem_padrao = "Erro de domínio"

    def __init__(self, mensagem: str | None = None):
        self.mensagem = mensagem or self.mensagem_padrao
        super().__init__(self.mensagem)


class NaoAutenticadoError(DominioError):
    status_code = 401
    mensagem_padrao = "Não autenticado"


class AcessoNegadoError(DominioError):
    status_code = 403
    mensagem_padrao = "Seu perfil não tem permissão para esta operação"


class NaoEncontradoError(DominioError):
    status_code = 404
    mensagem_padrao = "Registro não encontrado"


class RegraDeNegocioError(DominioError):
    status_code = 422
    mensagem_padrao = "Regra de negócio violada"


class ConflitoError(DominioError):
    status_code = 409
    mensagem_padrao = "Conflito com um registro existente"


class ConflitoReservaError(ConflitoError):
    mensagem_padrao = "A acomodação já está reservada em parte do período informado"


class DuplicidadeError(ConflitoError):
    mensagem_padrao = "Já existe um registro com esses dados"


class TransicaoInvalidaError(ConflitoError):
    def __init__(self, estado: str, operacao: str):
        super().__init__(f"Operação '{operacao}' não permitida para reserva {estado}")
