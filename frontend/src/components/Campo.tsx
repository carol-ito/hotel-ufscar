import { ReactNode, useId } from "react";

interface Props { rotulo: string; erro?: string; dica?: string; children: (id: string, descricao?: string) => ReactNode }

/** Rótulo + controle + mensagem de erro ligados por id (acessível e testável por getByLabelText). */
export default function Campo({ rotulo, erro, dica, children }: Props) {
  const id = useId();
  const descId = erro || dica ? `${id}-desc` : undefined;
  return (
    <div className={`campo${erro ? " campo-erro" : ""}`}>
      <label htmlFor={id}>{rotulo}</label>
      {children(id, descId)}
      {erro ? <small id={descId} className="msg-erro" role="alert">{erro}</small>
            : dica ? <small id={descId} className="dica">{dica}</small> : null}
    </div>
  );
}
