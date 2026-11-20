from app.core.errors import DuplicidadeError, NaoEncontradoError
from app.domain.documento import normalizar_documento
from app.models import Hospede


class HospedeService:
    def __init__(self, hospedes):
        self.hospedes = hospedes

    def listar(self, q: str | None, limite: int, offset: int):
        return self.hospedes.buscar(q, limite, offset)

    def obter(self, hospede_id: int) -> Hospede:
        hospede = self.hospedes.get(hospede_id)
        if hospede is None:
            raise NaoEncontradoError("Hóspede não encontrado")
        return hospede

    def criar(self, dados) -> Hospede:
        numero = normalizar_documento(dados.documento_tipo, dados.documento_numero)
        if self.hospedes.get_por_documento(dados.documento_tipo, numero):
            raise DuplicidadeError("Já existe um hóspede com este documento")
        return self.hospedes.add(Hospede(
            nome=dados.nome, documento_tipo=dados.documento_tipo, documento_numero=numero,
            email=dados.email, telefone=dados.telefone))

    def atualizar(self, hospede_id: int, dados) -> Hospede:
        hospede = self.obter(hospede_id)
        numero = normalizar_documento(dados.documento_tipo, dados.documento_numero)
        existente = self.hospedes.get_por_documento(dados.documento_tipo, numero)
        if existente is not None and existente.id != hospede.id:
            raise DuplicidadeError("Já existe um hóspede com este documento")
        hospede.nome, hospede.documento_tipo, hospede.documento_numero = dados.nome, dados.documento_tipo, numero
        hospede.email, hospede.telefone = dados.email, dados.telefone
        return self.hospedes.salvar(hospede)
