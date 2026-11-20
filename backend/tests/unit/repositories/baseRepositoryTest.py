"""SqlRepository e a tradução de erros do PostgreSQL. As consultas específicas (disponíveis, listar...)
precisam de PostgreSQL de verdade e são cobertas nos testes de integração."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflitoReservaError, DuplicidadeError, RegraDeNegocioError
from app.repositories.baseRepository import SqlRepository, traduzir_erro_banco


def integridade(sqlstate, constraint=None):
    orig = SimpleNamespace(sqlstate=sqlstate, diag=SimpleNamespace(constraint_name=constraint))
    return IntegrityError("INSERT", {}, orig)


class Repo(SqlRepository):
    model = dict


class BaseRepositoryTest:
    def test_exclusion_violation_vira_conflito_de_reserva(self):
        assert isinstance(traduzir_erro_banco(integridade("23P01")), ConflitoReservaError)

    def test_unique_violation_usa_mensagem_da_restricao_conhecida(self):
        erro = traduzir_erro_banco(integridade("23505", "ux_hospede_documento"))
        assert isinstance(erro, DuplicidadeError) and "documento" in erro.mensagem

    def test_unique_violation_desconhecida_tem_mensagem_generica(self):
        assert "Já existe um registro" in traduzir_erro_banco(integridade("23505", "outra")).mensagem

    @pytest.mark.parametrize("sqlstate", ["23503", "23514"])
    def test_fk_e_check_viram_regra_de_negocio(self, sqlstate):
        assert isinstance(traduzir_erro_banco(integridade(sqlstate)), RegraDeNegocioError)

    def test_erro_nao_mapeado_volta_como_veio(self):
        e = integridade("99999")
        assert traduzir_erro_banco(e) is e

    def test_add_envia_ao_banco_na_hora(self):
        session = Mock()
        item = {"x": 1}
        assert Repo(session).add(item) is item
        session.add.assert_called_once_with(item)
        session.flush.assert_called_once()
        session.refresh.assert_called_once_with(item)

    def test_salvar_traduz_o_erro_do_flush(self):
        session = Mock()
        session.flush.side_effect = integridade("23P01")
        with pytest.raises(ConflitoReservaError):
            Repo(session).salvar({})
        session.refresh.assert_not_called()

    def test_salvar_repropaga_erro_desconhecido(self):
        session = Mock()
        session.flush.side_effect = integridade("99999")
        with pytest.raises(IntegrityError):
            Repo(session).salvar({})

    def test_get_busca_pelo_modelo(self):
        session = Mock()
        session.get.return_value = "achou"
        assert Repo(session).get(5) == "achou"
        session.get.assert_called_once_with(dict, 5)
