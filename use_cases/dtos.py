"""Dados de saída (e entrada) dos casos de uso, imutáveis."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CoffeeSummaryDTO:
    """Café como aparece nos cards do catálogo."""

    id: int
    name: str
    roaster: str
    origin: str


@dataclass(frozen=True)
class BrewRecommendationDTO:
    """Recomendação de preparo; o que faltar vem como ``None``."""

    method: str
    ratio: str | None
    grind: str | None
    temperature: str | None


@dataclass(frozen=True)
class CoffeeDetailsDTO:
    """Café completo, como aparece na página dele.

    Atributos opcionais vazios vêm como ``None`` (ou tupla vazia): o
    texto "Não informado" é formatação do presenter.
    """

    id: int
    name: str
    roaster: str
    origin: str
    producer: str | None
    variety: str | None
    process: str | None
    altitude: int | None
    roast: str | None
    sensory_notes: tuple[str, ...]
    photo_url: str | None
    story: str | None
    brew_recommendations: tuple[BrewRecommendationDTO, ...]
