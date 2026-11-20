"""Factory Method: as invariantes da criação de reserva ficam num só lugar."""
from datetime import date
from decimal import Decimal

from app.models.reservaModel import Reserva


def calcular_valor_total(valor_diaria: Decimal, entrada: date, saida: date) -> Decimal:
    return (Decimal(valor_diaria) * (saida - entrada).days).quantize(Decimal("0.01"))


class ReservaFactory:
    @staticmethod
    def criar(dados, acomodacao, criada_por: int) -> Reserva:
        return Reserva(
            hospede_id=dados.hospede_id, acomodacao_id=acomodacao.id,
            data_entrada=dados.data_entrada, data_saida=dados.data_saida,
            qtd_hospedes=dados.qtd_hospedes, status="PENDENTE",
            valor_diaria=acomodacao.valor_diaria,   # cópia: mudar o preço não altera reservas existentes
            valor_total=calcular_valor_total(acomodacao.valor_diaria, dados.data_entrada, dados.data_saida),
            criada_por=criada_por)
