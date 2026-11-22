"""Filtros do catálogo como critérios de busca plugáveis (OCP).

Cada filtro marca valores de um conjunto fechado do domínio. Dentro do
filtro os valores combinam com OU; ``SearchCoffees`` combina os filtros
entre si com E, sem conhecer estas classes.
"""

from collections.abc import Collection

from domain.entities.coffee import Coffee
from domain.exceptions import ValidationError
from domain.value_objects.coffee_rating import CoffeeRating
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
from use_cases.coffee.search_criteria import (
    CriterionFactory,
    SearchCriterion,
)
from use_cases.dtos import SearchCoffeesInput


class OriginCriterion(SearchCriterion):
    """O café vem de qualquer uma das origens marcadas."""

    def __init__(self, origins: Collection[Origin]) -> None:
        self._origins = frozenset(origins)

    def matches(self, coffee: Coffee, rating: CoffeeRating) -> bool:
        return coffee.origin in self._origins


def origin_criterion(search: SearchCoffeesInput) -> SearchCriterion | None:
    origins = _known_members(Origin, search.origins)
    return OriginCriterion(origins) if origins else None


class ProcessCriterion(SearchCriterion):
    """O café tem um dos processos marcados; sem processo, não passa."""

    def __init__(self, processes: Collection[Process]) -> None:
        self._processes = frozenset(processes)

    def matches(self, coffee: Coffee, rating: CoffeeRating) -> bool:
        return coffee.process in self._processes


def process_criterion(search: SearchCoffeesInput) -> SearchCriterion | None:
    processes = _known_members(Process, search.processes)
    return ProcessCriterion(processes) if processes else None


class RoastCriterion(SearchCriterion):
    """O café tem uma das torras marcadas; sem torra, não passa."""

    def __init__(self, roasts: Collection[Roast]) -> None:
        self._roasts = frozenset(roasts)

    def matches(self, coffee: Coffee, rating: CoffeeRating) -> bool:
        return coffee.roast in self._roasts


def roast_criterion(search: SearchCoffeesInput) -> SearchCriterion | None:
    roasts = _known_members(Roast, search.roasts)
    return RoastCriterion(roasts) if roasts else None


class SensoryNoteCriterion(SearchCriterion):
    """O café tem qualquer uma das notas sensoriais marcadas."""

    def __init__(self, notes: Collection[SensoryNote]) -> None:
        self._notes = frozenset(notes)

    def matches(self, coffee: Coffee, rating: CoffeeRating) -> bool:
        return not self._notes.isdisjoint(coffee.sensory_notes)


def sensory_note_criterion(
    search: SearchCoffeesInput,
) -> SearchCriterion | None:
    notes = _known_members(SensoryNote, search.sensory_notes)
    return SensoryNoteCriterion(notes) if notes else None


def _known_members(enum_class, labels):
    """Membros que os rótulos nomeiam; os desconhecidos são ignorados."""
    members = []
    for label in labels:
        try:
            members.append(enum_class.parse(label))
        except ValidationError:
            continue
    return members


FILTER_CRITERION_FACTORIES: tuple[CriterionFactory, ...] = (
    origin_criterion,
    process_criterion,
    roast_criterion,
    sensory_note_criterion,
)
