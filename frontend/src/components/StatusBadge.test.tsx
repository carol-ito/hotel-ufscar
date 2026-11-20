import { render, screen } from "@testing-library/react";
import StatusBadge from "./StatusBadge";

it.each([["EM_ANDAMENTO", "Em andamento", "badge-em-andamento"], ["PENDENTE", "Pendente", "badge-pendente"], ["LIVRE", "Livre", "badge-livre"]])(
  "mostra %s como %s", (status, rotulo, classe) => {
    render(<StatusBadge status={status} />);
    expect(screen.getByText(rotulo)).toHaveClass(classe);
  });
