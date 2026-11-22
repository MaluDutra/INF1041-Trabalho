"""Dados de saída (e entrada) dos casos de uso, imutáveis."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CoffeeSummaryDTO:
    """Café como aparece nos cards do catálogo."""

    id: int
    name: str
    roaster: str
    origin: str
