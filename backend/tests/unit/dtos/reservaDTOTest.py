from datetime import date

import pytest
from pydantic import ValidationError

from app.dtos.reservaDTO import AlterarReservaIn, CancelarIn, NovaReservaIn

BASE = dict(hospede_id=1, acomodacao_id=1, data_entrada=date(2026, 12, 10), data_saida=date(2026, 12, 12), qtd_hospedes=2)


class ReservaDTOTest:
    def test_aceita_periodo_valido(self):
        assert NovaReservaIn(**BASE).qtd_hospedes == 2

    @pytest.mark.parametrize("saida", [date(2026, 12, 10), date(2026, 12, 9)])
    def test_saida_precisa_ser_depois_da_entrada(self, saida):
        with pytest.raises(ValidationError, match="posterior"):
            NovaReservaIn(**{**BASE, "data_saida": saida})

    @pytest.mark.parametrize("qtd", [0, -1, 21])
    def test_quantidade_de_hospedes_entre_1_e_20(self, qtd):
        with pytest.raises(ValidationError):
            NovaReservaIn(**{**BASE, "qtd_hospedes": qtd})

    def test_alterar_usa_a_mesma_regra_de_periodo(self):
        with pytest.raises(ValidationError):
            AlterarReservaIn(data_entrada=date(2026, 12, 10), data_saida=date(2026, 12, 10), qtd_hospedes=1)

    def test_cancelar_limpa_o_motivo(self):
        assert CancelarIn(motivo="  mudou ").motivo == "mudou"
        assert CancelarIn(motivo="  ").motivo is None and CancelarIn().motivo is None
