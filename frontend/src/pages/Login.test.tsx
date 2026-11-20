import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import Login from "./Login";
import { GESTAO, mockApi, renderApp } from "../test/utils";

const rotas = <Routes><Route path="/login" element={<Login />} /><Route path="/reservas" element={<p>reservas</p>} /></Routes>;

describe("Login", () => {
  it("entra e vai para as reservas", async () => {
    const { chamadas } = mockApi({ "POST /auth/login": { body: { access_token: "t", token_type: "bearer", expires_in: 3600, usuario: GESTAO } } });
    renderApp(rotas, { rota: "/login" });
    await userEvent.type(screen.getByLabelText("E-mail"), "g@h.local");
    await userEvent.type(screen.getByLabelText("Senha"), "senha123");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));
    expect(await screen.findByText("reservas")).toBeInTheDocument();
    expect(chamadas[0].corpo).toEqual({ email: "g@h.local", senha: "senha123" });
    expect(sessionStorage.getItem("hotel.token")).toBe("t");
  });

  it("mostra erro de credencial", async () => {
    mockApi({ "POST /auth/login": { status: 401, body: { erro: "E-mail ou senha inválidos" } } });
    renderApp(rotas, { rota: "/login" });
    await userEvent.type(screen.getByLabelText("E-mail"), "x@y.z");
    await userEvent.type(screen.getByLabelText("Senha"), "errada");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("E-mail ou senha inválidos");
  });

  it("mostra e oculta a senha", async () => {
    mockApi({});
    renderApp(rotas, { rota: "/login" });
    const campo = screen.getByLabelText("Senha");
    expect(campo).toHaveAttribute("type", "password");
    await userEvent.click(screen.getByRole("button", { name: "Mostrar senha" }));
    expect(campo).toHaveAttribute("type", "text");
    await userEvent.click(screen.getByRole("button", { name: "Ocultar senha" }));
    expect(campo).toHaveAttribute("type", "password");
  });

  it("limpa a senha depois de uma tentativa errada, mas mantém o e-mail", async () => {
    mockApi({ "POST /auth/login": { status: 401, body: { erro: "E-mail ou senha inválidos" } } });
    renderApp(rotas, { rota: "/login" });
    await userEvent.type(screen.getByLabelText("E-mail"), "x@y.z");
    await userEvent.type(screen.getByLabelText("Senha"), "errada");
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }));
    await screen.findByRole("alert");
    expect(screen.getByLabelText("Senha")).toHaveValue("");
    expect(screen.getByLabelText("E-mail")).toHaveValue("x@y.z");
  });
});
