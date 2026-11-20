import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import HospedeForm, { validarHospede } from "./HospedeForm";
import { mockApi, renderApp } from "../test/utils";

const vazio = { nome: "", documento_tipo: "CPF" as const, documento_numero: "", email: "", telefone: "" };

describe("validarHospede", () => {
  it("exige nome, documento e um contato", () => {
    expect(Object.keys(validarHospede(vazio)).sort()).toEqual(["contato", "documento_numero", "nome"]);
  });
  it("aceita só telefone como contato e rejeita e-mail malformado", () => {
    expect(validarHospede({ ...vazio, nome: "Ana", documento_numero: "1", telefone: "9" })).toEqual({});
    expect(validarHospede({ ...vazio, nome: "Ana", documento_numero: "1", email: "ana@" }).email).toBeTruthy();
  });
});

describe("HospedeForm", () => {
  it("não envia enquanto inválido", async () => {
    const { chamadas } = mockApi({});
    renderApp(<HospedeForm aoSalvar={() => {}} aoCancelar={() => {}} />);
    await userEvent.click(screen.getByRole("button", { name: "Salvar hóspede" }));
    expect(await screen.findByText("Informe o nome completo")).toBeInTheDocument();
    expect(screen.getByText(/ao menos um contato/)).toBeInTheDocument();
    expect(chamadas).toHaveLength(0);
  });

  it("envia o payload limpo e devolve o hóspede salvo", async () => {
    const salvo = { id: 7, nome: "Ana Lima", documento_tipo: "CPF", documento_numero: "52998224725", email: null, telefone: "16999", criado_em: "2026-11-06T10:00:00Z" };
    const { chamadas } = mockApi({ "POST /hospedes": { status: 201, body: salvo } });
    const aoSalvar = vi.fn();
    renderApp(<HospedeForm aoSalvar={aoSalvar} aoCancelar={() => {}} />);
    await userEvent.type(screen.getByLabelText("Nome completo"), "  Ana Lima ");
    await userEvent.type(screen.getByLabelText("Número do documento"), "529.982.247-25");
    await userEvent.type(screen.getByLabelText("Telefone"), "16999");
    await userEvent.click(screen.getByRole("button", { name: "Salvar hóspede" }));
    await waitFor(() => expect(aoSalvar).toHaveBeenCalledWith(salvo));
    expect(chamadas[0].corpo).toEqual({ nome: "Ana Lima", documento_tipo: "CPF", documento_numero: "529.982.247-25", email: null, telefone: "16999" });
  });

  it("mostra a mensagem da API (CPF inválido) sem fechar", async () => {
    mockApi({ "POST /hospedes": { status: 422, body: { erro: "CPF inválido" } } });
    const aoSalvar = vi.fn();
    renderApp(<HospedeForm aoSalvar={aoSalvar} aoCancelar={() => {}} />);
    await userEvent.type(screen.getByLabelText("Nome completo"), "Ana Lima");
    await userEvent.type(screen.getByLabelText("Número do documento"), "123");
    await userEvent.type(screen.getByLabelText("E-mail"), "a@b.com");
    await userEvent.click(screen.getByRole("button", { name: "Salvar hóspede" }));
    expect(await screen.findByText("CPF inválido")).toBeInTheDocument();
    expect(aoSalvar).not.toHaveBeenCalled();
  });
});
