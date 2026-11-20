"""Configuração por variáveis de ambiente (nenhum segredo no repositório)."""
import os
from dataclasses import dataclass, field


def normalizar_database_url(url: str) -> str:
    """Aceita as URLs no formato do Neon/Render (postgres://, postgresql://) e
    devolve a que o SQLAlchemy precisa para usar o driver psycopg 3."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


@dataclass(frozen=True)
class Settings:
    database_url: str = field(default_factory=lambda: normalizar_database_url(
        os.getenv("DATABASE_URL", "postgresql://hotel:hotel@localhost:5432/hotel")))
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", "troque-este-segredo-em-producao-com-32-ou-mais-caracteres"))
    jwt_expire_minutes: int = field(default_factory=lambda: int(os.getenv("JWT_EXPIRE_MINUTES", "60")))
    cors_origins: list[str] = field(default_factory=lambda: [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()])
    timezone: str = field(default_factory=lambda: os.getenv("HOTEL_TIMEZONE", "America/Sao_Paulo"))


def get_settings() -> Settings:
    return Settings()
