"""Conversão de rótulos para membros de conjuntos fechados (enums)."""

from enum import Enum

from domain.exceptions import ValidationError
from domain.text import normalize_text


def parse_member[E: Enum](
    enum_class: type[E], label: object, message: str
) -> E:
    """Devolve o membro cujo rótulo (``value``) casa com ``label``.

    A comparação ignora acentos e maiúsculas. Lança ``ValidationError``
    com ``message`` quando o rótulo não pertence ao conjunto.
    """
    if isinstance(label, enum_class):
        return label
    if isinstance(label, str):
        wanted = normalize_text(label)
        for member in enum_class:
            if normalize_text(member.value) == wanted:
                return member
    raise ValidationError(message)
