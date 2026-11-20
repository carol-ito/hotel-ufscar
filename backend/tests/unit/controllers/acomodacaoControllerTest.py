from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from app.controllers import acomodacaoController as c
from app.dtos.acomodacaoDTO import AcomodacaoIn, AtivoIn
from tests.unit.fakes import acomodacao_obj

DADOS = AcomodacaoIn(numero="301", categoria_id=1, capacidade=2, valor_diaria=Decimal("200"))


class AcomodacaoControllerTest:
    def test_listar_repassa_os_filtros(self):
        service = Mock(listar=Mock(return_value=["a"]))
        assert c.listar(ativo=True, categoria_id=2, status="LIVRE", _=None, service=service) == ["a"]
        service.listar.assert_called_once_with(True, 2, "LIVRE")

    def test_disponiveis_converte_para_dto_com_noites_e_total(self):
        disp = SimpleNamespace(acomodacao=acomodacao_obj(), noites=3, valor_total=Decimal("450.00"))
        service = Mock(consultar=Mock(return_value=[disp]))
        r = c.disponiveis(entrada=date(2026, 12, 1), saida=date(2026, 12, 4), hospedes=2, categoria_id=None,
                          _=None, service=service)
        service.consultar.assert_called_once_with(date(2026, 12, 1), date(2026, 12, 4), 2, None)
        assert r[0].noites == 3 and r[0].valor_total == Decimal("450.00") and r[0].acomodacao.numero == "101"

    def test_obter_criar_atualizar_delegam(self):
        service = Mock()
        c.obter(1, _=None, service=service)
        c.criar(DADOS, _=None, service=service)
        c.atualizar(1, DADOS, _=None, service=service)
        service.obter.assert_called_once_with(1)
        service.criar.assert_called_once_with(DADOS)
        service.atualizar.assert_called_once_with(1, DADOS)

    def test_definir_ativo_passa_so_o_booleano(self):
        service = Mock()
        c.definir_ativo(1, AtivoIn(ativo=False), _=None, service=service)
        service.definir_ativo.assert_called_once_with(1, False)

    def test_disponiveis_vem_antes_de_id_para_nao_ser_lida_como_id(self):
        caminhos = [r.path for r in c.router.routes]
        assert caminhos.index("/acomodacoes/disponiveis") < caminhos.index("/acomodacoes/{acomodacao_id}")
