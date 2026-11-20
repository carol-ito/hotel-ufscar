"""Injeção de dependência: o grafo de objetos é montado aqui, num só lugar,
e os testes substituem peças com app.dependency_overrides."""
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SESSAO
from app.core.errors import AcessoNegadoError, NaoAutenticadoError
from app.core.relogio import Relogio
from app.core.security import ler_token
from app.domain.reservaObserver import EVENTOS_QUE_ATUALIZAM_STATUS, AtualizarStatusAcomodacao, EventBus
from app.models import Usuario
from app.repositories.acomodacaoRepository import (AcomodacaoRepository, CaracteristicaRepository,
                                                    CategoriaRepository)
from app.repositories.hospedeRepository import HospedeRepository
from app.repositories.reservaRepository import ReservaRepository
from app.repositories.usuarioRepository import UsuarioRepository
from app.services.acomodacaoService import AcomodacaoService, CatalogoService
from app.services.authService import AuthService
from app.services.disponibilidadeService import DisponibilidadeService
from app.services.hospedeService import HospedeService
from app.services.reservaService import ReservaService

GESTAO, RECEPCAO = "GESTAO", "RECEPCAO"
_bearer = HTTPBearer(auto_error=False)


def get_relogio() -> Relogio:
    return Relogio()


def get_usuario_atual(cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
                      session: Session = SESSAO) -> Usuario:
    if cred is None:
        raise NaoAutenticadoError("Token ausente")
    dados = ler_token(cred.credentials)
    usuario = UsuarioRepository(session).get(int(dados["sub"]))
    if usuario is None or not usuario.ativo:
        raise NaoAutenticadoError("Usuário inexistente ou inativo")
    return usuario


def require_role(*perfis: str):
    """Autorização por perfil: cada endpoint declara quem pode chamá-lo."""
    def dependencia(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
        if usuario.perfil not in perfis:
            raise AcessoNegadoError()
        return usuario
    return dependencia


def get_auth_service(session: Session = SESSAO) -> AuthService:
    return AuthService(UsuarioRepository(session))


def get_hospede_service(session: Session = SESSAO) -> HospedeService:
    return HospedeService(HospedeRepository(session))


def get_catalogo_service(session: Session = SESSAO) -> CatalogoService:
    return CatalogoService(CategoriaRepository(session), CaracteristicaRepository(session))


def get_acomodacao_service(session: Session = SESSAO,
                           relogio: Relogio = Depends(get_relogio)) -> AcomodacaoService:
    return AcomodacaoService(AcomodacaoRepository(session), CategoriaRepository(session),
                             CaracteristicaRepository(session), ReservaRepository(session), relogio)


def get_disponibilidade_service(session: Session = SESSAO,
                                relogio: Relogio = Depends(get_relogio)) -> DisponibilidadeService:
    return DisponibilidadeService(AcomodacaoRepository(session), ReservaRepository(session), relogio)


def get_reserva_service(session: Session = SESSAO,
                        relogio: Relogio = Depends(get_relogio)) -> ReservaService:
    reservas, acomodacoes = ReservaRepository(session), AcomodacaoRepository(session)
    bus = EventBus()                       # um barramento por requisição, entrega síncrona
    assinante = AtualizarStatusAcomodacao(acomodacoes, reservas, relogio.hoje)
    for tipo in EVENTOS_QUE_ATUALIZAM_STATUS:
        bus.subscribe(tipo, assinante)
    return ReservaService(reservas, HospedeRepository(session), acomodacoes, bus, relogio)
