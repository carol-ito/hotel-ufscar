import { ApiError } from "../api/apiGateway";

export function mensagemErro(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  return "Algo deu errado. Tente novamente.";
}
