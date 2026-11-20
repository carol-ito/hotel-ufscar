import pytest
from pydantic import ValidationError

from app.dtos.hospedeDTO import HospedeIn

BASE = dict(nome="Ana Lima", documento_tipo="CPF", documento_numero="529.982.247-25", telefone="16999")


class HospedeDTOTest:
    def test_aceita_so_telefone_ou_so_email(self):
        assert HospedeIn(**BASE).email is None
        assert HospedeIn(**{**BASE, "telefone": None, "email": "a@b.com"}).telefone is None

    def test_exige_ao_menos_um_contato(self):
        with pytest.raises(ValidationError, match="ao menos um contato"):
            HospedeIn(**{**BASE, "telefone": None})

    def test_campos_vazios_viram_none(self):
        h = HospedeIn(**{**BASE, "email": "  ", "nome": "  Ana Lima "})
        assert h.email is None and h.nome == "Ana Lima"

    @pytest.mark.parametrize("campo,valor", [("email", "nao-e-email"), ("documento_tipo", "CNH"), ("nome", "A")])
    def test_rejeita_valores_invalidos(self, campo, valor):
        with pytest.raises(ValidationError):
            HospedeIn(**{**BASE, campo: valor})
