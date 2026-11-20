from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.core.errors import RegraDeNegocioError
from app.domain.reservaFactory import calcular_valor_total

LIMITE_DIAS_MAPA = 62


@dataclass
class Disponivel:
    acomodacao: object
    noites: int
    valor_total: Decimal


class DisponibilidadeService:
    def __init__(self, acomodacoes, reservas, relogio):
        self.acomodacoes, self.reservas, self.relogio = acomodacoes, reservas, relogio

    def consultar(self, entrada: date, saida: date, hospedes: int,
                  categoria_id: int | None = None) -> list[Disponivel]:
        if saida <= entrada:
            raise RegraDeNegocioError("A data de saída deve ser posterior à de entrada")
        if entrada < self.relogio.hoje():
            raise RegraDeNegocioError("A data de entrada não pode estar no passado")
        if hospedes < 1:
            raise RegraDeNegocioError("Informe ao menos 1 hóspede")
        noites = (saida - entrada).days
        return [Disponivel(a, noites, calcular_valor_total(a.valor_diaria, entrada, saida))
                for a in self.acomodacoes.disponiveis(entrada, saida, hospedes, categoria_id)]

    def mapa(self, ini: date, fim: date):
        """Linhas do mapa de ocupação: cada acomodação ativa com suas reservas vivas no período."""
        if fim <= ini:
            raise RegraDeNegocioError("O fim do período deve ser posterior ao início")
        if (fim - ini).days > LIMITE_DIAS_MAPA:
            raise RegraDeNegocioError(f"O mapa comporta no máximo {LIMITE_DIAS_MAPA} dias")
        por_acomodacao: dict[int, list] = {}
        for r in self.reservas.no_periodo(ini, fim):
            por_acomodacao.setdefault(r.acomodacao_id, []).append(r)
        return [(a, por_acomodacao.get(a.id, [])) for a in self.acomodacoes.listar(ativo=True)]
