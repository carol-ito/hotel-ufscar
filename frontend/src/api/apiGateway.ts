/** Gateway: o único lugar que chama fetch. Injeta o token, converte {"erro"} em exceção
 *  e leva o usuário ao login quando a API responde 401. */
const BASE = (import.meta.env.VITE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
const CHAVE = "hotel.token";

export class ApiError extends Error {
  constructor(public status: number, message: string, public campos: Record<string, string> = {}) {
    super(message);
    this.name = "ApiError";
  }
}

export const tokenStore = {
  get(): string | null {
    try { return sessionStorage.getItem(CHAVE); } catch { return null; }
  },
  set(token: string) {
    try { sessionStorage.setItem(CHAVE, token); } catch { /* armazenamento indisponível: sessão só em memória */ }
  },
  clear() {
    try { sessionStorage.removeItem(CHAVE); } catch { /* ignora */ }
  },
};

let aoExpirar: () => void = () => {};
export function onNaoAutenticado(handler: () => void) { aoExpirar = handler; }

type Params = Record<string, string | number | boolean | null | undefined>;
interface Opcoes { method?: string; body?: unknown; params?: Params; semToken?: boolean }

export async function api<T>(caminho: string, { method = "GET", body, params, semToken }: Opcoes = {}): Promise<T> {
  const url = new URL(BASE + caminho);
  Object.entries(params ?? {}).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, String(v));
  });
  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = tokenStore.get();
  if (token && !semToken) headers.Authorization = `Bearer ${token}`;

  let resposta: Response;
  try {
    resposta = await fetch(url.toString(), { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  } catch {
    throw new ApiError(0, "Não foi possível falar com o servidor. Verifique sua conexão ou tente novamente.");
  }

  if (resposta.status === 204) return undefined as T;
  const texto = await resposta.text();
  let json: unknown = null;
  try { json = texto ? JSON.parse(texto) : null; } catch { /* resposta sem JSON */ }

  if (!resposta.ok) {
    const corpo = (json ?? {}) as { erro?: string; campos?: Record<string, string> };
    if (resposta.status === 401 && !semToken) aoExpirar();
    throw new ApiError(resposta.status, corpo.erro ?? `Erro ${resposta.status}`, corpo.campos);
  }
  return json as T;
}
