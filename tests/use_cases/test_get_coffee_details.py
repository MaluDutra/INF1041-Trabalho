from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from domain.entities.coffee import Coffee
from domain.exceptions import NotFoundError
from domain.value_objects.brew_recommendation import BrewRecommendation
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from use_cases.coffee.get_coffee_details import GetCoffeeDetails


def full_coffee():
    return Coffee(
        name="Sítio da Torre",
        roaster="Café Lá",
        origin=Origin.BRAZIL,
        added_at=date(2026, 1, 15),
        producer="Família Silva",
        variety="Bourbon Amarelo",
        process=Process.NATURAL,
        altitude=1100,
        roast=Roast.MEDIUM,
        sensory_notes=(SensoryNote.CHOCOLATE, SensoryNote.CARAMEL),
        photo_url="/static/photos/torra-media.svg",
        story="Cultivado há três gerações.",
        brew_recommendations=(
            BrewRecommendation(
                method="V60",
                ratio="1:15",
                grind="Média",
                temperature="92 °C",
            ),
            BrewRecommendation(method="Prensa francesa"),
        ),
    )


def test_get_details_returns_every_attribute_of_the_coffee():  # SCRUM-12
    repository = InMemoryCoffeeRepository()
    stored = repository.add(full_coffee())

    details = GetCoffeeDetails(repository).execute(stored.id)

    assert details.id == stored.id
    assert details.name == "Sítio da Torre"
    assert details.roaster == "Café Lá"
    assert details.origin == "Brasil"
    assert details.producer == "Família Silva"
    assert details.variety == "Bourbon Amarelo"
    assert details.process == "Natural"
    assert details.altitude == 1100
    assert details.roast == "Média"
    assert details.sensory_notes == ("Chocolate", "Caramelo")
    assert details.photo_url == "/static/photos/torra-media.svg"
    assert details.story == "Cultivado há três gerações."
    assert [
        (b.method, b.ratio, b.grind, b.temperature)
        for b in details.brew_recommendations
    ] == [
        ("V60", "1:15", "Média", "92 °C"),
        ("Prensa francesa", None, None, None),
    ]


def test_get_details_leaves_missing_attributes_empty():  # SCRUM-12
    repository = InMemoryCoffeeRepository()
    stored = repository.add(
        Coffee(
            name="Blend",
            roaster="Café Lá",
            origin=Origin.BRAZIL,
            added_at=date(2026, 1, 15),
        )
    )

    details = GetCoffeeDetails(repository).execute(stored.id)

    assert details.producer is None
    assert details.variety is None
    assert details.process is None
    assert details.altitude is None
    assert details.roast is None
    assert details.sensory_notes == ()
    assert details.photo_url is None
    assert details.story is None
    assert details.brew_recommendations == ()


def test_get_details_of_unknown_id_raises_not_found():  # SCRUM-12
    repository = InMemoryCoffeeRepository()
    repository.add(full_coffee())

    with pytest.raises(NotFoundError):
        GetCoffeeDetails(repository).execute(999)


def test_details_dto_is_immutable():  # SCRUM-12
    repository = InMemoryCoffeeRepository()
    stored = repository.add(full_coffee())

    details = GetCoffeeDetails(repository).execute(stored.id)

    with pytest.raises(FrozenInstanceError):
        details.name = "Outro"
