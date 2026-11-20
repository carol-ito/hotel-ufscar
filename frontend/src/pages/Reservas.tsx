import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Alerta from "../components/Alerta";
import Campo from "../components/Campo";
import Paginacao from "../components/Paginacao";
import StatusBadge from "../components/StatusBadge";
import Tabela from "../components/Tabela";
import { useReservas } from "../hooks/useReservas";
import { mensagemErro } from "../lib/erros";
import { dataBR, moeda } from "../lib/format";

const LIMITE = 10;
const STATUS = ["PENDENTE", "CONFIRMADA", "EM_ANDAMENTO", "ENCERRADA", "CANCELADA"];

export default function Reservas() {
  const navegar = useNavigate();
  const [status, setStatus] = useState("");
  const [de, setDe] = useState("");
  const [ate, setAte] = useState("");
  const [offset, setOffset] = useState(0);
  const { data, isLoading, error } = useReservas({ status, entrada_de: de, entrada_ate: ate }, offset, LIMITE);
  const mudar = (fn: () => void) => { fn(); setOffset(0); };

  return (
    <section>
      <header className="topo">
        <div><h1>Reservas</h1><p className="sub">Da mais próxima entrada para a mais antiga.</p></div>
        <Link to="/reservas/nova" className="btn btn-primario">Nova reserva</Link>
      </header>
      <div className="filtros">
        <Campo rotulo="Status">
          {(id) => (
            <select id={id} value={status} onChange={(e) => mudar(() => setStatus(e.target.value))}>
              <option value="">Todos</option>
              {STATUS.map((s) => <option key={s} value={s}>{s === "EM_ANDAMENTO" ? "Em andamento" : s[0] + s.slice(1).toLowerCase()}</option>)}
            </select>
          )}
        </Campo>
        <Campo rotulo="Entrada de">{(id) => <input id={id} type="date" value={de} onChange={(e) => mudar(() => setDe(e.target.value))} />}</Campo>
        <Campo rotulo="Entrada até">{(id) => <input id={id} type="date" value={ate} min={de || undefined} onChange={(e) => mudar(() => setAte(e.target.value))} />}</Campo>
        {(status || de || ate) && <button type="button" className="btn btn-pequeno" onClick={() => mudar(() => { setStatus(""); setDe(""); setAte(""); })}>Limpar filtros</button>}
      </div>
      {error && <Alerta>{mensagemErro(error)}</Alerta>}
      <Tabela legenda="Lista de reservas" carregando={isLoading} itens={data?.itens} chave={(r) => r.id}
        vazio="Nenhuma reserva com esses filtros." aoClicar={(r) => navegar(`/reservas/${r.id}`)}
        colunas={[
          { cabecalho: "Nº", celula: (r) => `#${r.id}` },
          { cabecalho: "Hóspede", celula: (r) => <Link to={`/reservas/${r.id}`}><strong>{r.hospede.nome}</strong></Link> },
          { cabecalho: "Quarto", celula: (r) => r.acomodacao.numero },
          { cabecalho: "Período", celula: (r) => `${dataBR(r.data_entrada)} → ${dataBR(r.data_saida)}` },
          { cabecalho: "Noites", classe: "num", celula: (r) => r.noites },
          { cabecalho: "Total", classe: "num", celula: (r) => moeda(r.valor_total) },
          { cabecalho: "Status", celula: (r) => <StatusBadge status={r.status} /> },
        ]} />
      {data && <Paginacao total={data.total} limite={LIMITE} offset={offset} aoMudar={setOffset} />}
    </section>
  );
}
