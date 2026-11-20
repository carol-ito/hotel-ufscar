import { ReactNode, useEffect, useRef } from "react";

interface Props { titulo: string; aoFechar(): void; children: ReactNode; largura?: number }

export default function Modal({ titulo, aoFechar, children, largura = 560 }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const anterior = document.activeElement as HTMLElement | null;
    ref.current?.querySelector<HTMLElement>("input, select, textarea, button")?.focus();
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") aoFechar(); };
    document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("keydown", esc); anterior?.focus(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="modal-fundo" onMouseDown={(e) => { if (e.target === e.currentTarget) aoFechar(); }}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={titulo} style={{ maxWidth: largura }} ref={ref}>
        <header className="modal-topo">
          <h2>{titulo}</h2>
          <button type="button" className="btn-icone" aria-label="Fechar" onClick={aoFechar}>×</button>
        </header>
        <div className="modal-corpo">{children}</div>
      </div>
    </div>
  );
}
