"""Status do quarto a partir das reservas vivas."""
from datetime import date


def calcular_status(vivas, hoje: date) -> str:
    """OCUPADO se alguma reserva está EM_ANDAMENTO; RESERVADO se uma CONFIRMADA cobre hoje
    (período [entrada, saída)); senão LIVRE. Reserva PENDENTE não prende o quarto."""
    if any(r.status == "EM_ANDAMENTO" for r in vivas):
        return "OCUPADO"
    if any(r.status == "CONFIRMADA" and r.data_entrada <= hoje < r.data_saida for r in vivas):
        return "RESERVADO"
    return "LIVRE"
