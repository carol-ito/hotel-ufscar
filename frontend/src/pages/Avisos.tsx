import { Link } from "react-router-dom";

export function AcessoNegado() {
  return (
    <section className="aviso-pagina">
      <h1>Acesso negado</h1>
      <p>Seu perfil não tem permissão para ver esta página.</p>
      <Link className="btn btn-primario" to="/reservas">Ir para as reservas</Link>
    </section>
  );
}

export function NaoEncontrada() {
  return (
    <section className="aviso-pagina">
      <h1>Página não encontrada</h1>
      <p>O endereço não existe ou foi movido.</p>
      <Link className="btn btn-primario" to="/reservas">Ir para as reservas</Link>
    </section>
  );
}
