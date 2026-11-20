import { screen } from "@testing-library/react";
import { Route, Routes } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";
import { GESTAO, mockApi, RECEPCAO, renderApp } from "../test/utils";

const rotas = (
  <Routes>
    <Route path="/login" element={<p>tela de login</p>} />
    <Route path="/acesso-negado" element={<p>acesso negado</p>} />
    <Route path="/" element={<ProtectedRoute><p>área logada</p></ProtectedRoute>} />
    <Route path="/gestao" element={<ProtectedRoute perfis={["GESTAO"]}><p>só gestão</p></ProtectedRoute>} />
  </Routes>
);

describe("ProtectedRoute", () => {
  it("sem token vai para o login", async () => {
    mockApi({});
    renderApp(rotas, { rota: "/" });
    expect(await screen.findByText("tela de login")).toBeInTheDocument();
  });

  it("com sessão válida mostra a página", async () => {
    mockApi({ "GET /auth/me": { body: RECEPCAO } });
    renderApp(rotas, { rota: "/", logado: RECEPCAO });
    expect(await screen.findByText("área logada")).toBeInTheDocument();
  });

  it("perfil sem permissão cai em acesso negado", async () => {
    mockApi({ "GET /auth/me": { body: RECEPCAO } });
    renderApp(rotas, { rota: "/gestao", logado: RECEPCAO });
    expect(await screen.findByText("acesso negado")).toBeInTheDocument();
  });

  it("gestão entra na rota de gestão", async () => {
    mockApi({ "GET /auth/me": { body: GESTAO } });
    renderApp(rotas, { rota: "/gestao", logado: GESTAO });
    expect(await screen.findByText("só gestão")).toBeInTheDocument();
  });

  it("token rejeitado pela API volta ao login", async () => {
    mockApi({ "GET /auth/me": { status: 401, body: { erro: "Sessão expirada" } } });
    renderApp(rotas, { rota: "/", logado: RECEPCAO });
    expect(await screen.findByText("tela de login")).toBeInTheDocument();
  });
});
