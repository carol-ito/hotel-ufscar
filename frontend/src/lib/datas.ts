/** Datas da UI são sempre strings ISO "AAAA-MM-DD" (o mesmo formato da API). */
export function hojeISO(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function paraUTC(iso: string): number {
  const [a, m, d] = iso.split("-").map(Number);
  return Date.UTC(a, m - 1, d);
}

export function addDias(iso: string, dias: number): string {
  return new Date(paraUTC(iso) + dias * 86_400_000).toISOString().slice(0, 10);
}

/** Noites entre entrada (inclusive) e saída (exclusive). */
export function noitesEntre(entrada: string, saida: string): number {
  return Math.round((paraUTC(saida) - paraUTC(entrada)) / 86_400_000);
}

export function periodoValido(entrada: string, saida: string): boolean {
  return Boolean(entrada && saida) && noitesEntre(entrada, saida) > 0;
}

const SEMANA = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];
export const diaDaSemana = (iso: string) => SEMANA[new Date(paraUTC(iso)).getUTCDay()];
