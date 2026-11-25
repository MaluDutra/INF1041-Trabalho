"""Filtros do catálogo (SCRUM-13) no caso de uso SearchCoffees."""

from datetime import date

import pytest

from domain.entities.coffee import Coffee
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from tests.fakes.in_memory_review_repository import (
    InMemoryReviewRepository,
)
from tests.use_cases.test_search_coffees import rate
from use_cases.coffee.search_coffees import SearchCoffees
from use_cases.coffee.search_criteria import term_criterion
from use_cases.coffee.search_filters import FILTER_CRITERION_FACTORIES
from use_cases.dtos import SearchCoffeesInput

FACTORIES = (term_criterion, *FILTER_CRITERION_FACTORIES)


def add(
    repository,
    name,
    origin=Origin.BRAZIL,
    process=None,
    roast=None,
    notes=(),
    added_at=date(2026, 1, 15),
):
    return repository.add(
        Coffee(
            name=name,
            roaster="Café Lá",
            origin=origin,
            added_at=added_at,
            process=process,
            roast=roast,
            sensory_notes=notes,
        )
    )


def search(repository, reviews=None, **fields):
    reviews = InMemoryReviewRepository() if reviews is None else reviews
    use_case = SearchCoffees(
        repository, reviews, criterion_factories=FACTORIES
    )
    return [
        result.name
        for result in use_case.execute(SearchCoffeesInput(**fields))
    ]


def test_origin_filter_matches_any_of_the_marked_origins():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(repository, "Bourbon", Origin.BRAZIL)
    add(repository, "Geisha", Origin.ETHIOPIA)
    add(repository, "Caturra", Origin.COLOMBIA)

    assert search(repository, origins=("Brasil", "Etiópia")) == [
        "Bourbon",
        "Geisha",
    ]
    assert search(repository, origins=("Colômbia",)) == ["Caturra"]


def test_process_filter_matches_any_marked_process_and_skips_empty():
    # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(repository, "Bourbon", process=Process.NATURAL)
    add(repository, "Geisha", process=Process.WASHED)
    add(repository, "Caturra", process=Process.HONEY)
    add(repository, "Blend")

    assert search(repository, processes=("Natural",)) == ["Bourbon"]
    assert search(repository, processes=("lavado", "Natural")) == [
        "Bourbon",
        "Geisha",
    ]


def test_roast_filter_matches_any_marked_roast_and_skips_empty():
    # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(repository, "Bourbon", roast=Roast.LIGHT)
    add(repository, "Geisha", roast=Roast.MEDIUM_DARK)
    add(repository, "Caturra", roast=Roast.DARK)
    add(repository, "Blend")

    assert search(repository, roasts=("Clara",)) == ["Bourbon"]
    assert search(repository, roasts=("escura", "média-escura")) == [
        "Caturra",
        "Geisha",
    ]


def test_sensory_note_filter_matches_coffee_with_any_marked_note():
    # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(
        repository,
        "Bourbon",
        notes=(SensoryNote.CHOCOLATE, SensoryNote.CARAMEL),
    )
    add(repository, "Geisha", notes=(SensoryNote.FLORAL, SensoryNote.FRUITY))
    add(repository, "Caturra", notes=(SensoryNote.NUTS,))
    add(repository, "Blend")

    assert search(repository, sensory_notes=("Caramelo",)) == ["Bourbon"]
    assert search(repository, sensory_notes=("frutado", "castanhas")) == [
        "Caturra",
        "Geisha",
    ]


def test_different_filters_combine_with_and():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(
        repository,
        "Alvo Um",
        Origin.BRAZIL,
        Process.NATURAL,
        notes=(SensoryNote.CHOCOLATE,),
    )
    add(
        repository,
        "Alvo Dois",
        Origin.ETHIOPIA,
        Process.NATURAL,
        notes=(SensoryNote.FRUITY, SensoryNote.FLORAL),
    )
    add(
        repository,
        "Outra origem",
        Origin.PERU,
        Process.NATURAL,
        notes=(SensoryNote.CHOCOLATE,),
    )
    add(
        repository,
        "Outro processo",
        Origin.BRAZIL,
        Process.WASHED,
        notes=(SensoryNote.CHOCOLATE,),
    )
    add(
        repository,
        "Outra nota",
        Origin.BRAZIL,
        Process.NATURAL,
        notes=(SensoryNote.NUTS,),
    )
    add(repository, "Sem atributos", Origin.BRAZIL)

    assert search(
        repository,
        origins=("Brasil", "Etiópia"),
        processes=("Natural",),
        sensory_notes=("Chocolate", "Frutado"),
    ) == ["Alvo Dois", "Alvo Um"]


def test_roast_combines_with_the_other_filters():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(repository, "Alvo", Origin.BRAZIL, roast=Roast.LIGHT)
    add(repository, "Outra torra", Origin.BRAZIL, roast=Roast.DARK)
    add(repository, "Outra origem", Origin.PERU, roast=Roast.LIGHT)

    assert search(repository, origins=("Brasil",), roasts=("Clara",)) == [
        "Alvo"
    ]


def test_filters_combine_with_the_term_and_the_sort():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    azul = add(repository, "Bourbon Azul", added_at=date(2026, 2, 1))
    rosa = add(repository, "Bourbon Rosa", added_at=date(2026, 1, 1))
    rate(reviews, azul, 3)
    rate(reviews, rosa, 5)
    add(repository, "Bourbon Ouro", Origin.PERU, added_at=date(2026, 3, 1))
    add(repository, "Geisha")

    assert search(
        repository, reviews, term="bourbon", origins=("Brasil",)
    ) == ["Bourbon Rosa", "Bourbon Azul"]
    assert search(
        repository,
        reviews,
        term="bourbon",
        origins=("Brasil",),
        sort="mais-recentes",
    ) == ["Bourbon Azul", "Bourbon Rosa"]
    assert search(
        repository, reviews, term="bourbon", sort="mais-recentes"
    ) == ["Bourbon Ouro", "Bourbon Azul", "Bourbon Rosa"]


def test_unknown_filter_values_are_ignored():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(repository, "Bourbon", Origin.BRAZIL)
    add(repository, "Geisha", Origin.ETHIOPIA)

    assert search(repository, origins=("Brasil", "Atlântida")) == ["Bourbon"]


def test_filter_with_only_unknown_values_does_not_filter():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(repository, "Bourbon", Origin.BRAZIL, Process.NATURAL)
    add(repository, "Geisha", Origin.ETHIOPIA)

    assert search(repository, origins=("Atlântida",), processes=("",)) == [
        "Bourbon",
        "Geisha",
    ]


def test_filter_values_ignore_accents_and_case():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(repository, "Geisha", Origin.ETHIOPIA)
    add(repository, "Bourbon", Origin.BRAZIL)

    assert search(repository, origins=("ETIOPIA",)) == ["Geisha"]


def test_filters_without_a_match_return_nothing():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(repository, "Bourbon", Origin.BRAZIL, Process.WASHED)

    assert (
        search(repository, origins=("Brasil",), processes=("Natural",)) == []
    )


@pytest.mark.parametrize("field", ["processes", "roasts", "sensory_notes"])
def test_coffee_without_the_attribute_fails_a_filter_on_it(field):
    # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add(repository, "Blend")
    values = {
        "processes": "Natural",
        "roasts": "Clara",
        "sensory_notes": "Floral",
    }

    assert search(repository, **{field: (values[field],)}) == []
