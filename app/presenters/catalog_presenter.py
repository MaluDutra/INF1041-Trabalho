"""Formata a lista de cafés e as opções de ordenação para a home."""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from app.presenters.rating_presenter import format_rating_summary
from use_cases.coffee.search_sorting import SortStrategy
from use_cases.dtos import CoffeeSummaryDTO


@dataclass(frozen=True)
class CoffeeCardView:
    id: int
    name: str
    roaster: str
    origin: str
    rating_summary: str


@dataclass(frozen=True)
class SortOptionView:
    id: str
    label: str
    selected: bool


def present_cards(
    summaries: Iterable[CoffeeSummaryDTO],
) -> list[CoffeeCardView]:
    return [
        CoffeeCardView(
            id=summary.id,
            name=summary.name,
            roaster=summary.roaster,
            origin=summary.origin,
            rating_summary=format_rating_summary(summary.rating),
        )
        for summary in summaries
    ]


def present_sort_options(
    strategies: Sequence[SortStrategy], chosen: str
) -> tuple[SortOptionView, ...]:
    """Marca a ordenação escolhida; valor desconhecido marca a padrão.

    A padrão é a primeira estratégia, a mesma que ``SearchCoffees`` usa.
    """
    known = {strategy.id for strategy in strategies}
    selected = chosen if chosen in known else strategies[0].id
    return tuple(
        SortOptionView(strategy.id, strategy.label, strategy.id == selected)
        for strategy in strategies
    )
