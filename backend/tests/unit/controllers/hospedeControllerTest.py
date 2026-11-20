from unittest.mock import Mock

from app.controllers import hospedeController
from app.dtos.hospedeDTO import HospedeIn
from tests.unit.fakes import hospede_obj

DADOS = HospedeIn(nome="Ana Lima", documento_tipo="CPF", documento_numero="52998224725", telefone="16999")


class HospedeControllerTest:
    def test_listar_monta_a_pagina_com_os_parametros_recebidos(self):
        service = Mock(listar=Mock(return_value=([hospede_obj(1), hospede_obj(2)], 7)))
        pagina = hospedeController.listar(q="ana", limite=2, offset=4, _=None, service=service)
        service.listar.assert_called_once_with("ana", 2, 4)
        assert (pagina.total, pagina.limite, pagina.offset, len(pagina.itens)) == (7, 2, 4, 2)

    def test_criar_delega_ao_service(self):
        service = Mock(criar=Mock(return_value="novo"))
        assert hospedeController.criar(DADOS, _=None, service=service) == "novo"
        service.criar.assert_called_once_with(DADOS)

    def test_obter_delega_ao_service(self):
        service = Mock(obter=Mock(return_value="h"))
        assert hospedeController.obter(5, _=None, service=service) == "h"
        service.obter.assert_called_once_with(5)

    def test_atualizar_delega_id_e_dados(self):
        service = Mock(atualizar=Mock(return_value="h"))
        assert hospedeController.atualizar(5, DADOS, _=None, service=service) == "h"
        service.atualizar.assert_called_once_with(5, DADOS)

    def test_expoe_as_rotas_de_hospedes(self):
        perfis = {r.path: r.methods for r in hospedeController.router.routes}
        assert "/hospedes" in perfis and "/hospedes/{hospede_id}" in perfis
