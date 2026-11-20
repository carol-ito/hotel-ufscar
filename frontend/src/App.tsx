import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute";
import Layout from "./components/Layout";
import Acomodacoes from "./pages/Acomodacoes";
import { AcessoNegado, NaoEncontrada } from "./pages/Avisos";
import Disponibilidade from "./pages/Disponibilidade";
import Hospedes from "./pages/Hospedes";
import Login from "./pages/Login";
import ReservaDetalhe from "./pages/ReservaDetalhe";
import ReservaNova from "./pages/ReservaNova";
import Reservas from "./pages/Reservas";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute perfis={["GESTAO", "RECEPCAO"]}><Layout /></ProtectedRoute>}>
        <Route index element={<Navigate to="/reservas" replace />} />
        <Route path="/reservas" element={<Reservas />} />
        <Route path="/reservas/nova" element={<ReservaNova />} />
        <Route path="/reservas/:id" element={<ReservaDetalhe />} />
        <Route path="/disponibilidade" element={<Disponibilidade />} />
        <Route path="/hospedes" element={<Hospedes />} />
        <Route path="/acomodacoes" element={<Acomodacoes />} />
        <Route path="/acesso-negado" element={<AcessoNegado />} />
        <Route path="*" element={<NaoEncontrada />} />
      </Route>
    </Routes>
  );
}
