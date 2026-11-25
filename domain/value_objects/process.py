"""Processo: método de pós-colheita do café (lista fechada)."""

from enum import Enum

from domain.value_objects.closed_set import parse_member


class Process(Enum):
    NATURAL = "Natural"
    WASHED = "Lavado"
    HONEY = "Cereja descascado (Honey)"
    FERMENTED = "Fermentado"

    @classmethod
    def parse(cls, label: "Process | str") -> "Process":
        return parse_member(cls, label, "Processo inválido.")
