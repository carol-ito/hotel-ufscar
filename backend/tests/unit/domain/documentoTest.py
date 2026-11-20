import pytest

from app.core.errors import RegraDeNegocioError
from app.domain.documento import cpf_valido, normalizar_documento


class DocumentoTest:
    def test_cpf_valido_com_e_sem_mascara(self):
        assert cpf_valido("529.982.247-25") and cpf_valido("52998224725")

    @pytest.mark.parametrize("cpf", ["111.111.111-11", "529.982.247-24", "123", ""])
    def test_cpf_invalido(self, cpf):
        assert not cpf_valido(cpf)

    def test_normaliza_cpf_para_so_digitos_e_outros_para_maiusculo(self):
        assert normalizar_documento("CPF", "529.982.247-25") == "52998224725"
        assert normalizar_documento("PASSAPORTE", " ab123 ") == "AB123"

    def test_rejeita_cpf_invalido_e_documento_vazio(self):
        with pytest.raises(RegraDeNegocioError):
            normalizar_documento("CPF", "123")
        with pytest.raises(RegraDeNegocioError):
            normalizar_documento("RG", "   ")
