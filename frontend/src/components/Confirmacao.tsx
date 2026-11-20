import { ReactNode } from "react";
import Modal from "./Modal";

interface Props {
  titulo: string; confirmarTexto: string; perigo?: boolean; ocupado?: boolean;
  aoConfirmar(): void; aoCancelar(): void; children: ReactNode;
}

export default function Confirmacao({ titulo, confirmarTexto, perigo, ocupado, aoConfirmar, aoCancelar, children }: Props) {
  return (
    <Modal titulo={titulo} aoFechar={aoCancelar} largura={440}>
      <div className="modal-texto">{children}</div>
      <div className="acoes">
        <button type="button" className="btn" onClick={aoCancelar}>Voltar</button>
        <button type="button" className={`btn ${perigo ? "btn-perigo" : "btn-primario"}`} onClick={aoConfirmar} disabled={ocupado}>
          {ocupado ? "Aguarde…" : confirmarTexto}
        </button>
      </div>
    </Modal>
  );
}
