import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import type { MapaLinha, ReservaMapa } from "../api/types";
import Alerta from "../components/Alerta";
import Campo from "../components/Campo";
import DateRangePicker from "../components/DateRangePicker";
import StatusBadge from "../components/StatusBadge";
import Tabela from "../components/Tabela";
import { BuscaDisponibilidade, useCategorias, useDisponibilidade, useMapa } from "../hooks/useAcomodacoes";
import { addDias, diaDaSemana, hojeISO, noitesEntre, periodoValido } from "../lib/datas";
import { mensagemErro } from "../lib/erros";
import { dataBR, moeda } from "../lib/format";

export default function Disponibilidade() {
  const [aba, setAba] = useState<"consulta" | "mapa">("consulta");
  return (
    <section>
      <header className="topo"><div><h1>Disponibilidade</h1><p className="sub">Quartos livres por período e mapa de ocupação.</p></div></header>
      <div className="abas" role="tablist">
        <button role="tab" type="button" aria-selected={aba === "consulta"} className={aba === "consulta" ? "aba ativa" : "aba"} onClick={() => setAba("consulta")}>Consultar período</button>
        <button role="tab" type="button" aria-selected={aba === "mapa"} className={aba === "mapa" ? "aba ativa" : "aba"} onClick={() => setAba("mapa")}>Mapa de ocupação</button>
      </div>
      {aba === "consulta" ? <Consulta /> : <Mapa />}
    </section>
  );
}

function Consulta() {
  const navegar = useNavigate();
  const categorias = useCategorias();
  const hoje = hojeISO();
  const [entrada, setEntrada] = useState(hoje);
  const [saida, setSaida] = useState(addDias(hoje, 1));
  const [hospedes, setHospedes] = useState("2");
  const [categoria, setCategoria] = useState("");
  const [busca, setBusca] = useState<BuscaDisponibilidade | null>(null);
  const { data, isFetching, error } = useDisponibilidade(busca);
  const podeBuscar = periodoValido(entrada, saida) && entrada >= hoje && Number(hospedes) >= 1;

  function consultar(e: React.FormEvent) {
    e.preventDefault();
    if (!podeBuscar) return;
    setBusca({ entrada, saida, hospedes: Number(hospedes), categoria_id: categoria ? Number(categoria) : undefined });
  }

  return (
    <>
      <form className="filtros filtros-consulta" onSubmit={consultar}>
        <DateRangePicker entrada={entrada} saida={saida} aoMudar={(e, s) => { setEntrada(e); setSaida(s); }} />
        <Campo rotulo="Hóspedes">{(id) => <input id={id} type="number" min={1} max={20} value={hospedes} onChange={(e) => setHospedes(e.target.value)} />}</Campo>
        <Campo rotulo="Categoria">
          {(id) => (
            <select id={id} value={categoria} onChange={(e) => setCategoria(e.target.value)}>
              <option value="">Todas</option>
              {categorias.data?.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
            </select>
          )}
        </Campo>
        <button type="submit" className="btn btn-primario" disabled={!podeBuscar || isFetching}>{isFetching ? "Buscando…" : "Buscar"}</button>
      </form>

      {error && <Alerta>{mensagemErro(error)}</Alerta>}
      {busca && data && (
        <>
          <p className="resumo" role="status">
            {data.length === 0
              ? "Nenhuma acomodação livre nesse período. Tente outras datas ou menos hóspedes."
              : `${data.length} ${data.length === 1 ? "acomodação livre" : "acomodações livres"} de ${dataBR(busca.entrada)} a ${dataBR(busca.saida)}.`}
          </p>
          {data.length > 0 && (
            <Tabela legenda="Acomodações disponíveis" itens={data} chave={(d) => d.acomodacao.id}
              colunas={[
                { cabecalho: "Nº", celula: (d) => <strong>{d.acomodacao.numero}</strong> },
                { cabecalho: "Categoria", celula: (d) => d.acomodacao.categoria.nome },
                { cabecalho: "Capacidade", celula: (d) => d.acomodacao.capacidade },
                { cabecalho: "Características", celula: (d) => <span className="chips">{d.acomodacao.caracteristicas.map((c) => <span key={c.id} className="chip">{c.nome}</span>)}</span> },
                { cabecalho: "Diária", classe: "num", celula: (d) => moeda(d.acomodacao.valor_diaria) },
                { cabecalho: `Total`, classe: "num", celula: (d) => <><strong>{moeda(d.valor_total)}</strong><small className="sub"> · {d.noites} {d.noites === 1 ? "noite" : "noites"}</small></> },
                { cabecalho: "Ação", celula: (d) => (
                  <button type="button" className="btn btn-pequeno btn-primario"
                    onClick={() => navegar(`/reservas/nova?acomodacao=${d.acomodacao.id}&entrada=${busca.entrada}&saida=${busca.saida}&hospedes=${busca.hospedes}`)}>
                    Reservar
                  </button>
                ) },
              ]} />
          )}
        </>
      )}
    </>
  );
}

const LARGURA_DIAS = [14, 30, 60];

function Mapa() {
  const [ini, setIni] = useState(hojeISO());
  const [dias, setDias] = useState(14);
  const fim = addDias(ini, dias);
  const { data, isLoading, error } = useMapa(ini, fim);
  const colunas = useMemo(() => Array.from({ length: dias }, (_, i) => addDias(ini, i)), [ini, dias]);

  return (
    <>
      <div className="filtros">
        <Campo rotulo="A partir de">{(id) => <input id={id} type="date" value={ini} onChange={(e) => e.target.value && setIni(e.target.value)} />}</Campo>
        <Campo rotulo="Janela">
          {(id) => (
            <select id={id} value={dias} onChange={(e) => setDias(Number(e.target.value))}>
              {LARGURA_DIAS.map((d) => <option key={d} value={d}>{d} dias</option>)}
            </select>
          )}
        </Campo>
        <ul className="legenda" aria-label="Legenda">
          <li><StatusBadge status="PENDENTE" /></li><li><StatusBadge status="CONFIRMADA" /></li><li><StatusBadge status="EM_ANDAMENTO" /></li>
        </ul>
      </div>
      {error && <Alerta>{mensagemErro(error)}</Alerta>}
      {isLoading && <p className="carregando">Carregando mapa…</p>}
      {data && (
        <div className="mapa-wrap">
          <table className="mapa">
            <caption className="sr-only">Mapa de ocupação de {dataBR(ini)} a {dataBR(fim)}</caption>
            <thead>
              <tr>
                <th scope="col" className="mapa-quarto">Quarto</th>
                {colunas.map((d) => (
                  <th key={d} scope="col" className={`mapa-dia${["sáb", "dom"].includes(diaDaSemana(d)) ? " fds" : ""}`}>
                    <span>{d.slice(8)}</span><small>{diaDaSemana(d)}</small>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>{data.map((linha) => <LinhaMapa key={linha.acomodacao.id} linha={linha} ini={ini} fim={fim} dias={dias} />)}</tbody>
          </table>
        </div>
      )}
      <p className="dica">A saída conta como dia livre: um hóspede que sai no dia 15 libera o quarto para uma entrada no dia 15.</p>
    </>
  );
}

function LinhaMapa({ linha, ini, fim, dias }: { linha: MapaLinha; ini: string; fim: string; dias: number }) {
  const celulas: JSX.Element[] = [];
  let cursor = 0;
  const reservas: ReservaMapa[] = [...linha.reservas].sort((a, b) => a.data_entrada.localeCompare(b.data_entrada));
  for (const r of reservas) {
    const de = r.data_entrada < ini ? ini : r.data_entrada;     // recorta ao que aparece na janela
    const ate = r.data_saida > fim ? fim : r.data_saida;
    const inicio = noitesEntre(ini, de);
    const span = noitesEntre(de, ate);
    if (span <= 0 || inicio < cursor) continue;
    for (; cursor < inicio; cursor++) celulas.push(<td key={`v${cursor}`} className="mapa-cel" />);
    celulas.push(
      <td key={`r${r.id}`} colSpan={span} className={`mapa-cel mapa-res res-${r.status.toLowerCase().replace(/_/g, "-")}`}>
        <Link to={`/reservas/${r.id}`} title={`${r.hospede_nome} · ${dataBR(r.data_entrada)} a ${dataBR(r.data_saida)}`}>{span > 1 ? r.hospede_nome : "·"}</Link>
      </td>);
    cursor += span;
  }
  for (; cursor < dias; cursor++) celulas.push(<td key={`v${cursor}`} className="mapa-cel" />);
  return <tr><th scope="row" className="mapa-quarto">{linha.acomodacao.numero}</th>{celulas}</tr>;
}
