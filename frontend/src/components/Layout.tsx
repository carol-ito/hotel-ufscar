import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const ITENS = [
  { para: "/reservas", rotulo: "Reservas" },
  { para: "/disponibilidade", rotulo: "Disponibilidade" },
  { para: "/hospedes", rotulo: "Hóspedes" },
  { para: "/acomodacoes", rotulo: "Acomodações" },
];

export default function Layout() {
  const { usuario, sair } = useAuth();
  return (
    <div className="app">
      <aside className="lateral">
        <div className="marca"><span className="marca-logo" aria-hidden="true">H</span> Hotel UFSCar</div>
        <nav aria-label="Principal">
          {ITENS.map((i) => <NavLink key={i.para} to={i.para} className={({ isActive }) => (isActive ? "ativo" : undefined)}>{i.rotulo}</NavLink>)}
        </nav>
        <div className="usuario">
          <strong>{usuario?.nome}</strong>
          <span>{usuario?.perfil === "GESTAO" ? "Gestão" : "Recepção"}</span>
          <button type="button" className="btn btn-pequeno" onClick={() => sair()}>Sair</button>
        </div>
      </aside>
      <main className="conteudo"><Outlet /></main>
    </div>
  );
}
