import { ReactNode } from "react";

export interface Coluna<T> { cabecalho: string; celula(item: T): ReactNode; classe?: string }

interface Props<T> {
  colunas: Coluna<T>[]; itens: T[] | undefined; chave(item: T): string | number;
  carregando?: boolean; vazio?: string; aoClicar?(item: T): void; legenda: string;
}

export default function Tabela<T>({ colunas, itens, chave, carregando, vazio = "Nenhum registro encontrado.", aoClicar, legenda }: Props<T>) {
  return (
    <div className="tabela-wrap">
      <table className="tabela">
        <caption className="sr-only">{legenda}</caption>
        <thead>
          <tr>{colunas.map((c) => <th key={c.cabecalho} scope="col" className={c.classe}>{c.cabecalho}</th>)}</tr>
        </thead>
        <tbody>
          {carregando && !itens ? (
            <tr><td colSpan={colunas.length} className="vazio">Carregando…</td></tr>
          ) : itens && itens.length === 0 ? (
            <tr><td colSpan={colunas.length} className="vazio">{vazio}</td></tr>
          ) : (
            itens?.map((item) => (
              <tr key={chave(item)} className={aoClicar ? "clicavel" : undefined}
                  onClick={aoClicar ? () => aoClicar(item) : undefined}>
                {colunas.map((c) => <td key={c.cabecalho} className={c.classe}>{c.celula(item)}</td>)}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
