import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/apiGateway";
import type { Hospede, HospedeForm, Pagina } from "../api/types";

export function payloadHospede(f: HospedeForm) {
  return {
    nome: f.nome.trim(), documento_tipo: f.documento_tipo, documento_numero: f.documento_numero.trim(),
    email: f.email.trim() || null, telefone: f.telefone.trim() || null,
  };
}

export function useHospedes(q: string, offset: number, limite = 10) {
  return useQuery({
    queryKey: ["hospedes", q, offset, limite],
    queryFn: () => api<Pagina<Hospede>>("/hospedes", { params: { q, offset, limite } }),
    placeholderData: keepPreviousData,
  });
}

export function useSalvarHospede() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, dados }: { id?: number; dados: HospedeForm }) =>
      id
        ? api<Hospede>(`/hospedes/${id}`, { method: "PUT", body: payloadHospede(dados) })
        : api<Hospede>("/hospedes", { method: "POST", body: payloadHospede(dados) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["hospedes"] }),
  });
}
