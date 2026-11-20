import { addDias, diaDaSemana, noitesEntre, periodoValido } from "./datas";

describe("datas", () => {
  it("soma dias atravessando mês e ano sem deslocar por fuso", () => {
    expect(addDias("2026-12-30", 3)).toBe("2027-01-02");
    expect(addDias("2026-03-01", -1)).toBe("2026-02-28");
  });
  it("conta noites com saída exclusiva", () => {
    expect(noitesEntre("2026-12-10", "2026-12-15")).toBe(5);
    expect(noitesEntre("2026-12-10", "2026-12-10")).toBe(0);
  });
  it("só aceita período com saída depois da entrada", () => {
    expect(periodoValido("2026-12-10", "2026-12-11")).toBe(true);
    expect(periodoValido("2026-12-10", "2026-12-10")).toBe(false);
    expect(periodoValido("2026-12-10", "2026-12-09")).toBe(false);
    expect(periodoValido("", "2026-12-09")).toBe(false);
  });
  it("dia da semana", () => expect(diaDaSemana("2026-11-06")).toBe("sex"));
});
