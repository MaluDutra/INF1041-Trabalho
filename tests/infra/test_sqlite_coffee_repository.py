"""O repositório SQLite cumpre o contrato do port (LSP)."""

from datetime import date

import pytest

from domain.entities.coffee import Coffee
from domain.exceptions import ConflictError
from domain.value_objects.brew_recommendation import BrewRecommendation
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
from infra.db.database import connect, init_schema
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)


@pytest.fixture
def repository(tmp_path):
    db_path = tmp_path / "test.db"
    connection = connect(db_path)
    init_schema(connection)
    connection.close()
    return SqliteCoffeeRepository(db_path)


def full_coffee(**overrides):
    data = {
        "name": "Sítio da Torre",
        "roaster": "Café Lá",
        "origin": Origin.BRAZIL,
        "added_at": date(2026, 1, 15),
        "producer": "Família Silva",
        "variety": "Bourbon",
        "process": Process.HONEY,
        "altitude": 1100,
        "roast": Roast.MEDIUM_DARK,
        "sensory_notes": (SensoryNote.NUTS, SensoryNote.CARAMEL),
        "photo_url": "/static/photos/a.svg",
        "story": "Uma história.",
        "brew_recommendations": (
            BrewRecommendation("V60", "1:15", "Média", "92 °C"),
            BrewRecommendation("Prensa francesa"),
        ),
    }
    data.update(overrides)
    return Coffee(**data)


def test_round_trip_keeps_every_attribute(repository):  # SCRUM-12
    stored = repository.add(full_coffee())

    assert repository.get_by_id(stored.id) == stored
    assert repository.list_all() == [stored]


def test_round_trip_of_a_coffee_with_only_required_fields(
    repository,
):  # SCRUM-12
    stored = repository.add(
        full_coffee(
            producer=None,
            variety=None,
            process=None,
            altitude=None,
            roast=None,
            sensory_notes=(),
            photo_url=None,
            story=None,
            brew_recommendations=(),
        )
    )

    assert repository.get_by_id(stored.id) == stored


def test_get_by_id_returns_none_for_unknown_id(repository):  # SCRUM-12
    assert repository.get_by_id(999) is None


def test_sensory_notes_and_brews_keep_their_order(repository):  # SCRUM-12
    other = full_coffee(
        name="Outro",
        sensory_notes=(SensoryNote.HERBAL, SensoryNote.CHOCOLATE),
    )
    first = repository.add(full_coffee())
    second = repository.add(other)

    by_id = {coffee.id: coffee for coffee in repository.list_all()}
    assert by_id[first.id].sensory_notes == first.sensory_notes
    assert by_id[second.id].sensory_notes == second.sensory_notes
    assert by_id[first.id].brew_recommendations == (first.brew_recommendations)


def test_duplicate_identity_is_rejected_and_leaves_no_orphans(
    repository,
):  # SCRUM-12
    repository.add(full_coffee())

    with pytest.raises(ConflictError):
        repository.add(full_coffee(name="sitio da torre"))

    assert len(repository.list_all()) == 1
