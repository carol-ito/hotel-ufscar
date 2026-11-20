from app.core.errors import NaoAutenticadoError
from app.core.security import emitir_token, verificar_senha


class AuthService:
    def __init__(self, usuarios):
        self.usuarios = usuarios

    def login(self, email: str, senha: str):
        usuario = self.usuarios.get_por_email(email)
        # mesma mensagem para e-mail inexistente, senha errada e usuário inativo
        if usuario is None or not usuario.ativo or not verificar_senha(senha, usuario.senha_hash):
            raise NaoAutenticadoError("E-mail ou senha inválidos")
        token, expira_em = emitir_token(usuario.id, usuario.perfil)
        return token, expira_em, usuario
