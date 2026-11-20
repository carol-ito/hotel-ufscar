import { useState } from "react";
import { Link } from "react-router-dom";
import type { Hospede } from "../api/types";
import Alerta from "../components/Alerta";
import HospedeForm from "../components/HospedeForm";
import Modal from "../components/Modal";
import Paginacao from "../components/Paginacao";
import Tabela from "../components/Tabela";
import { useDebounce } from "../hooks/useDebounce";
import { useHospedes } from "../hooks/useHospedes";
import { mensagemErro } from "../lib/erros";
import { dataBR, documentoBR } from "../lib/format";

type Edicao = { tipo: "novo" } | { tipo: "editar"; hospede: Hospede } | null;
const LIMITE = 10;

export default function Hospedes() {
  const [busca, setBusca] = useState("");
  const [offset, setOffset] = useState(0);
  const [edicao, setEdicao] = useState<Edicao>(null);
  const [aviso, setAviso] = useState<string | null>(null);
  const q = useDebounce(busca.trim(), 300);
  const { data, isLoading, error } = useHospedes(q, offset, LIMITE);

  return (
    <section>
      <header className="topo">
        <div><h1>Hóspedes</h1><p className="sub">Cadastro e busca por nome ou documento.</p></div>
        <button type="button" className="btn btn-primario" onClick={() => setEdicao({ tipo: "novo" })}>Novo hóspede</button>
      </header>

      {aviso && <Alerta tipo="sucesso">{aviso}</Alerta>}
      {error && <Alerta>{mensagemErro(error)}</Alerta>}

      <div className="filtros">
        <div className="campo campo-busca">
          <label htmlFor="busca-hospede">Buscar</label>
          <input id="busca-hospede" type="search" placeholder="Nome ou documento" value={busca}
            onChange={(e) => { setBusca(e.target.value); setOffset(0); }} />
        </div>
      </div>

      <Tabela legenda="Lista de hóspedes" carregando={isLoading} itens={data?.itens} chave={(h) => h.id}
        vazio={q ? "Nenhum hóspede encontrado para essa busca." : "Nenhum hóspede cadastrado ainda."}
        colunas={[
          { cabecalho: "Nome", celula: (h) => <strong>{h.nome}</strong> },
          { cabecalho: "Documento", celula: (h) => documentoBR(h.documento_tipo, h.documento_numero) },
          { cabecalho: "Contato", celula: (h) => [h.email, h.telefone].filter(Boolean).join(" · ") },
          { cabecalho: "Cadastro", celula: (h) => dataBR(h.criado_em) },
          { cabecalho: "Ações", classe: "acoes-celula", celula: (h) => (
            <>
              <button type="button" className="btn btn-pequeno" onClick={() => setEdicao({ tipo: "editar", hospede: h })}>Editar</button>{" "}
              <Link className="btn btn-pequeno" to={`/reservas/nova?hospede=${h.id}`}>Nova reserva</Link>
            </>
          ) },
        ]} />
      {data && <Paginacao total={data.total} limite={LIMITE} offset={offset} aoMudar={setOffset} />}

      {edicao && (
        <Modal titulo={edicao.tipo === "novo" ? "Novo hóspede" : "Editar hóspede"} aoFechar={() => setEdicao(null)}>
          <HospedeForm inicial={edicao.tipo === "editar" ? edicao.hospede : undefined}
            aoCancelar={() => setEdicao(null)}
            aoSalvar={(h) => { setEdicao(null); setAviso(`Hóspede ${h.nome} salvo.`); }} />
        </Modal>
      )}
    </section>
  );
}
