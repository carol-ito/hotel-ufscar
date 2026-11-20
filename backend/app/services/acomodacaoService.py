from app.core.errors import DuplicidadeError, NaoEncontradoError, RegraDeNegocioError
from app.models import Acomodacao, Caracteristica, Categoria


class CatalogoService:
    """Categorias e características: dados de apoio do cadastro de acomodações."""

    def __init__(self, categorias, caracteristicas):
        self.categorias, self.caracteristicas = categorias, caracteristicas

    def listar_categorias(self):
        return self.categorias.listar()

    def criar_categoria(self, dados) -> Categoria:
        return self.categorias.add(Categoria(nome=dados.nome, descricao=dados.descricao))

    def atualizar_categoria(self, categoria_id: int, dados) -> Categoria:
        categoria = self.categorias.get(categoria_id)
        if categoria is None:
            raise NaoEncontradoError("Categoria não encontrada")
        categoria.nome, categoria.descricao = dados.nome, dados.descricao
        return self.categorias.salvar(categoria)

    def listar_caracteristicas(self):
        return self.caracteristicas.listar()

    def criar_caracteristica(self, dados) -> Caracteristica:
        return self.caracteristicas.add(Caracteristica(nome=dados.nome))

    def atualizar_caracteristica(self, caracteristica_id: int, dados) -> Caracteristica:
        item = self.caracteristicas.get(caracteristica_id)
        if item is None:
            raise NaoEncontradoError("Característica não encontrada")
        item.nome = dados.nome
        return self.caracteristicas.salvar(item)


class AcomodacaoService:
    def __init__(self, acomodacoes, categorias, caracteristicas, reservas, relogio):
        self.acomodacoes, self.categorias = acomodacoes, categorias
        self.caracteristicas, self.reservas, self.relogio = caracteristicas, reservas, relogio

    def listar(self, ativo=None, categoria_id=None, status=None):
        return self.acomodacoes.listar(ativo, categoria_id, status)

    def obter(self, acomodacao_id: int) -> Acomodacao:
        acomodacao = self.acomodacoes.get(acomodacao_id)
        if acomodacao is None:
            raise NaoEncontradoError("Acomodação não encontrada")
        return acomodacao

    def _resolver_dependencias(self, dados):
        if self.categorias.get(dados.categoria_id) is None:
            raise NaoEncontradoError("Categoria não encontrada")
        ids = sorted(set(dados.caracteristica_ids))
        itens = self.caracteristicas.por_ids(ids)
        if len(itens) != len(ids):
            raise NaoEncontradoError("Alguma característica informada não existe")
        return itens

    def criar(self, dados) -> Acomodacao:
        itens = self._resolver_dependencias(dados)
        if self.acomodacoes.get_por_numero(dados.numero):
            raise DuplicidadeError("Já existe uma acomodação com este número")
        acomodacao = Acomodacao(numero=dados.numero, categoria_id=dados.categoria_id,
                                capacidade=dados.capacidade, valor_diaria=dados.valor_diaria,
                                status="LIVRE", ativo=True)
        acomodacao.caracteristicas = itens
        return self.acomodacoes.add(acomodacao)

    def atualizar(self, acomodacao_id: int, dados) -> Acomodacao:
        acomodacao = self.obter(acomodacao_id)
        itens = self._resolver_dependencias(dados)
        existente = self.acomodacoes.get_por_numero(dados.numero)
        if existente is not None and existente.id != acomodacao.id:
            raise DuplicidadeError("Já existe uma acomodação com este número")
        vivas = self.reservas.vivas_a_partir_de(acomodacao.id, self.relogio.hoje())
        if any(r.qtd_hospedes > dados.capacidade for r in vivas):
            raise RegraDeNegocioError("Há reservas ativas com mais hóspedes do que a nova capacidade")
        acomodacao.numero, acomodacao.categoria_id = dados.numero, dados.categoria_id
        acomodacao.capacidade, acomodacao.valor_diaria = dados.capacidade, dados.valor_diaria
        acomodacao.caracteristicas = itens   # a diária das reservas existentes não muda (valor copiado)
        return self.acomodacoes.salvar(acomodacao)

    def definir_ativo(self, acomodacao_id: int, ativo: bool) -> Acomodacao:
        acomodacao = self.obter(acomodacao_id)
        if not ativo and self.reservas.vivas_a_partir_de(acomodacao.id, self.relogio.hoje()):
            raise RegraDeNegocioError("A acomodação tem reservas ativas; cancele ou conclua antes de inativar")
        acomodacao.ativo = ativo
        return self.acomodacoes.salvar(acomodacao)
