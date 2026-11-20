import { FormEvent, KeyboardEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import Alerta from "../components/Alerta";
import Campo from "../components/Campo";
import { mensagemErro } from "../lib/erros";

const RECURSOS = [
  "Reservas e disponibilidade em tempo real",
  "Cadastro de hóspedes e acomodações",
  "Sem risco de reserva em duplicidade",
];

function Icone({ d }: { d: string }) {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={d} />
    </svg>
  );
}
const ICONE_CADEADO = "M7 11V8a5 5 0 0 1 10 0v3M5 11h14v10H5z";
const ICONE_OLHO = "M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z";
const ICONE_OLHO_RISCADO = "M3 3l18 18M10.6 5.1A9.7 9.7 0 0 1 12 5c6.5 0 10 7 10 7a17 17 0 0 1-3.2 4M6.5 6.6A16 16 0 0 0 2 12s3.5 7 10 7a9.6 9.6 0 0 0 4.4-1M9.9 9.9a3 3 0 0 0 4.2 4.2";

export default function Login() {
  const { usuario, entrar, aviso } = useAuth();
  const navegar = useNavigate();
  const local = useLocation();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [verSenha, setVerSenha] = useState(false);
  const [capsLigado, setCapsLigado] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const destino = (local.state as { de?: string } | null)?.de ?? "/reservas";

  if (usuario) return <Navigate to={destino} replace />;

  const checarCaps = (e: KeyboardEvent<HTMLInputElement>) => setCapsLigado(e.getModifierState?.("CapsLock") ?? false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setErro(null);
    setEnviando(true);
    try {
      await entrar(email.trim(), senha);
      navegar(destino, { replace: true });
    } catch (err) {
      setErro(mensagemErro(err));
      setSenha("");     // quem errou a senha não precisa apagá-la à mão
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="auth">
      <aside className="auth-marca">
        <div className="marca marca-clara"><span className="marca-logo" aria-hidden="true">H</span> Hotel UFSCar</div>
        <div className="auth-texto">
          <h2>Gestão de hospedagem</h2>
          <p>Painel interno da equipe do hotel.</p>
          <ul className="auth-recursos">
            {RECURSOS.map((r) => <li key={r}><span aria-hidden="true">✓</span> {r}</li>)}
          </ul>
        </div>
        <small className="auth-rodape">Acesso restrito a colaboradores autorizados.</small>
      </aside>

      <main className="auth-painel">
        <form className="auth-form form" onSubmit={enviar}>
          <div className="auth-cadeado"><Icone d={ICONE_CADEADO} /></div>
          <h1>Acesse sua conta</h1>
          <p className="sub">Entre com o e-mail e a senha fornecidos pela gestão.</p>
          {aviso && <Alerta tipo="info">{aviso}</Alerta>}
          {erro && <Alerta>{erro}</Alerta>}
          <Campo rotulo="E-mail">
            {(id) => <input id={id} type="email" autoComplete="username" autoFocus required placeholder="nome@hotel.com" value={email} onChange={(e) => setEmail(e.target.value)} />}
          </Campo>
          <Campo rotulo="Senha">
            {(id) => (
              <div className="senha">
                <input id={id} type={verSenha ? "text" : "password"} autoComplete="current-password" required value={senha}
                  onChange={(e) => setSenha(e.target.value)} onKeyDown={checarCaps} onKeyUp={checarCaps} onBlur={() => setCapsLigado(false)} />
                <button type="button" className="senha-ver" aria-label={verSenha ? "Ocultar senha" : "Mostrar senha"} aria-pressed={verSenha}
                  onClick={() => setVerSenha((v) => !v)}><Icone d={verSenha ? ICONE_OLHO_RISCADO : ICONE_OLHO} /></button>
              </div>
            )}
          </Campo>
          {capsLigado && <small className="auth-caps" role="status">Caps Lock está ativado</small>}
          <button type="submit" className="btn btn-primario btn-largo" disabled={enviando}>
            {enviando && <span className="giro" aria-hidden="true" />}{enviando ? "Entrando…" : "Entrar"}
          </button>
          <p className="dica auth-ajuda">Sem acesso ou esqueceu a senha? Fale com a gestão do hotel.</p>
        </form>
      </main>
    </div>
  );
}
