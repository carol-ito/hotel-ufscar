import { addDias, hojeISO, noitesEntre, periodoValido } from "../lib/datas";
import Campo from "./Campo";

interface Props {
  entrada: string; saida: string; aoMudar(entrada: string, saida: string): void;
  permitirPassado?: boolean; rotuloEntrada?: string; rotuloSaida?: string;
}

/** Período semiaberto [entrada, saída): a saída no dia D libera o quarto para uma entrada no dia D. */
export default function DateRangePicker({ entrada, saida, aoMudar, permitirPassado, rotuloEntrada = "Entrada", rotuloSaida = "Saída" }: Props) {
  const hoje = hojeISO();
  const erroSaida = entrada && saida && !periodoValido(entrada, saida) ? "A saída deve ser depois da entrada" : undefined;
  const erroEntrada = !permitirPassado && entrada && entrada < hoje ? "A entrada não pode estar no passado" : undefined;
  const noites = periodoValido(entrada, saida) ? noitesEntre(entrada, saida) : 0;

  return (
    <div className="periodo">
      <Campo rotulo={rotuloEntrada} erro={erroEntrada}>
        {(id, desc) => (
          <input id={id} type="date" value={entrada} min={permitirPassado ? undefined : hoje} aria-describedby={desc}
            onChange={(e) => {
              const nova = e.target.value;
              // empurra a saída para o dia seguinte se ela ficaria antes da nova entrada
              aoMudar(nova, nova && saida && !periodoValido(nova, saida) ? addDias(nova, 1) : saida);
            }} />
        )}
      </Campo>
      <Campo rotulo={rotuloSaida} erro={erroSaida}>
        {(id, desc) => (
          <input id={id} type="date" value={saida} min={entrada ? addDias(entrada, 1) : undefined} aria-describedby={desc}
            onChange={(e) => aoMudar(entrada, e.target.value)} />
        )}
      </Campo>
      <p className="periodo-noites" aria-live="polite">{noites > 0 ? `${noites} ${noites === 1 ? "noite" : "noites"}` : ""}</p>
    </div>
  );
}
