import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { ReactElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";
import { tokenStore } from "../api/apiGateway";
import { AuthProvider } from "../auth/AuthContext";

type Resposta = { status?: number; body?: unknown };
type Rota = Resposta | ((init: RequestInit | undefined, url: URL) => Resposta);

/** Simula a API: chaves "METHOD /caminho". Rotas não mapeadas falham o teste de forma legível. */
export function mockApi(rotas: Record<string, Rota>) {
  const chamadas: { metodo: string; caminho: string; corpo: unknown; headers: Record<string, string> }[] = [];
  const fn = vi.fn(async (entrada: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(entrada));
    const metodo = init?.method ?? "GET";
    chamadas.push({ metodo, caminho: url.pathname + url.search, corpo: init?.body ? JSON.parse(String(init.body)) : undefined,
      headers: (init?.headers ?? {}) as Record<string, string> });
    const rota = rotas[`${metodo} ${url.pathname}`];
    if (!rota) throw new Error(`Rota não simulada: ${metodo} ${url.pathname}`);
    const r = typeof rota === "function" ? rota(init, url) : rota;
    const status = r.status ?? 200;
    return new Response(r.body === undefined ? null : JSON.stringify(r.body), { status });
  });
  vi.stubGlobal("fetch", fn);
  return { chamadas };
}

export const GESTAO = { id: 1, nome: "Gestora", email: "g@h.local", perfil: "GESTAO" as const };
export const RECEPCAO = { id: 2, nome: "Recepção", email: "r@h.local", perfil: "RECEPCAO" as const };

export function renderApp(ui: ReactElement, { rota = "/", logado }: { rota?: string; logado?: typeof GESTAO | typeof RECEPCAO } = {}) {
  if (logado) tokenStore.set("token-de-teste");
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[rota]}>
        <AuthProvider>{ui}</AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}
