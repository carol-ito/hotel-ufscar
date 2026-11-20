"""Relógio injetável: os testes substituem por um relógio fixo."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.core.config import get_settings


class Relogio:
    def agora(self) -> datetime:
        return datetime.now(ZoneInfo(get_settings().timezone))

    def hoje(self) -> date:
        return self.agora().date()
