from app.domain.politicaStatus import calcular_status
from datetime import date
from tests.unit.fakes import HOJE, reserva


class PoliticaStatusTest:
    def test_sem_reservas_o_quarto_esta_livre(self):
        assert calcular_status([], HOJE) == "LIVRE"

    def test_pendente_nao_reserva_o_quarto(self):
        assert calcular_status([reserva("PENDENTE", date(2026, 11, 5), date(2026, 11, 8))], HOJE) == "LIVRE"

    def test_confirmada_cobrindo_hoje_reserva(self):
        assert calcular_status([reserva("CONFIRMADA", date(2026, 11, 6), date(2026, 11, 8))], HOJE) == "RESERVADO"

    def test_confirmada_futura_nao_reserva_hoje(self):
        assert calcular_status([reserva("CONFIRMADA", date(2026, 11, 7), date(2026, 11, 9))], HOJE) == "LIVRE"

    def test_saida_hoje_nao_ocupa(self):
        assert calcular_status([reserva("CONFIRMADA", date(2026, 11, 4), date(2026, 11, 6))], HOJE) == "LIVRE"

    def test_em_andamento_ocupa_e_vence_a_reservada(self):
        conf = reserva("CONFIRMADA", date(2026, 11, 6), date(2026, 11, 8))
        em_andamento = reserva("EM_ANDAMENTO", date(2026, 11, 5), date(2026, 11, 7))
        assert calcular_status([conf, em_andamento], HOJE) == "OCUPADO"
