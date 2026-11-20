import { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import type { Perfil } from "../api/types";
import { useAuth } from "./AuthContext";

interface Props { perfis?: Perfil[]; children: ReactNode }

/** Sem sessão → login; perfil errado → acesso negado. É conveniência de interface:
 *  quem garante a regra é a API (403). */
export default function ProtectedRoute({ perfis, children }: Props) {
  const { usuario, carregando, tem } = useAuth();
  const local = useLocation();
  if (carregando) return <p className="carregando" role="status">Carregando…</p>;
  if (!usuario) return <Navigate to="/login" replace state={{ de: local.pathname + local.search }} />;
  if (perfis && !tem(...perfis)) return <Navigate to="/acesso-negado" replace />;
  return <>{children}</>;
}
