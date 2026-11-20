import { dataBR, documentoBR, moeda } from "./format";

describe("format", () => {
  it("formata moeda em reais a partir de string decimal", () => {
    expect(moeda("1250.5").replace(/\s/g, " ")).toBe("R$ 1.250,50");
  });
  it("formata data ISO sem passar por Date", () => {
    expect(dataBR("2026-12-01")).toBe("01/12/2026");
    expect(dataBR(null)).toBe("—");
  });
  it("mascara CPF só quando tem 11 dígitos", () => {
    expect(documentoBR("CPF", "52998224725")).toBe("529.982.247-25");
    expect(documentoBR("PASSAPORTE", "AB123")).toBe("PASSAPORTE AB123");
  });
});
