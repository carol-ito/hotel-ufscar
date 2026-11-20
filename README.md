# Hotel UFSCar

Sistema de reservas do hotel (GPQS). Módulos implementados: **Cadastros** (hóspedes, acomodações, categorias, características, login) e **Reservas e Disponibilidade**.

## Stack
- Backend: FastAPI, SQLAlchemy 2, PostgreSQL 16 (`btree_gist` + EXCLUDE GiST contra overbooking)
- Frontend: React 18, TypeScript, Vite, React Query
- Infra: Docker Compose (local), GitHub Actions (CI)

## Rodar tudo com Docker
```powershell
copy .env.example .env
docker compose up --build
```
- Frontend: http://localhost:5173
- API: http://localhost:8000/docs
- Logins de teste: `gestao@hotel.local` / `recepcao@hotel.local`, senha `senha123`

Para recriar o banco do zero: `docker compose down -v` e suba de novo.

## Testes
```powershell
# backend (precisa de um Postgres 16 com o banco hotel_test)
cd backend
pip install -r requirements-dev.txt
pytest --cov=app

# frontend
cd frontend
npm install
npm test
```

## Estrutura
```
backend/   app/{controllers,services,repositories,models,dtos,domain,activities,core}, tests/
frontend/  src/{api,auth,components,hooks,lib,pages,test}
db/        schema.sql, seed.sql
.github/workflows/ci.yml
```

## Nomes por padrão de projeto
Arquivos seguem o papel: `controllers/reservaController.py`, `services/reservaService.py`, `repositories/reservaRepository.py`,
`models/reservaModel.py`, `dtos/reservaDTO.py`, `domain/reservaFactory.py` (Factory), `domain/reservaState.py` (State),
`domain/reservaObserver.py` (Observer/EventBus) e, no front, `api/apiGateway.ts` (Gateway).

## Convenção dos testes
- **Unitários** (`backend/tests/unit/`): subpastas espelham `app/` (`controllers/`, `services/`, `repositories/`, `domain/`, `dtos/`, `core/`); um arquivo por classe de produção, `<classe>Test.py` com a classe `<Classe>Test`
  (ex.: `reservaServiceTest.py`, `acomodacaoControllerTest.py`, `eventBusTest.py`). Sem banco e sem HTTP.
- **Integração** (`backend/tests/integration/`): os testes ficam em `<api>Tests.py` (`reservaTests.py`), usando PostgreSQL de verdade.
  Eles chamam as classes `<api>Activity` de `backend/app/activities/` (`reservaActivity.py`), que escondem as rotas HTTP.
- Rodar só um grupo: `pytest tests/unit` ou `pytest tests/integration`.

## Variáveis de ambiente
| Variável | Onde | Descrição |
|---|---|---|
| `DATABASE_URL` | api | URL do Postgres (aceita `postgres://` e `postgresql://`) |
| `JWT_SECRET` | api | Segredo do token, 32+ caracteres |
| `CORS_ORIGINS` | api | Origens permitidas, separadas por vírgula |
| `JWT_EXPIRE_MINUTES` | api | Validade do token (padrão 60) |
| `HOTEL_TIMEZONE` | api | Padrão `America/Sao_Paulo` |
| `VITE_API_URL` | frontend | URL pública da API |
