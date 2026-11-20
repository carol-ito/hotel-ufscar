import pytest

from app.core.errors import (AcessoNegadoError, ConflitoReservaError, DominioError, DuplicidadeError, NaoAutenticadoError,
                             NaoEncontradoError, RegraDeNegocioError, TransicaoInvalidaError)


class ErrorsTest:
    @pytest.mark.parametrize("erro,status", [
        (NaoAutenticadoError(), 401), (AcessoNegadoError(), 403), (NaoEncontradoError(), 404),
        (RegraDeNegocioError(), 422), (ConflitoReservaError(), 409), (DuplicidadeError(), 409),
        (TransicaoInvalidaError("PENDENTE", "checkin"), 409)])
    def test_cada_erro_carrega_o_seu_codigo_http(self, erro, status):
        assert isinstance(erro, DominioError) and erro.status_code == status

    def test_mensagem_propria_substitui_a_padrao(self):
        assert NaoEncontradoError("Hóspede não encontrado").mensagem == "Hóspede não encontrado"
        assert NaoEncontradoError().mensagem == "Registro não encontrado"

    def test_transicao_invalida_cita_estado_e_operacao(self):
        assert "checkin" in TransicaoInvalidaError("PENDENTE", "checkin").mensagem
