import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import type { Hospede } from "../api/types";
import Alerta from "../components/Alerta";
import Campo from "../components/Campo";
import DateRangePicker from "../components/DateRangePicker";
import HospedeForm from "../components/HospedeForm";
import Modal from "../components/Modal";
import { useDisponibilidade } from "../hooks/useAcomodacoes";
import { useDebounce } from "../hooks/useDebounce";
import { useHospedes } from "../hooks/useHospedes";
import { useCriarReserva } from "../hooks/useReservas";
import { api } from "../api/apiGateway";
import { useQuery } from "@tanstack/react-query";
import { addDias, hojeISO, periodoValido } from "../lib/datas";
import { mensagemErro } from "../lib/erros";
import { documentoBR, moeda } from "../lib/format";

export default function ReservaNova() {
  const navegar = useNavigate();
  const [params] = useSearchParams();
  const hoje = hojeISO();
  const [entrada, setEntrada] = useState(params.get("entrada") ?? hoje);
  const [saida, setSaida] = useState(params.get("saida") ?? addDias(params.get("entrada") ?? hoje, 1));
  const [qtd, setQtd] = useState(params.get("hospedes") ?? "2");
  const [acomodacaoId, setAcomodacaoId] = useState<number | null>(params.get("acomodacao") ? Number(params.get("acomodacao")) : null);
  const [hospede, setHospede] = useState<Hospede | null>(null);
  const [cadastrando, setCadastrando] = useState(false);
  const [busca, setBusca] = useState("");
  const q = useDebounce(busca.trim(), 300);
  const criar = useCriarReserva();

  const hospedeInicial = params.get("hospede");
  const inicial = useQuery({
    queryKey: ["hospede", hospedeInicial],
    enabled: Boolean(hospedeInicial),
    queryFn: () => api<Hospede>(`/hospedes/${hospedeInicial}`),
  });
  // ?hospede=ID vem do botão "Nova reserva" da lista de hóspedes; só pré-seleciona uma vez
  useEffect(() => { if (inicial.data) setHospede((atual) => atual ?? inicial.data); }, [inicial.data]);

  const periodoOk = periodoValido(entrada, saida) && entrada >= hoje;
  const quantidade = Number(qtd);
  const livres = useDisponibilidade(periodoOk && quantidade >= 1 ? { entrada, saida, hospedes: quantidade } : null);
  const sugestoes = useHospedes(q, 0, 5);
  const escolhida = livres.data?.find((d) => d.acomodacao.id === acomodacaoId);
  const preenchidaIndisponivel = acomodacaoId !== null && livres.data && !escolhida;
  const pronto = Boolean(hospede && escolhida && periodoOk);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    if (!hospede || !escolhida) return;
    try {
      const r = await criar.mutateAsync({ hospede_id: hospede.id, acomodacao_id: escolhida.acomodacao.id, data_entrada: entrada, data_saida: saida, qtd_hospedes: quantidade });
      navegar(`/reservas/${r.id}`, { state: { aviso: "Reserva criada como pendente. Confirme para garantir o quarto." } });
    } catch { /* erro mostrado abaixo; a lista de livres é recarregada */ }
  }

  return (
    <section>
      <header className="topo"><div><h1>Nova reserva</h1><p className="sub">Escolha o período, o quarto e o hóspede.</p></div></header>
      <form className="form form-largo" onSubmit={enviar} noValidate>
        {criar.error && <Alerta>{mensagemErro(criar.error)}</Alerta>}

        <fieldset className="grupo">
          <legend>1. Período e hóspedes</legend>
          <div className="linha linha-periodo">
            <DateRangePicker entrada={entrada} saida={saida} aoMudar={(e, s) => { setEntrada(e); setSaida(s); }} />
            <Campo rotulo="Nº de hóspedes">{(id) => <input id={id} type="number" min={1} max={20} value={qtd} onChange={(e) => setQtd(e.target.value)} />}</Campo>
          </div>
        </fieldset>

        <fieldset className="grupo">
          <legend>2. Acomodação</legend>
          {!periodoOk && <p className="dica">Informe um período válido para ver os quartos livres.</p>}
          {livres.error && <Alerta>{mensagemErro(livres.error)}</Alerta>}
          {preenchidaIndisponivel && <Alerta tipo="info">O quarto escolhido antes não está livre nesse período. Escolha outro abaixo.</Alerta>}
          {livres.data?.length === 0 && <p className="dica">Nenhum quarto livre para {quantidade} hóspede(s) nesse período.</p>}
          <div className="opcoes">
            {livres.data?.map((d) => (
              <label key={d.acomodacao.id} className={`opcao${acomodacaoId === d.acomodacao.id ? " marcada" : ""}`}>
                <input type="radio" name="acomodacao" checked={acomodacaoId === d.acomodacao.id} onChange={() => setAcomodacaoId(d.acomodacao.id)} />
                <span className="opcao-titulo">Quarto {d.acomodacao.numero} · {d.acomodacao.categoria.nome}</span>
                <span className="opcao-sub">até {d.acomodacao.capacidade} hóspedes · {moeda(d.acomodacao.valor_diaria)}/noite</span>
                <span className="opcao-total">{moeda(d.valor_total)}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset className="grupo">
          <legend>3. Hóspede</legend>
          {hospede ? (
            <div className="selecionado">
              <div><strong>{hospede.nome}</strong><br /><small>{documentoBR(hospede.documento_tipo, hospede.documento_numero)}</small></div>
              <button type="button" className="btn btn-pequeno" onClick={() => setHospede(null)}>Trocar</button>
            </div>
          ) : (
            <>
              <div className="linha-busca">
                <Campo rotulo="Buscar hóspede">{(id) => <input id={id} type="search" placeholder="Nome ou documento" value={busca} onChange={(e) => setBusca(e.target.value)} />}</Campo>
                <button type="button" className="btn" onClick={() => setCadastrando(true)}>Cadastrar novo hóspede</button>
              </div>
              {q && sugestoes.data && (
                <ul className="sugestoes" aria-label="Hóspedes encontrados">
                  {sugestoes.data.itens.length === 0 && <li className="dica">Nenhum hóspede encontrado.</li>}
                  {sugestoes.data.itens.map((h) => (
                    <li key={h.id}><button type="button" onClick={() => { setHospede(h); setBusca(""); }}>
                      <strong>{h.nome}</strong> <small>{documentoBR(h.documento_tipo, h.documento_numero)}</small>
                    </button></li>
                  ))}
                </ul>
              )}
            </>
          )}
        </fieldset>

        {escolhida && (
          <p className="resumo" role="status">
            {escolhida.noites} {escolhida.noites === 1 ? "noite" : "noites"} × {moeda(escolhida.acomodacao.valor_diaria)} = <strong>{moeda(escolhida.valor_total)}</strong>
          </p>
        )}
        <div className="acoes">
          <button type="button" className="btn" onClick={() => navegar("/reservas")}>Cancelar</button>
          <button type="submit" className="btn btn-primario" disabled={!pronto || criar.isPending}>{criar.isPending ? "Criando…" : "Criar reserva"}</button>
        </div>
      </form>

      {cadastrando && (
        <Modal titulo="Novo hóspede" aoFechar={() => setCadastrando(false)}>
          <HospedeForm aoCancelar={() => setCadastrando(false)} aoSalvar={(h) => { setHospede(h); setCadastrando(false); }} />
        </Modal>
      )}
    </section>
  );
}
