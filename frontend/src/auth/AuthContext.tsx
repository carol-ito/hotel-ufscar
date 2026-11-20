import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { api, onNaoAutenticado, tokenStore } from "../api/apiGateway";
import type { Perfil, Token, Usuario } from "../api/types";

interface AuthValor {
  usuario: Usuario | null;
  carregando: boolean;
  aviso: string | null;
  entrar(email: string, senha: string): Promise<void>;
  sair(aviso?: string): void;
  tem(...perfis: Perfil[]): boolean;
}

const Ctx = createContext<AuthValor | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState<boolean>(() => tokenStore.get() !== null);
  const [aviso, setAviso] = useState<string | null>(null);

  const sair = useCallback((mensagem?: string) => {
    tokenStore.clear();
    setUsuario(null);
    setAviso(mensagem ?? null);
    queryClient.clear();     // nada de dados da sessão anterior na tela do próximo usuário
  }, [queryClient]);

  // token curto, sem refresh: ao expirar a API devolve 401 e o usuário volta ao login
  useEffect(() => onNaoAutenticado(() => sair("Sua sessão expirou. Entre novamente.")), [sair]);

  useEffect(() => {
    if (tokenStore.get() === null) return;
    api<Usuario>("/auth/me")
      .then(setUsuario)
      .catch(() => tokenStore.clear())
      .finally(() => setCarregando(false));
  }, []);

  const entrar = useCallback(async (email: string, senha: string) => {
    const t = await api<Token>("/auth/login", { method: "POST", body: { email, senha }, semToken: true });
    tokenStore.set(t.access_token);
    setAviso(null);
    setUsuario(t.usuario);
  }, []);

  const valor = useMemo<AuthValor>(() => ({
    usuario, carregando, aviso, entrar, sair,
    tem: (...perfis) => usuario !== null && perfis.includes(usuario.perfil),
  }), [usuario, carregando, aviso, entrar, sair]);

  return <Ctx.Provider value={valor}>{children}</Ctx.Provider>;
}

export function useAuth(): AuthValor {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth fora do AuthProvider");
  return v;
}
