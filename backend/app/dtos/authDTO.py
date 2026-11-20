from pydantic import BaseModel, Field

from app.dtos.comumDTO import Saida


class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=160)
    senha: str = Field(min_length=1, max_length=128)


class UsuarioOut(Saida):
    id: int
    nome: str
    email: str
    perfil: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: UsuarioOut
