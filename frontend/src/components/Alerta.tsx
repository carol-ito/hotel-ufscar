import { ReactNode } from "react";

interface Props { tipo?: "erro" | "sucesso" | "info"; children: ReactNode }

export default function Alerta({ tipo = "erro", children }: Props) {
  return <div className={`alerta alerta-${tipo}`} role={tipo === "erro" ? "alert" : "status"}>{children}</div>;
}
