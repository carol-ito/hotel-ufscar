import { vi } from "vitest";
import { api, ApiError, onNaoAutenticado, tokenStore } from "./apiGateway";
import { mockApi } from "../test/utils";

describe("api gateway", () => {
  it("injeta o token e serializa query params ignorando vazios", async () => {
    tokenStore.set("abc");
    const { chamadas } = mockApi({ "GET /hospedes": { body: { itens: [] } } });
    await api("/hospedes", { params: { q: "ana", offset: 0, vazio: "", nulo: null } });
    expect(chamadas[0].caminho).toBe("/hospedes?q=ana&offset=0");
    expect(chamadas[0].headers.Authorization).toBe("Bearer abc");
  });

  it("converte {erro, campos} em ApiError", async () => {
    mockApi({ "POST /hospedes": { status: 422, body: { erro: "CPF inválido", campos: { documento_numero: "CPF inválido" } } } });
    const e = await api("/hospedes", { method: "POST", body: {} }).catch((x) => x);
    expect(e).toBeInstanceOf(ApiError);
    expect(e).toMatchObject({ status: 422, message: "CPF inválido", campos: { documento_numero: "CPF inválido" } });
  });

  it("401 avisa o handler de sessão expirada, mas não no login", async () => {
    const aviso = vi.fn();
    onNaoAutenticado(aviso);
    tokenStore.set("expirado");
    mockApi({ "GET /reservas": { status: 401, body: { erro: "Sessão expirada" } }, "POST /auth/login": { status: 401, body: { erro: "E-mail ou senha inválidos" } } });
    await expect(api("/reservas")).rejects.toThrow("Sessão expirada");
    expect(aviso).toHaveBeenCalledTimes(1);
    await expect(api("/auth/login", { method: "POST", body: {}, semToken: true })).rejects.toThrow("E-mail ou senha");
    expect(aviso).toHaveBeenCalledTimes(1);
  });

  it("erro de rede vira mensagem amigável", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("fail")));
    await expect(api("/x")).rejects.toMatchObject({ status: 0 });
  });
});
