"""Normalização e validação de documentos do hóspede."""
import re

from app.core.errors import RegraDeNegocioError


def so_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor)


def cpf_valido(cpf: str) -> bool:
    d = so_digitos(cpf)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(d[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10 % 11) % 10
        if digito != int(d[tamanho]):
            return False
    return True


def normalizar_documento(tipo: str, numero: str) -> str:
    """CPF é guardado só com dígitos (e validado); os demais, sem espaços nas pontas."""
    numero = numero.strip()
    if tipo == "CPF":
        if not cpf_valido(numero):
            raise RegraDeNegocioError("CPF inválido")
        return so_digitos(numero)
    if not numero:
        raise RegraDeNegocioError("Número do documento é obrigatório")
    return numero.upper() if tipo == "PASSAPORTE" else numero
