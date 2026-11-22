from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from domain.entities.coffee import Coffee
from domain.exceptions import ValidationError
from domain.value_objects.origin import Origin
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from use_cases.coffee.search_coffees import SearchCoffees
from use_cases.coffee.search_criteria import SearchCriterion, term_criterion
from use_cases.dtos import SearchCoffeesInput


def add_coffee(
    repository,
    name,
    roaster="Café Lá",
    origin=Origin.BRAZIL,
    producer=None,
):
    return repository.add(
        Coffee(
            name=name,
            roaster=roaster,
            origin=origin,
            added_at=date(2026, 1, 15),
            producer=producer,
        )
    )


def search_names(repository, term):
    results = SearchCoffees(repository).execute(SearchCoffeesInput(term))
    return [result.name for result in results]


def test_search_with_empty_term_returns_whole_catalog():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon", "Torra Cá", Origin.COLOMBIA)
    add_coffee(repository, "Geisha", "Café Lá", Origin.ETHIOPIA)

    results = SearchCoffees(repository).execute(SearchCoffeesInput())

    assert [(r.name, r.roaster, r.origin) for r in results] == [
        ("Bourbon", "Torra Cá", "Colômbia"),
        ("Geisha", "Café Lá", "Etiópia"),
    ]


def test_search_orders_by_normalized_name():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    for name in ["Zebra", "Éclair", "banana", "Abacaxi"]:
        add_coffee(repository, name)

    results = SearchCoffees(repository).execute(SearchCoffeesInput())

    assert [r.name for r in results] == [
        "Abacaxi",
        "banana",
        "Éclair",
        "Zebra",
    ]


def test_search_of_empty_catalog_returns_nothing():  # SCRUM-13
    assert (
        SearchCoffees(InMemoryCoffeeRepository()).execute(SearchCoffeesInput())
        == []
    )


def test_search_results_are_immutable_dtos():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    stored = add_coffee(repository, "Bourbon")

    (result,) = SearchCoffees(repository).execute(SearchCoffeesInput())

    assert result.id == stored.id
    with pytest.raises(FrozenInstanceError):
        result.name = "Outro"


def test_search_term_matches_name_ignoring_accents_and_case():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Sítio da Torre")
    add_coffee(repository, "Geisha")

    assert search_names(repository, "sitio") == ["Sítio da Torre"]


def test_search_term_is_matched_as_a_whole_phrase():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Sítio da Torre")

    assert search_names(repository, "SITIO DA") == ["Sítio da Torre"]
    assert search_names(repository, "torre sítio") == []


def test_search_term_matches_roaster():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon", roaster="Torrefação Ágata")
    add_coffee(repository, "Geisha", roaster="Café Lá")

    assert search_names(repository, "agata") == ["Bourbon"]


def test_search_term_matches_producer():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon", producer="Fazenda São João")
    add_coffee(repository, "Geisha")

    assert search_names(repository, "sao joao") == ["Bourbon"]


@pytest.mark.parametrize("term", ["a", " a ", "á"])
def test_search_rejects_a_term_with_one_useful_character(term):  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon")

    with pytest.raises(ValidationError, match="2 caracteres"):
        SearchCoffees(repository).execute(SearchCoffeesInput(term))


@pytest.mark.parametrize("term", ["", "   "])
def test_search_with_blank_term_returns_whole_catalog(term):  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon")
    add_coffee(repository, "Geisha")

    assert search_names(repository, term) == ["Bourbon", "Geisha"]


def test_search_without_a_match_returns_nothing():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon")

    assert search_names(repository, "inexistente") == []


def test_search_accepts_extra_criteria_without_changing_the_use_case():
    # SCRUM-13: OCP, filtros novos entram como novas fábricas
    class OnlyColombia(SearchCriterion):
        def matches(self, coffee):
            return coffee.origin == Origin.COLOMBIA

    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon", origin=Origin.COLOMBIA)
    add_coffee(repository, "Bourbon Rosa", origin=Origin.BRAZIL)
    use_case = SearchCoffees(
        repository, (term_criterion, lambda search: OnlyColombia())
    )

    results = use_case.execute(SearchCoffeesInput("bourbon"))

    assert [r.name for r in results] == ["Bourbon"]
