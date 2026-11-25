"""Origem: país onde o café foi cultivado (lista fechada)."""

from enum import Enum

from domain.value_objects.closed_set import parse_member


class Origin(Enum):
    BRAZIL = "Brasil"
    COLOMBIA = "Colômbia"
    COSTA_RICA = "Costa Rica"
    ETHIOPIA = "Etiópia"
    GUATEMALA = "Guatemala"
    HONDURAS = "Honduras"
    INDONESIA = "Indonésia"
    KENYA = "Quênia"
    PERU = "Peru"
    RWANDA = "Ruanda"

    @classmethod
    def parse(cls, label: "Origin | str") -> "Origin":
        """Converte o rótulo (sem diferenciar acentos e maiúsculas)."""
        return parse_member(cls, label, "Origem inválida.")
