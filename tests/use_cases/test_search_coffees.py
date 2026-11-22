from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from domain.entities.coffee import Coffee
from domain.value_objects.origin import Origin
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from use_cases.coffee.search_coffees import SearchCoffees


def add_coffee(repository, name, roaster="Café Lá", origin=Origin.BRAZIL):
    return repository.add(
        Coffee(
            name=name,
            roaster=roaster,
            origin=origin,
            added_at=date(2026, 1, 15),
        )
    )


def test_search_with_empty_term_returns_whole_catalog():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon", "Torra Cá", Origin.COLOMBIA)
    add_coffee(repository, "Geisha", "Café Lá", Origin.ETHIOPIA)

    results = SearchCoffees(repository).execute()

    assert [(r.name, r.roaster, r.origin) for r in results] == [
        ("Bourbon", "Torra Cá", "Colômbia"),
        ("Geisha", "Café Lá", "Etiópia"),
    ]


def test_search_orders_by_normalized_name():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    for name in ["Zebra", "Éclair", "banana", "Abacaxi"]:
        add_coffee(repository, name)

    results = SearchCoffees(repository).execute()

    assert [r.name for r in results] == [
        "Abacaxi",
        "banana",
        "Éclair",
        "Zebra",
    ]


def test_search_of_empty_catalog_returns_nothing():  # SCRUM-13
    assert SearchCoffees(InMemoryCoffeeRepository()).execute() == []


def test_search_results_are_immutable_dtos():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    stored = add_coffee(repository, "Bourbon")

    (result,) = SearchCoffees(repository).execute()

    assert result.id == stored.id
    with pytest.raises(FrozenInstanceError):
        result.name = "Outro"
