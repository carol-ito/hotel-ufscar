from datetime import datetime

from app.core.relogio import Relogio


class RelogioTest:
    def test_agora_tem_fuso_do_hotel(self, monkeypatch):
        monkeypatch.setenv("HOTEL_TIMEZONE", "America/Sao_Paulo")
        agora = Relogio().agora()
        assert isinstance(agora, datetime) and agora.tzinfo is not None and agora.utcoffset().total_seconds() == -3 * 3600

    def test_hoje_e_a_data_de_agora(self):
        r = Relogio()
        assert abs((r.hoje() - r.agora().date()).days) <= 1
