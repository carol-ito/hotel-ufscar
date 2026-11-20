from fastapi import APIRouter, Depends

from app.core.dependencies import get_auth_service, get_usuario_atual
from app.dtos.authDTO import LoginIn, TokenOut, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Acesso"])


@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, service=Depends(get_auth_service)):
    token, expira_em, usuario = service.login(dados.email, dados.senha)
    return TokenOut(access_token=token, expires_in=expira_em, usuario=UsuarioOut.model_validate(usuario))


@router.get("/me", response_model=UsuarioOut)
def me(usuario=Depends(get_usuario_atual)):
    return usuario
