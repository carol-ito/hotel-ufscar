from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """As tabelas são criadas por db/schema.sql; os models só as mapeiam."""
