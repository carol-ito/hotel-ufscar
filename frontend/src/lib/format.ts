const brl = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export const moeda = (valor: string | number) => brl.format(Number(valor));

/** "2026-12-10" → "10/12/2026" (sem passar por Date, para não deslocar o dia pelo fuso). */
export function dataBR(iso: string | null | undefined): string {
  if (!iso) return "—";
  const [a, m, d] = iso.slice(0, 10).split("-");
  return `${d}/${m}/${a}`;
}

export function dataHoraBR(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

export function documentoBR(tipo: string, numero: string): string {
  if (tipo === "CPF" && /^\d{11}$/.test(numero)) {
    return `${numero.slice(0, 3)}.${numero.slice(3, 6)}.${numero.slice(6, 9)}-${numero.slice(9)}`;
  }
  return `${tipo} ${numero}`;
}

export const ROTULO_STATUS: Record<string, string> = {
  PENDENTE: "Pendente", CONFIRMADA: "Confirmada", EM_ANDAMENTO: "Em andamento",
  ENCERRADA: "Encerrada", CANCELADA: "Cancelada",
  LIVRE: "Livre", RESERVADO: "Reservado", OCUPADO: "Ocupado",
};
