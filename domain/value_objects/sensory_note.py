"""Nota sensorial: sabor ou aroma característico (lista fechada)."""

from enum import Enum

from domain.value_objects.closed_set import parse_member


class SensoryNote(Enum):
    CHOCOLATE = "Chocolate"
    CARAMEL = "Caramelo"
    NUTS = "Castanhas"
    FRUITY = "Frutado"
    CITRUS = "Cítrico"
    FLORAL = "Floral"
    RED_FRUITS = "Frutas vermelhas"
    SPICY = "Especiado"
    HONEY = "Mel"
    HERBAL = "Herbal"

    @classmethod
    def parse(cls, label: "SensoryNote | str") -> "SensoryNote":
        return parse_member(cls, label, "Nota sensorial inválida.")
