"""Contrato do port CoffeeRepository, verificado com o fake em memória.

O repositório SQLite cumpre o mesmo contrato (LSP): a restrição de
unicidade do banco recusa o mesmo par normalizado.
"""

from datetime import date

import pytest

from domain.entities.coffee import Coffee
from domain.exceptions import ConflictError
from domain.value_objects.origin import Origin
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)


def make_coffee(name, roaster):
    return Coffee(
        name=name,
        roaster=roaster,
        origin=Origin.BRAZIL,
        added_at=date(2026, 1, 15),
    )


def test_repository_rejects_same_normalized_name_and_roaster():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    repository.add(make_coffee("Sítio da Torre", "Café Lá"))

    with pytest.raises(ConflictError):
        repository.add(make_coffee("sitio da torre", "CAFÉ LA"))


def test_repository_assigns_an_id_to_the_stored_coffee():  # SCRUM-13
    repository = InMemoryCoffeeRepository()

    stored = repository.add(make_coffee("Sítio da Torre", "Café Lá"))

    assert stored.id is not None
    assert repository.list_all() == [stored]


def test_repository_finds_a_stored_coffee_by_id():  # SCRUM-12
    repository = InMemoryCoffeeRepository()
    stored = repository.add(make_coffee("Sítio da Torre", "Café Lá"))

    assert repository.get_by_id(stored.id) == stored


def test_repository_returns_none_for_an_unknown_id():  # SCRUM-12
    repository = InMemoryCoffeeRepository()

    assert repository.get_by_id(42) is None
