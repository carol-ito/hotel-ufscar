"""Hash de senha (bcrypt) e emissão/leitura do JWT."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.errors import NaoAutenticadoError

ALGORITMO = "HS256"


def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode()[:72], bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode()[:72], senha_hash.encode())
    except ValueError:
        return False


def emitir_token(usuario_id: int, perfil: str, agora: datetime | None = None) -> tuple[str, int]:
    """Token com expiração curta e sem refresh: ao expirar, novo login."""
    cfg = get_settings()
    agora = agora or datetime.now(timezone.utc)
    exp = agora + timedelta(minutes=cfg.jwt_expire_minutes)
    token = jwt.encode({"sub": str(usuario_id), "perfil": perfil, "exp": exp, "iat": agora},
                       cfg.jwt_secret, algorithm=ALGORITMO)
    return token, cfg.jwt_expire_minutes * 60


def ler_token(token: str) -> dict:
    try:
        return jwt.decode(token, get_settings().jwt_secret, algorithms=[ALGORITMO])
    except jwt.ExpiredSignatureError as e:
        raise NaoAutenticadoError("Sessão expirada. Entre novamente.") from e
    except jwt.PyJWTError as e:
        raise NaoAutenticadoError("Token inválido") from e
