import { FormEvent, useState } from "react";
import { ApiError } from "../api/apiGateway";
import type { Acomodacao, AcomodacaoForm, Caracteristica, Categoria } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import Alerta from "../components/Alerta";
import Campo from "../components/Campo";
import Confirmacao from "../components/Confirmacao";
import Modal from "../components/Modal";
import StatusBadge from "../components/StatusBadge";
import Tabela from "../components/Tabela";
import { useAcomodacoes, useCaracteristicas, useCategorias, useDefinirAtivo, useSalvarAcomodacao, useSalvarCatalogo } from "../hooks/useAcomodacoes";
import { mensagemErro } from "../lib/erros";
import { moeda } from "../lib/format";

type Aba = "acomodacoes" | "categorias" | "caracteristicas";

export default function Acomodacoes() {
  const { tem } = useAuth();
  const gestao = tem("GESTAO");
  const [aba, setAba] = useState<Aba>("acomodacoes");
  const abas: [Aba, string][] = [["acomodacoes", "Acomodações"], ["categorias", "Categorias"], ["caracteristicas", "Características"]];

  return (
    <section>
      <header className="topo"><div><h1>Acomodações</h1><p className="sub">Catálogo de quartos e o status de cada um.</p></div></header>
      {gestao && (
        <div className="abas" role="tablist">
          {abas.map(([id, rotulo]) => (
            <button key={id} role="tab" type="button" aria-selected={aba === id} className={aba === id ? "aba ativa" : "aba"} onClick={() => setAba(id)}>{rotulo}</button>
          ))}
        </div>
      )}
      {aba === "acomodacoes" && <ListaAcomodacoes gestao={gestao} />}
      {gestao && aba === "categorias" && <Catalogo tipo="categorias" />}
      {gestao && aba === "caracteristicas" && <Catalogo tipo="caracteristicas" />}
    </section>
  );
}

function ListaAcomodacoes({ gestao }: { gestao: boolean }) {
  const { data, isLoading, error } = useAcomodacoes();
  const categorias = useCategorias();
  const [categoria, setCategoria] = useState("");
  const [status, setStatus] = useState("");
  const [inativas, setInativas] = useState(false);
  const [edicao, setEdicao] = useState<{ item?: Acomodacao } | null>(null);
  const [alvoAtivo, setAlvoAtivo] = useState<Acomodacao | null>(null);
  const definirAtivo = useDefinirAtivo();
  const [aviso, setAviso] = useState<string | null>(null);

  const itens = data?.filter((a) => (inativas || a.ativo) && (!categoria || String(a.categoria.id) === categoria) && (!status || a.status === status));

  async function confirmarAtivo() {
    if (!alvoAtivo) return;
    try {
      await definirAtivo.mutateAsync({ id: alvoAtivo.id, ativo: !alvoAtivo.ativo });
      setAviso(`Acomodação ${alvoAtivo.numero} ${alvoAtivo.ativo ? "inativada" : "reativada"}.`);
      setAlvoAtivo(null);
    } catch { /* o erro aparece no próprio modal */ }
  }

  return (
    <>
      {gestao && <div className="acoes-topo"><button type="button" className="btn btn-primario" onClick={() => setEdicao({})}>Nova acomodação</button></div>}
      {aviso && <Alerta tipo="sucesso">{aviso}</Alerta>}
      {error && <Alerta>{mensagemErro(error)}</Alerta>}
      <div className="filtros">
        <Campo rotulo="Categoria">
          {(id) => (
            <select id={id} value={categoria} onChange={(e) => setCategoria(e.target.value)}>
              <option value="">Todas</option>
              {categorias.data?.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
            </select>
          )}
        </Campo>
        <Campo rotulo="Status">
          {(id) => (
            <select id={id} value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">Todos</option><option value="LIVRE">Livre</option><option value="RESERVADO">Reservado</option><option value="OCUPADO">Ocupado</option>
            </select>
          )}
        </Campo>
        <label className="check"><input type="checkbox" checked={inativas} onChange={(e) => setInativas(e.target.checked)} /> Mostrar inativas</label>
      </div>

      <Tabela legenda="Lista de acomodações" carregando={isLoading} itens={itens} chave={(a) => a.id}
        colunas={[
          { cabecalho: "Nº", celula: (a) => <strong>{a.numero}</strong> },
          { cabecalho: "Categoria", celula: (a) => a.categoria.nome },
          { cabecalho: "Capacidade", celula: (a) => `${a.capacidade} hóspede${a.capacidade > 1 ? "s" : ""}` },
          { cabecalho: "Diária", classe: "num", celula: (a) => moeda(a.valor_diaria) },
          { cabecalho: "Características", celula: (a) => <span className="chips">{a.caracteristicas.map((c) => <span key={c.id} className="chip">{c.nome}</span>)}</span> },
          { cabecalho: "Status", celula: (a) => a.ativo ? <StatusBadge status={a.status} /> : <span className="badge badge-inativa">Inativa</span> },
          ...(gestao ? [{ cabecalho: "Ações", classe: "acoes-celula", celula: (a: Acomodacao) => (
            <>
              <button type="button" className="btn btn-pequeno" onClick={() => setEdicao({ item: a })}>Editar</button>{" "}
              <button type="button" className="btn btn-pequeno" onClick={() => { definirAtivo.reset(); setAlvoAtivo(a); }}>{a.ativo ? "Inativar" : "Reativar"}</button>
            </>
          ) }] : []),
        ]} />

      {edicao && <AcomodacaoModal item={edicao.item} aoFechar={() => setEdicao(null)} aoSalvar={(a) => { setEdicao(null); setAviso(`Acomodação ${a.numero} salva.`); }} />}
      {alvoAtivo && (
        <Confirmacao titulo={alvoAtivo.ativo ? "Inativar acomodação" : "Reativar acomodação"} perigo={alvoAtivo.ativo}
          confirmarTexto={alvoAtivo.ativo ? "Inativar" : "Reativar"} ocupado={definirAtivo.isPending}
          aoConfirmar={confirmarAtivo} aoCancelar={() => setAlvoAtivo(null)}>
          {definirAtivo.error && <Alerta>{mensagemErro(definirAtivo.error)}</Alerta>}
          <p>{alvoAtivo.ativo
            ? `A acomodação ${alvoAtivo.numero} deixa de aparecer nas consultas de disponibilidade. O histórico de reservas é mantido.`
            : `A acomodação ${alvoAtivo.numero} volta a aparecer nas consultas de disponibilidade.`}</p>
        </Confirmacao>
      )}
    </>
  );
}

function normalizarDecimal(v: string): string {
  return v.trim().replace(/\./g, "").replace(",", ".");   // aceita "1.250,50" e "150,5"
}

function AcomodacaoModal({ item, aoFechar, aoSalvar }: { item?: Acomodacao; aoFechar(): void; aoSalvar(a: Acomodacao): void }) {
  const categorias = useCategorias();
  const caracteristicas = useCaracteristicas();
  const salvar = useSalvarAcomodacao();
  const [numero, setNumero] = useState(item?.numero ?? "");
  const [categoriaId, setCategoriaId] = useState(item ? String(item.categoria.id) : "");
  const [capacidade, setCapacidade] = useState(String(item?.capacidade ?? 2));
  const [valor, setValor] = useState(item ? String(item.valor_diaria).replace(".", ",") : "");
  const [marcadas, setMarcadas] = useState<number[]>(item?.caracteristicas.map((c) => c.id) ?? []);
  const [erros, setErros] = useState<Record<string, string>>({});

  async function enviar(ev: FormEvent) {
    ev.preventDefault();
    const e: Record<string, string> = {};
    const dec = normalizarDecimal(valor);
    if (!numero.trim()) e.numero = "Informe o número";
    if (!categoriaId) e.categoria_id = "Escolha a categoria";
    if (!(Number(capacidade) >= 1)) e.capacidade = "Mínimo 1 hóspede";
    if (!(Number(dec) > 0)) e.valor_diaria = "Informe um valor maior que zero";
    setErros(e);
    if (Object.keys(e).length) return;
    const dados: AcomodacaoForm = { numero: numero.trim(), categoria_id: Number(categoriaId), capacidade: Number(capacidade), valor_diaria: dec, caracteristica_ids: marcadas };
    try {
      aoSalvar(await salvar.mutateAsync({ id: item?.id, dados }));
    } catch (err) {
      if (err instanceof ApiError && err.campos) setErros(err.campos);
    }
  }

  const alternar = (id: number) => setMarcadas(marcadas.includes(id) ? marcadas.filter((x) => x !== id) : [...marcadas, id]);

  return (
    <Modal titulo={item ? `Editar acomodação ${item.numero}` : "Nova acomodação"} aoFechar={aoFechar}>
      <form className="form" onSubmit={enviar} noValidate>
        {salvar.error && <Alerta>{mensagemErro(salvar.error)}</Alerta>}
        <div className="linha">
          <Campo rotulo="Número" erro={erros.numero}>{(id, d) => <input id={id} value={numero} maxLength={10} onChange={(e) => setNumero(e.target.value)} aria-describedby={d} />}</Campo>
          <Campo rotulo="Categoria" erro={erros.categoria_id}>
            {(id, d) => (
              <select id={id} value={categoriaId} onChange={(e) => setCategoriaId(e.target.value)} aria-describedby={d}>
                <option value="">Selecione…</option>
                {categorias.data?.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
              </select>
            )}
          </Campo>
        </div>
        <div className="linha">
          <Campo rotulo="Capacidade (hóspedes)" erro={erros.capacidade}>{(id, d) => <input id={id} type="number" min={1} max={20} value={capacidade} onChange={(e) => setCapacidade(e.target.value)} aria-describedby={d} />}</Campo>
          <Campo rotulo="Valor da diária (R$)" erro={erros.valor_diaria} dica={item ? "Não altera reservas já feitas." : undefined}>
            {(id, d) => <input id={id} inputMode="decimal" placeholder="150,00" value={valor} onChange={(e) => setValor(e.target.value)} aria-describedby={d} />}
          </Campo>
        </div>
        <fieldset className="grupo">
          <legend>Características</legend>
          {caracteristicas.data?.length === 0 && <p className="dica">Cadastre características na aba “Características”.</p>}
          <div className="chips-check">
            {caracteristicas.data?.map((c: Caracteristica) => (
              <label key={c.id} className="check"><input type="checkbox" checked={marcadas.includes(c.id)} onChange={() => alternar(c.id)} /> {c.nome}</label>
            ))}
          </div>
        </fieldset>
        <div className="acoes">
          <button type="button" className="btn" onClick={aoFechar}>Cancelar</button>
          <button type="submit" className="btn btn-primario" disabled={salvar.isPending}>{salvar.isPending ? "Salvando…" : "Salvar"}</button>
        </div>
      </form>
    </Modal>
  );
}

function Catalogo({ tipo }: { tipo: "categorias" | "caracteristicas" }) {
  const categorias = useCategorias();
  const caracteristicas = useCaracteristicas();
  const lista = tipo === "categorias" ? categorias : caracteristicas;
  const salvar = useSalvarCatalogo(tipo);
  const [edicao, setEdicao] = useState<{ item?: Categoria | Caracteristica } | null>(null);
  const [nome, setNome] = useState("");
  const [descricao, setDescricao] = useState("");
  const rotulo = tipo === "categorias" ? "categoria" : "característica";

  function abrir(item?: Categoria | Caracteristica) {
    salvar.reset();
    setNome(item?.nome ?? "");
    setDescricao(item && "descricao" in item ? item.descricao ?? "" : "");
    setEdicao({ item });
  }

  async function enviar(ev: FormEvent) {
    ev.preventDefault();
    if (nome.trim().length < 2) return;
    try {
      await salvar.mutateAsync({ id: edicao?.item?.id, dados: tipo === "categorias" ? { nome: nome.trim(), descricao: descricao.trim() || null } : { nome: nome.trim() } });
      setEdicao(null);
    } catch { /* mostrado no modal */ }
  }

  return (
    <>
      <div className="acoes-topo"><button type="button" className="btn btn-primario" onClick={() => abrir()}>Nova {rotulo}</button></div>
      {lista.error && <Alerta>{mensagemErro(lista.error)}</Alerta>}
      <Tabela legenda={`Lista de ${tipo}`} carregando={lista.isLoading} itens={lista.data as (Categoria | Caracteristica)[] | undefined} chave={(i) => i.id}
        colunas={[
          { cabecalho: "Nome", celula: (i) => <strong>{i.nome}</strong> },
          ...(tipo === "categorias" ? [{ cabecalho: "Descrição", celula: (i: Categoria | Caracteristica) => ("descricao" in i ? i.descricao ?? "—" : "—") }] : []),
          { cabecalho: "Ações", classe: "acoes-celula", celula: (i) => <button type="button" className="btn btn-pequeno" onClick={() => abrir(i)}>Editar</button> },
        ]} />
      {edicao && (
        <Modal titulo={`${edicao.item ? "Editar" : "Nova"} ${rotulo}`} aoFechar={() => setEdicao(null)} largura={460}>
          <form className="form" onSubmit={enviar}>
            {salvar.error && <Alerta>{mensagemErro(salvar.error)}</Alerta>}
            <Campo rotulo="Nome">{(id) => <input id={id} value={nome} maxLength={60} required minLength={2} onChange={(e) => setNome(e.target.value)} />}</Campo>
            {tipo === "categorias" && <Campo rotulo="Descrição">{(id) => <input id={id} value={descricao} maxLength={255} onChange={(e) => setDescricao(e.target.value)} />}</Campo>}
            <div className="acoes">
              <button type="button" className="btn" onClick={() => setEdicao(null)}>Cancelar</button>
              <button type="submit" className="btn btn-primario" disabled={salvar.isPending}>Salvar</button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}
