import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/apiGateway";
import type { NovaReserva, Pagina, Reserva } from "../api/types";

export interface FiltroReservas { status: string; entrada_de: string; entrada_ate: string; hospede_id?: number }

export function useReservas(filtro: FiltroReservas, offset: number, limite = 10) {
  return useQuery({
    queryKey: ["reservas", filtro, offset, limite],
    queryFn: () => api<Pagina<Reserva>>("/reservas", { params: { ...filtro, offset, limite } }),
    placeholderData: keepPreviousData,
  });
}

export const useReserva = (id: number) =>
  useQuery({ queryKey: ["reserva", id], queryFn: () => api<Reserva>(`/reservas/${id}`) });

/** Reserva mexe em disponibilidade, mapa e status do quarto: invalida tudo que depende disso. */
function useInvalidarTudo() {
  const qc = useQueryClient();
  return () => Promise.all(["reservas", "reserva", "disponibilidade", "mapa", "acomodacoes"]
    .map((k) => qc.invalidateQueries({ queryKey: [k] })));
}

export function useCriarReserva() {
  const invalidar = useInvalidarTudo();
  return useMutation({
    mutationFn: (dados: NovaReserva) => api<Reserva>("/reservas", { method: "POST", body: dados }),
    onSettled: invalidar,     // também em erro 409: a lista de livres mudou
  });
}

export function useAcaoReserva(id: number) {
  const invalidar = useInvalidarTudo();
  return useMutation({
    mutationFn: (acao:
      | { tipo: "confirmar" }
      | { tipo: "cancelar"; motivo: string }
      | { tipo: "alterar"; data_entrada: string; data_saida: string; qtd_hospedes: number }) => {
      if (acao.tipo === "confirmar") return api<Reserva>(`/reservas/${id}/confirmar`, { method: "POST" });
      if (acao.tipo === "cancelar") return api<Reserva>(`/reservas/${id}/cancelar`, { method: "POST", body: { motivo: acao.motivo } });
      const { tipo: _tipo, ...dados } = acao;
      return api<Reserva>(`/reservas/${id}`, { method: "PUT", body: dados });
    },
    onSettled: invalidar,
  });
}
