import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import get_engine
from app.core.dependencies import get_relogio
from app.core.security import gerar_hash
from app.main import create_app
from tests.conftest import SCHEMA, RelogioFixo
from app.activities.acomodacaoActivity import AcomodacaoActivity
from app.activities.authActivity import AuthActivity
from app.activities.catalogoActivity import CatalogoActivity
from app.activities.disponibilidadeActivity import DisponibilidadeActivity
from app.activities.hospedeActivity import HospedeActivity, dados_hospede
from app.activities.reservaActivity import ReservaActivity
from app.activities.saudeActivity import SaudeActivity

SENHA = "senha123"
HASH_SENHA = gerar_hash(SENHA)   # bcrypt é lento de propósito: calcula uma vez só


@pytest.fixture(scope="session", autouse=True)
def banco():
    """Recria o banco de teste a partir do schema.sql (uma vez por sessão de testes)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute(SCHEMA.read_text(encoding="utf-8"))
        raw.commit()
    finally:
        raw.close()
    yield engine


@pytest.fixture(autouse=True)
def dados_base(banco):
    """Estado conhecido antes de cada teste: 2 usuários, 2 categorias, 3 acomodações."""
    hash_ = HASH_SENHA
    with banco.begin() as conn:
        conn.execute(text("TRUNCATE pagamento, lancamento_servico, reserva, acomodacao_caracteristica, "
                          "acomodacao, caracteristica, categoria_acomodacao, hospede, servico, usuario "
                          "RESTART IDENTITY CASCADE"))
        conn.execute(text("INSERT INTO usuario (nome, email, senha_hash, perfil) VALUES "
                          "('Gestora', 'gestao@hotel.test', :h, 'GESTAO'), "
                          "('Recepção', 'recepcao@hotel.test', :h, 'RECEPCAO')"), {"h": hash_})
        conn.execute(text("INSERT INTO categoria_acomodacao (nome) VALUES ('Standard'), ('Luxo')"))
        conn.execute(text("INSERT INTO caracteristica (nome) VALUES ('Ar-condicionado'), ('Frigobar')"))
        conn.execute(text("INSERT INTO acomodacao (numero, categoria_id, capacidade, valor_diaria) VALUES "
                          "('101', 1, 2, 150.00), ('102', 1, 3, 180.00), ('201', 2, 4, 320.00)"))


@pytest.fixture
def client():
    app = create_app()
    app.dependency_overrides[get_relogio] = lambda: RelogioFixo()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_api(client):
    return AuthActivity(client)


@pytest.fixture
def gestao(auth_api):
    return auth_api.cabecalho_de("gestao@hotel.test")


@pytest.fixture
def recepcao(auth_api):
    return auth_api.cabecalho_de("recepcao@hotel.test")


# Activities já autenticadas como Recepção; use .como(gestao) quando o teste for de Gestão
@pytest.fixture
def hospede_api(client, recepcao):
    return HospedeActivity(client, recepcao)


@pytest.fixture
def catalogo_api(client, recepcao):
    return CatalogoActivity(client, recepcao)


@pytest.fixture
def acomodacao_api(client, recepcao):
    return AcomodacaoActivity(client, recepcao)


@pytest.fixture
def disponibilidade_api(client, recepcao):
    return DisponibilidadeActivity(client, recepcao)


@pytest.fixture
def reserva_api(client, recepcao):
    return ReservaActivity(client, recepcao)


@pytest.fixture
def saude_api(client):
    return SaudeActivity(client)


@pytest.fixture
def hospede(hospede_api):
    """Um hóspede já cadastrado (dict da resposta)."""
    r = hospede_api.criar(dados_hospede(nome="Maria Souza", email="maria@exemplo.com"))
    assert r.status_code == 201, r.text
    return r.json()
