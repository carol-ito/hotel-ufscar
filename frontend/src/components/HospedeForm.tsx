import { FormEvent, useState } from "react";
import { ApiError } from "../api/apiGateway";
import type { Hospede, HospedeForm as Dados, TipoDocumento } from "../api/types";
import { useSalvarHospede } from "../hooks/useHospedes";
import Alerta from "./Alerta";
import Campo from "./Campo";

interface Props { inicial?: Hospede; aoSalvar(h: Hospede): void; aoCancelar(): void }

const TIPOS: TipoDocumento[] = ["CPF", "RG", "PASSAPORTE", "OUTRO"];

export function validarHospede(f: Dados): Record<string, string> {
  const e: Record<string, string> = {};
  if (f.nome.trim().length < 2) e.nome = "Informe o nome completo";
  if (!f.documento_numero.trim()) e.documento_numero = "Informe o número do documento";
  if (!f.email.trim() && !f.telefone.trim()) e.contato = "Informe ao menos um contato: e-mail ou telefone";
  if (f.email.trim() && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email.trim())) e.email = "E-mail inválido";
  return e;
}

export default function HospedeForm({ inicial, aoSalvar, aoCancelar }: Props) {
  const [f, setF] = useState<Dados>({
    nome: inicial?.nome ?? "", documento_tipo: inicial?.documento_tipo ?? "CPF",
    documento_numero: inicial?.documento_numero ?? "", email: inicial?.email ?? "", telefone: inicial?.telefone ?? "",
  });
  const [erros, setErros] = useState<Record<string, string>>({});
  const salvar = useSalvarHospede();
  const set = (campo: keyof Dados) => (e: { target: { value: string } }) => setF({ ...f, [campo]: e.target.value });

  async function enviar(ev: FormEvent) {
    ev.preventDefault();
    const locais = validarHospede(f);
    setErros(locais);
    if (Object.keys(locais).length) return;
    try {
      aoSalvar(await salvar.mutateAsync({ id: inicial?.id, dados: f }));
    } catch (e) {
      if (e instanceof ApiError && e.campos) setErros(e.campos);
    }
  }

  const erroApi = salvar.error instanceof ApiError ? salvar.error.message : salvar.error ? "Erro inesperado" : null;

  return (
    <form onSubmit={enviar} noValidate className="form">
      {erroApi && <Alerta>{erroApi}</Alerta>}
      <Campo rotulo="Nome completo" erro={erros.nome}>
        {(id, d) => <input id={id} value={f.nome} onChange={set("nome")} maxLength={120} autoComplete="off" aria-describedby={d} />}
      </Campo>
      <div className="linha">
        <Campo rotulo="Tipo de documento">
          {(id) => (
            <select id={id} value={f.documento_tipo} onChange={set("documento_tipo")}>
              {TIPOS.map((t) => <option key={t}>{t}</option>)}
            </select>
          )}
        </Campo>
        <Campo rotulo="Número do documento" erro={erros.documento_numero}>
          {(id, d) => <input id={id} value={f.documento_numero} onChange={set("documento_numero")} maxLength={30} autoComplete="off" aria-describedby={d} />}
        </Campo>
      </div>
      <div className="linha">
        <Campo rotulo="E-mail" erro={erros.email}>
          {(id, d) => <input id={id} type="email" value={f.email} onChange={set("email")} maxLength={160} aria-describedby={d} />}
        </Campo>
        <Campo rotulo="Telefone">
          {(id) => <input id={id} type="tel" value={f.telefone} onChange={set("telefone")} maxLength={20} />}
        </Campo>
      </div>
      {erros.contato && <small className="msg-erro" role="alert">{erros.contato}</small>}
      <p className="dica">Guardamos só o necessário (LGPD): nome, documento e um contato.</p>
      <div className="acoes">
        <button type="button" className="btn" onClick={aoCancelar}>Cancelar</button>
        <button type="submit" className="btn btn-primario" disabled={salvar.isPending}>{salvar.isPending ? "Salvando…" : "Salvar hóspede"}</button>
      </div>
    </form>
  );
}
