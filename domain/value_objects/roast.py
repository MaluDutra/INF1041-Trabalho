"""Torra: grau de torra do café (lista fechada)."""

from enum import Enum

from domain.value_objects.closed_set import parse_member


class Roast(Enum):
    LIGHT = "Clara"
    MEDIUM = "Média"
    MEDIUM_DARK = "Média-escura"
    DARK = "Escura"

    @classmethod
    def parse(cls, label: "Roast | str") -> "Roast":
        return parse_member(cls, label, "Torra inválida.")
