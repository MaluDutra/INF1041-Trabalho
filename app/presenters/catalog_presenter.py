"""Formata cafés, ordenações e filtros do catálogo para a home."""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum

from app.presenters.rating_presenter import format_rating_summary
from domain.exceptions import ValidationError
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
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


@dataclass(frozen=True)
class FilterField:
    """Um filtro da tela: parâmetro do endereço, campo do pedido e o
    conjunto fechado do domínio que fornece as opções."""

    param: str
    input_field: str
    label: str
    members: type[Enum]


FILTER_FIELDS: tuple[FilterField, ...] = (
    FilterField("origem", "origins", "Origem", Origin),
    FilterField("processo", "processes", "Processo", Process),
    FilterField("torra", "roasts", "Torra", Roast),
    FilterField("nota", "sensory_notes", "Nota sensorial", SensoryNote),
)


@dataclass(frozen=True)
class FilterOptionView:
    value: str
    checked: bool


@dataclass(frozen=True)
class FilterGroupView:
    param: str
    label: str
    options: tuple[FilterOptionView, ...]


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


def present_filter_groups(
    selected: Mapping[str, Sequence[str]],
) -> tuple[FilterGroupView, ...]:
    """Um grupo por filtro, com as opções vindas do domínio.

    Rótulos selecionados que não pertencem ao conjunto são ignorados,
    como faz o caso de uso.
    """
    return tuple(
        FilterGroupView(
            field.param,
            field.label,
            _present_options(field, selected.get(field.param, ())),
        )
        for field in FILTER_FIELDS
    )


def has_active_filters(groups: Iterable[FilterGroupView]) -> bool:
    return any(option.checked for g in groups for option in g.options)


def _present_options(
    field: FilterField, labels: Sequence[str]
) -> tuple[FilterOptionView, ...]:
    chosen = set()
    for label in labels:
        try:
            chosen.add(field.members.parse(label))
        except ValidationError:
            continue
    return tuple(
        FilterOptionView(member.value, member in chosen)
        for member in field.members
    )
