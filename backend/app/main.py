from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.controllers import (acomodacaoController, authController, catalogoController, disponibilidadeController,
                             hospedeController, reservaController)
from app.core.config import get_settings
from app.core.database import get_engine
from app.core.errors import DominioError


def _mensagem_validacao(erros: list[dict]) -> str:
    partes = []
    for e in erros:
        campo = ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path"))
        msg = e["msg"].removeprefix("Value error, ")
        partes.append(f"{campo}: {msg}" if campo else msg)
    return "; ".join(partes)


def create_app() -> FastAPI:
    app = FastAPI(title="Hotel UFSCar — API", version="0.3.0")
    app.add_middleware(CORSMiddleware, allow_origins=get_settings().cors_origins,
                       allow_methods=["*"], allow_headers=["*"])

    @app.exception_handler(DominioError)
    async def _dominio(_: Request, erro: DominioError):
        return JSONResponse(status_code=erro.status_code, content={"erro": erro.mensagem})

    @app.exception_handler(RequestValidationError)
    async def _validacao(_: Request, erro: RequestValidationError):
        erros = erro.errors()
        return JSONResponse(status_code=422, content={
            "erro": _mensagem_validacao(erros),
            "campos": {".".join(str(p) for p in e["loc"][1:]): e["msg"].removeprefix("Value error, ")
                       for e in erros if len(e["loc"]) > 1}})

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, erro: StarletteHTTPException):
        return JSONResponse(status_code=erro.status_code, content={"erro": str(erro.detail)})

    @app.get("/health", tags=["Infra"])
    def health():
        return {"status": "ok"}

    @app.get("/health/db", tags=["Infra"])
    def health_db():
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "banco": "conectado"}

    for modulo in (authController, hospedeController, catalogoController, acomodacaoController,
                   disponibilidadeController, reservaController):
        app.include_router(modulo.router)
    return app


app = create_app()
