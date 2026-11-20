"""Configuração comum. A integração usa PostgreSQL de verdade (a regra anti-overbooking é uma
restrição do PostgreSQL), criado do mesmo db/schema.sql que vai para produção."""
import os
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "postgresql://hotel:hotel@localhost:5432/hotel_test")
os.environ.setdefault("JWT_SECRET", "segredo-de-teste-com-pelo-menos-32-caracteres")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

SCHEMA = Path(__file__).resolve().parents[2] / "db" / "schema.sql"
HOJE = date(2026, 11, 6)


class RelogioFixo:
    """Os services recebem o relógio por injeção: testes não dependem da data real."""

    def __init__(self, hoje: date = HOJE):
        self._hoje = hoje

    def hoje(self) -> date:
        return self._hoje

    def agora(self) -> datetime:
        return datetime(self._hoje.year, self._hoje.month, self._hoje.day, 12, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
