from types import SimpleNamespace

import pytest

from app.core.errors import DuplicidadeError, NaoEncontradoError, RegraDeNegocioError
from app.services.hospedeService import HospedeService
from tests.unit.fakes import FakeHospedeRepository


def hospede_in(**kw):
    base = dict(nome="Ana", documento_tipo="CPF", documento_numero="529.982.247-25", email="a@x.com", telefone=None)
    return SimpleNamespace(**{**base, **kw})


class HospedeServiceTest:
    def test_criar_normaliza_o_documento(self):
        assert HospedeService(FakeHospedeRepository()).criar(hospede_in()).documento_numero == "52998224725"

    def test_criar_bloqueia_documento_duplicado_mesmo_com_mascara_diferente(self):
        s = HospedeService(FakeHospedeRepository())
        s.criar(hospede_in())
        with pytest.raises(DuplicidadeError):
            s.criar(hospede_in(documento_numero="52998224725", nome="Outra"))

    def test_criar_rejeita_cpf_invalido(self):
        with pytest.raises(RegraDeNegocioError):
            HospedeService(FakeHospedeRepository()).criar(hospede_in(documento_numero="111.111.111-11"))

    def test_obter_inexistente(self):
        with pytest.raises(NaoEncontradoError):
            HospedeService(FakeHospedeRepository()).obter(99)

    def test_atualizar_com_o_mesmo_documento_e_permitido(self):
        s = HospedeService(FakeHospedeRepository())
        h = s.criar(hospede_in())
        s.atualizar(h.id, hospede_in(nome="Ana Maria"))
        assert s.obter(h.id).nome == "Ana Maria"

    def test_atualizar_para_documento_de_outro_hospede_e_conflito(self):
        s = HospedeService(FakeHospedeRepository())
        s.criar(hospede_in())
        outro = s.criar(hospede_in(documento_tipo="RG", documento_numero="MG123", nome="Pedro"))
        with pytest.raises(DuplicidadeError):
            s.atualizar(outro.id, hospede_in(nome="Pedro"))

    def test_listar_delega_ao_repository(self):
        s = HospedeService(FakeHospedeRepository())
        s.criar(hospede_in())
        itens, total = s.listar(None, 10, 0)
        assert total == 1 and len(itens) == 1
