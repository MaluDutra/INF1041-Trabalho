"""Origem: país onde o café foi cultivado (lista fechada)."""

from enum import Enum

from domain.exceptions import ValidationError
from domain.text import normalize_text


class Origin(Enum):
    BRAZIL = "Brasil"
    COLOMBIA = "Colômbia"
    ETHIOPIA = "Etiópia"
    GUATEMALA = "Guatemala"
    KENYA = "Quênia"

    @classmethod
    def parse(cls, label: str) -> "Origin":
        """Converte o rótulo (sem diferenciar acentos e maiúsculas)."""
        wanted = normalize_text(label)
        for origin in cls:
            if normalize_text(origin.value) == wanted:
                return origin
        raise ValidationError("Origem inválida.")
