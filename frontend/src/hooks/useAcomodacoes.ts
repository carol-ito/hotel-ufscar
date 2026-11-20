import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/apiGateway";
import type { Acomodacao, AcomodacaoForm, Caracteristica, Categoria, Disponivel, MapaLinha } from "../api/types";
import { periodoValido } from "../lib/datas";

export const useAcomodacoes = () =>
  useQuery({ queryKey: ["acomodacoes"], queryFn: () => api<Acomodacao[]>("/acomodacoes") });

export const useCategorias = () =>
  useQuery({ queryKey: ["categorias"], queryFn: () => api<Categoria[]>("/categorias"), staleTime: 60_000 });

export const useCaracteristicas = () =>
  useQuery({ queryKey: ["caracteristicas"], queryFn: () => api<Caracteristica[]>("/caracteristicas"), staleTime: 60_000 });

export function useSalvarAcomodacao() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, dados }: { id?: number; dados: AcomodacaoForm }) =>
      id
        ? api<Acomodacao>(`/acomodacoes/${id}`, { method: "PUT", body: dados })
        : api<Acomodacao>("/acomodacoes", { method: "POST", body: dados }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["acomodacoes"] }),
  });
}

export function useDefinirAtivo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ativo }: { id: number; ativo: boolean }) =>
      api<Acomodacao>(`/acomodacoes/${id}/ativo`, { method: "PATCH", body: { ativo } }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["acomodacoes"] }),
  });
}

export function useSalvarCatalogo(tipo: "categorias" | "caracteristicas") {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, dados }: { id?: number; dados: { nome: string; descricao?: string | null } }) =>
      api(id ? `/${tipo}/${id}` : `/${tipo}`, { method: id ? "PUT" : "POST", body: dados }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [tipo] });
      qc.invalidateQueries({ queryKey: ["acomodacoes"] });
    },
  });
}

export interface BuscaDisponibilidade { entrada: string; saida: string; hospedes: number; categoria_id?: number }

export function useDisponibilidade(busca: BuscaDisponibilidade | null) {
  const ativo = busca !== null && periodoValido(busca.entrada, busca.saida) && busca.hospedes >= 1;
  return useQuery({
    queryKey: ["disponibilidade", busca],
    queryFn: () => api<Disponivel[]>("/acomodacoes/disponiveis", { params: { ...busca } }),
    enabled: ativo,
  });
}

export const useMapa = (ini: string, fim: string) =>
  useQuery({
    queryKey: ["mapa", ini, fim],
    queryFn: () => api<MapaLinha[]>("/disponibilidade/mapa", { params: { ini, fim } }),
    enabled: periodoValido(ini, fim),
  });
