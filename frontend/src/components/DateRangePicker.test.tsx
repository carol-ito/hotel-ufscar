import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";
import DateRangePicker from "./DateRangePicker";

describe("DateRangePicker", () => {
  it("mostra as noites quando o período é válido", () => {
    render(<DateRangePicker entrada="2099-12-10" saida="2099-12-15" aoMudar={() => {}} />);
    expect(screen.getByText("5 noites")).toBeInTheDocument();
  });

  it("alerta saída igual ou anterior à entrada", () => {
    render(<DateRangePicker entrada="2099-12-10" saida="2099-12-10" aoMudar={() => {}} />);
    expect(screen.getByRole("alert")).toHaveTextContent("A saída deve ser depois da entrada");
  });

  it("alerta entrada no passado, a menos que seja permitido", () => {
    const { rerender } = render(<DateRangePicker entrada="2020-01-01" saida="2020-01-03" aoMudar={() => {}} />);
    expect(screen.getByText("A entrada não pode estar no passado")).toBeInTheDocument();
    rerender(<DateRangePicker entrada="2020-01-01" saida="2020-01-03" aoMudar={() => {}} permitirPassado />);
    expect(screen.queryByText("A entrada não pode estar no passado")).not.toBeInTheDocument();
  });

  it("ao avançar a entrada para depois da saída, empurra a saída para o dia seguinte", () => {
    const aoMudar = vi.fn();
    render(<DateRangePicker entrada="2099-12-10" saida="2099-12-12" aoMudar={aoMudar} />);
    const entrada = screen.getByLabelText("Entrada");
    fireEvent.change(entrada, { target: { value: "2099-12-20" } });
    expect(aoMudar).toHaveBeenLastCalledWith("2099-12-20", "2099-12-21");
  });
});
