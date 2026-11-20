import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import ReservaNova from "./ReservaNova";
import { mockApi, RECEPCAO, renderApp } from "../test/utils";

const quarto = (id: number, numero: string, diaria: string) => ({
  acomodacao: { id, numero, categoria: { id: 1, nome: "Standard", descricao: null }, capacidade: 2, valor_diaria: diaria, status: "LIVRE", ativo: true, caracteristicas: [] },
  noites: 5, valor_total: String(Number(diaria) * 5),
});
const maria = { id: 3, nome: "Maria Souza", documento_tipo: "CPF", documento_numero: "52998224725", email: "m@x.com", telefone: null, criado_em: "2026-11-01T10:00:00Z" };

function tela() {
  return (
    <Routes>
      <Route path="/reservas/nova" element={<ReservaNova />} />
      <Route path="/reservas/:id" element={<p>detalhe criado</p>} />
    </Routes>
  );
}

describe("Nova reserva", () => {
  it("fluxo completo: quarto vindo da disponibilidade + hóspede pré-selecionado → POST", async () => {
    const { chamadas } = mockApi({
      "GET /auth/me": { body: RECEPCAO },
      "GET /acomodacoes/disponiveis": { body: [quarto(1, "101", "150.00"), quarto(2, "102", "180.00")] },
      "GET /hospedes/3": { body: maria },
      "POST /reservas": { status: 201, body: { id: 99 } },
    });
    renderApp(tela(), { rota: "/reservas/nova?acomodacao=2&entrada=2099-12-10&saida=2099-12-15&hospedes=2&hospede=3", logado: RECEPCAO });

    expect(await screen.findByText("Maria Souza")).toBeInTheDocument();
    const quarto102 = await screen.findByRole("radio", { name: /Quarto 102/ });
    expect(quarto102).toBeChecked();
    expect(screen.getByRole("status")).toHaveTextContent("5 noites");

    await userEvent.click(screen.getByRole("button", { name: "Criar reserva" }));
    expect(await screen.findByText("detalhe criado")).toBeInTheDocument();
    const post = chamadas.find((c) => c.metodo === "POST")!;
    expect(post.corpo).toEqual({ hospede_id: 3, acomodacao_id: 2, data_entrada: "2099-12-10", data_saida: "2099-12-15", qtd_hospedes: 2 });
  });

  it("só habilita criar com quarto e hóspede escolhidos", async () => {
    mockApi({ "GET /auth/me": { body: RECEPCAO }, "GET /acomodacoes/disponiveis": { body: [quarto(1, "101", "150.00")] } });
    renderApp(tela(), { rota: "/reservas/nova?entrada=2099-12-10&saida=2099-12-15", logado: RECEPCAO });
    const criar = await screen.findByRole("button", { name: "Criar reserva" });
    expect(criar).toBeDisabled();
    await userEvent.click(await screen.findByRole("radio", { name: /Quarto 101/ }));
    expect(criar).toBeDisabled();   // falta o hóspede
  });

  it("avisa quando o quarto pré-escolhido já não está livre", async () => {
    mockApi({ "GET /auth/me": { body: RECEPCAO }, "GET /acomodacoes/disponiveis": { body: [quarto(1, "101", "150.00")] } });
    renderApp(tela(), { rota: "/reservas/nova?acomodacao=2&entrada=2099-12-10&saida=2099-12-15", logado: RECEPCAO });
    expect(await screen.findByText(/não está livre nesse período/)).toBeInTheDocument();
  });

  it("mostra o 409 do anti-overbooking e mantém o formulário", async () => {
    mockApi({
      "GET /auth/me": { body: RECEPCAO },
      "GET /acomodacoes/disponiveis": { body: [quarto(1, "101", "150.00")] },
      "GET /hospedes/3": { body: maria },
      "POST /reservas": { status: 409, body: { erro: "A acomodação já está reservada em parte do período informado" } },
    });
    renderApp(tela(), { rota: "/reservas/nova?acomodacao=1&entrada=2099-12-10&saida=2099-12-15&hospede=3", logado: RECEPCAO });
    await userEvent.click(await screen.findByRole("button", { name: "Criar reserva" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("já está reservada");
    await waitFor(() => expect(screen.getByRole("button", { name: "Criar reserva" })).toBeInTheDocument());
  });
});
