from datetime import date

from sqlalchemy import exists, literal_column, select
from sqlalchemy.orm import Session

from app.models import Acomodacao, Caracteristica, Categoria, Reserva
from app.models.reservaModel import STATUS_VIVOS
from app.repositories.baseRepository import SqlRepository


def periodo(entrada, saida):
    """Mesma expressão da restrição ex_reserva_sem_sobreposicao: o PostgreSQL reaproveita o índice GiST."""
    from sqlalchemy import func
    return func.daterange(entrada, saida, literal_column("'[)'"))


def sobrepoe(a, b):
    return a.op("&&", is_comparison=True)(b)


class CategoriaRepository(SqlRepository[Categoria]):
    model = Categoria

    def listar(self) -> list[Categoria]:
        return list(self.session.scalars(select(Categoria).order_by(Categoria.nome)))


class CaracteristicaRepository(SqlRepository[Caracteristica]):
    model = Caracteristica

    def listar(self) -> list[Caracteristica]:
        return list(self.session.scalars(select(Caracteristica).order_by(Caracteristica.nome)))

    def por_ids(self, ids: list[int]) -> list[Caracteristica]:
        if not ids:
            return []
        return list(self.session.scalars(select(Caracteristica).where(Caracteristica.id.in_(ids))))


class AcomodacaoRepository(SqlRepository[Acomodacao]):
    model = Acomodacao

    def get_por_numero(self, numero: str) -> Acomodacao | None:
        return self.session.scalar(select(Acomodacao).where(Acomodacao.numero == numero))

    def listar(self, ativo: bool | None = None, categoria_id: int | None = None,
               status: str | None = None) -> list[Acomodacao]:
        consulta = select(Acomodacao).order_by(Acomodacao.numero)
        if ativo is not None:
            consulta = consulta.where(Acomodacao.ativo == ativo)
        if categoria_id is not None:
            consulta = consulta.where(Acomodacao.categoria_id == categoria_id)
        if status:
            consulta = consulta.where(Acomodacao.status == status)
        return list(self.session.scalars(consulta))

    def disponiveis(self, entrada: date, saida: date, hospedes: int,
                    categoria_id: int | None = None) -> list[Acomodacao]:
        """Ativas, com capacidade suficiente e sem reserva viva sobreposta ao período."""
        conflito = exists().where(
            Reserva.acomodacao_id == Acomodacao.id,
            Reserva.status.in_(STATUS_VIVOS),
            sobrepoe(periodo(Reserva.data_entrada, Reserva.data_saida), periodo(entrada, saida)))
        consulta = (select(Acomodacao)
                    .where(Acomodacao.ativo.is_(True), Acomodacao.capacidade >= hospedes, ~conflito)
                    .order_by(Acomodacao.valor_diaria, Acomodacao.numero))
        if categoria_id is not None:
            consulta = consulta.where(Acomodacao.categoria_id == categoria_id)
        return list(self.session.scalars(consulta))
