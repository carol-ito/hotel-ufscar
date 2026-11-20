import { useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import Alerta from "../components/Alerta";
import Campo from "../components/Campo";
import Confirmacao from "../components/Confirmacao";
import DateRangePicker from "../components/DateRangePicker";
import Modal from "../components/Modal";
import StatusBadge from "../components/StatusBadge";
import { useAcaoReserva, useReserva } from "../hooks/useReservas";
import { periodoValido } from "../lib/datas";
import { mensagemErro } from "../lib/erros";
import { dataBR, dataHoraBR, documentoBR, moeda } from "../lib/format";
import type { Reserva } from "../api/types";

type Dialogo = "confirmar" | "cancelar" | "alterar" | null;

export default function ReservaDetalhe() {
  const id = Number(useParams().id);
  const local = useLocation();
  const { data: r, isLoading, error } = useReserva(id);
  const acao = useAcaoReserva(id);
  const [dialogo, setDialogo] = useState<Dialogo>(null);
  const [aviso, setAviso] = useState<string | null>((local.state as { aviso?: string } | null)?.aviso ?? null);

  const abrir = (d: Dialogo) => { acao.reset(); setDialogo(d); };
  const fechar = () => setDialogo(null);
  const concluir = (msg: string) => { setDialogo(null); setAviso(msg); };

  if (isLoading) return <p className="carregando">Carregando…</p>;
  if (error || !r) return <section><Alerta>{mensagemErro(error)}</Alerta><Link to="/reservas">← Voltar às reservas</Link></section>;

  const pode = (a: string) => r.acoes_permitidas.includes(a as never);

  return (
    <section>
      <p><Link to="/reservas">← Reservas</Link></p>
      <header className="topo">
        <div><h1>Reserva #{r.id} <StatusBadge status={r.status} /></h1><p className="sub">{r.hospede.nome} · quarto {r.acomodacao.numero}</p></div>
        <div className="acoes-topo">
          {pode("alterar") && <button type="button" className="btn" onClick={() => abrir("alterar")}>Alterar</button>}
          {pode("cancelar") && <button type="button" className="btn btn-perigo-contorno" onClick={() => abrir("cancelar")}>Cancelar reserva</button>}
          {pode("confirmar") && <button type="button" className="btn btn-primario" onClick={() => abrir("confirmar")}>Confirmar</button>}
        </div>
      </header>
      {aviso && <Alerta tipo="sucesso">{aviso}</Alerta>}
      {r.status === "PENDENTE" && <Alerta tipo="info">Reserva pendente: o período já está bloqueado para outras reservas, mas o quarto só passa a “Reservado” depois de confirmada.</Alerta>}

      <div className="cartoes">
        <dl className="detalhes">
          <dt>Período</dt><dd>{dataBR(r.data_entrada)} → {dataBR(r.data_saida)} ({r.noites} {r.noites === 1 ? "noite" : "noites"})</dd>
          <dt>Hóspedes</dt><dd>{r.qtd_hospedes} de {r.acomodacao.capacidade}</dd>
          <dt>Diária aplicada</dt><dd>{moeda(r.valor_diaria)}</dd>
          <dt>Total das diárias</dt><dd><strong>{moeda(r.valor_total)}</strong></dd>
          {r.motivo_cancelamento && (<><dt>Motivo do cancelamento</dt><dd>{r.motivo_cancelamento}</dd></>)}
        </dl>
        <dl className="detalhes">
          <dt>Hóspede</dt><dd>{r.hospede.nome}<br /><small>{documentoBR(r.hospede.documento_tipo, r.hospede.documento_numero)}</small></dd>
          <dt>Criada em</dt><dd>{dataHoraBR(r.criada_em)}</dd>
          {r.confirmada_em && (<><dt>Confirmada em</dt><dd>{dataHoraBR(r.confirmada_em)}</dd></>)}
          {r.cancelada_em && (<><dt>Cancelada em</dt><dd>{dataHoraBR(r.cancelada_em)}</dd></>)}
        </dl>
      </div>

      {dialogo === "confirmar" && (
        <Confirmacao titulo="Confirmar reserva" confirmarTexto="Confirmar reserva" ocupado={acao.isPending}
          aoCancelar={fechar} aoConfirmar={() => acao.mutate({ tipo: "confirmar" }, { onSuccess: () => concluir("Reserva confirmada.") })}>
          {acao.error && <Alerta>{mensagemErro(acao.error)}</Alerta>}
          <p>Confirmar a reserva de <strong>{r.hospede.nome}</strong> no quarto {r.acomodacao.numero}, de {dataBR(r.data_entrada)} a {dataBR(r.data_saida)}?</p>
        </Confirmacao>
      )}
      {dialogo === "cancelar" && <CancelarModal r={r} acao={acao} aoFechar={fechar} aoConcluir={() => concluir("Reserva cancelada. O período foi liberado.")} />}
      {dialogo === "alterar" && <AlterarModal r={r} acao={acao} aoFechar={fechar} aoConcluir={() => concluir("Reserva alterada.")} />}
    </section>
  );
}

type Acao = ReturnType<typeof useAcaoReserva>;

function CancelarModal({ r, acao, aoFechar, aoConcluir }: { r: Reserva; acao: Acao; aoFechar(): void; aoConcluir(): void }) {
  const [motivo, setMotivo] = useState("");
  return (
    <Modal titulo="Cancelar reserva" aoFechar={aoFechar} largura={480}>
      <form className="form" onSubmit={(e) => { e.preventDefault(); acao.mutate({ tipo: "cancelar", motivo }, { onSuccess: aoConcluir }); }}>
        {acao.error && <Alerta>{mensagemErro(acao.error)}</Alerta>}
        <p>Cancelar a reserva #{r.id} libera o quarto {r.acomodacao.numero} neste período. Isso não pode ser desfeito.</p>
        <Campo rotulo="Motivo (opcional)">{(id) => <textarea id={id} rows={3} maxLength={255} value={motivo} onChange={(e) => setMotivo(e.target.value)} />}</Campo>
        <div className="acoes">
          <button type="button" className="btn" onClick={aoFechar}>Voltar</button>
          <button type="submit" className="btn btn-perigo" disabled={acao.isPending}>{acao.isPending ? "Cancelando…" : "Cancelar reserva"}</button>
        </div>
      </form>
    </Modal>
  );
}

function AlterarModal({ r, acao, aoFechar, aoConcluir }: { r: Reserva; acao: Acao; aoFechar(): void; aoConcluir(): void }) {
  const [entrada, setEntrada] = useState(r.data_entrada);
  const [saida, setSaida] = useState(r.data_saida);
  const [qtd, setQtd] = useState(String(r.qtd_hospedes));
  const valido = periodoValido(entrada, saida) && Number(qtd) >= 1 && Number(qtd) <= r.acomodacao.capacidade;
  return (
    <Modal titulo="Alterar reserva" aoFechar={aoFechar}>
      <form className="form" onSubmit={(e) => { e.preventDefault(); if (valido) acao.mutate({ tipo: "alterar", data_entrada: entrada, data_saida: saida, qtd_hospedes: Number(qtd) }, { onSuccess: aoConcluir }); }}>
        {acao.error && <Alerta>{mensagemErro(acao.error)}</Alerta>}
        <DateRangePicker entrada={entrada} saida={saida} aoMudar={(e, s) => { setEntrada(e); setSaida(s); }} permitirPassado={entrada === r.data_entrada} />
        <Campo rotulo="Nº de hóspedes" dica={`Esta acomodação comporta até ${r.acomodacao.capacidade}.`}>
          {(id, d) => <input id={id} type="number" min={1} max={r.acomodacao.capacidade} value={qtd} onChange={(e) => setQtd(e.target.value)} aria-describedby={d} />}
        </Campo>
        <p className="dica">A diária de {moeda(r.valor_diaria)} da reserva é mantida; só o total é recalculado.</p>
        <div className="acoes">
          <button type="button" className="btn" onClick={aoFechar}>Voltar</button>
          <button type="submit" className="btn btn-primario" disabled={!valido || acao.isPending}>{acao.isPending ? "Salvando…" : "Salvar alterações"}</button>
        </div>
      </form>
    </Modal>
  );
}
