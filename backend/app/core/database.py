"""Engine e Unit of Work: uma sessão e um commit por requisição."""
from collections.abc import Iterator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine():
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False, autoflush=True)


def get_session() -> Iterator[Session]:
    session = get_sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# scope="function": o commit (e portanto uma violação detectada nele) acontece ANTES de a resposta
# ser enviada; assim o cliente nunca recebe 201 por algo que ainda não foi gravado.
SESSAO = Depends(get_session, scope="function")
