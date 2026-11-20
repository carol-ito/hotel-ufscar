interface Props { total: number; limite: number; offset: number; aoMudar(offset: number): void }

export default function Paginacao({ total, limite, offset, aoMudar }: Props) {
  if (total <= limite) return null;
  const pagina = Math.floor(offset / limite) + 1;
  const paginas = Math.ceil(total / limite);
  return (
    <nav className="paginacao" aria-label="Paginação">
      <button type="button" className="btn btn-pequeno" disabled={offset === 0} onClick={() => aoMudar(Math.max(0, offset - limite))}>← Anterior</button>
      <span>Página {pagina} de {paginas} · {total} registros</span>
      <button type="button" className="btn btn-pequeno" disabled={offset + limite >= total} onClick={() => aoMudar(offset + limite)}>Próxima →</button>
    </nav>
  );
}
