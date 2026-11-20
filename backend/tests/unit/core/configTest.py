from app.core.config import Settings, get_settings, normalizar_database_url


class ConfigTest:
    def test_normaliza_url_do_neon_e_do_render(self):
        assert normalizar_database_url("postgres://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
        assert normalizar_database_url("postgresql://u:p@h/db?sslmode=require") == "postgresql+psycopg://u:p@h/db?sslmode=require"

    def test_url_ja_normalizada_nao_muda(self):
        assert normalizar_database_url("postgresql+psycopg://u:p@h/db") == "postgresql+psycopg://u:p@h/db"

    def test_settings_le_variaveis_de_ambiente(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "http://a.com, http://b.com ,")
        monkeypatch.setenv("JWT_EXPIRE_MINUTES", "15")
        monkeypatch.setenv("HOTEL_TIMEZONE", "America/Manaus")
        s = get_settings()
        assert s.cors_origins == ["http://a.com", "http://b.com"] and s.jwt_expire_minutes == 15
        assert s.timezone == "America/Manaus"

    def test_settings_e_imutavel(self):
        import dataclasses
        import pytest
        with pytest.raises(dataclasses.FrozenInstanceError):
            Settings().timezone = "UTC"
