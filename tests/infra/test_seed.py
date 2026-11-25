"""O seed do catálogo cobre os conjuntos fechados do domínio."""

from pathlib import Path

from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
from infra.db.seed import SEED_COFFEES, init_database
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)

STATIC_DIR = Path(__file__).parents[2] / "app" / "static"


def test_seed_has_about_twenty_coffees():  # SCRUM-12
    assert 18 <= len(SEED_COFFEES) <= 22


def test_seed_has_no_duplicate_identities():  # SCRUM-12
    identities = [coffee.identity for coffee in SEED_COFFEES]

    assert len(set(identities)) == len(identities)


def test_seed_covers_every_origin_process_roast_and_note():  # SCRUM-12
    assert {c.origin for c in SEED_COFFEES} == set(Origin)
    assert {c.process for c in SEED_COFFEES if c.process} == set(Process)
    assert {c.roast for c in SEED_COFFEES if c.roast} == set(Roast)
    assert {note for c in SEED_COFFEES for note in c.sensory_notes} == set(
        SensoryNote
    )


def test_seed_has_distinct_catalog_entry_dates():  # SCRUM-12
    dates = [coffee.added_at for coffee in SEED_COFFEES]

    assert len(set(dates)) == len(dates)


def test_seed_leaves_some_attributes_empty():  # SCRUM-12
    assert any(c.producer is None for c in SEED_COFFEES)
    assert any(c.variety is None for c in SEED_COFFEES)
    assert any(c.process is None for c in SEED_COFFEES)
    assert any(c.altitude is None for c in SEED_COFFEES)
    assert any(c.roast is None for c in SEED_COFFEES)
    assert any(not c.sensory_notes for c in SEED_COFFEES)
    assert any(c.story is None for c in SEED_COFFEES)
    assert any(c.photo_url is None for c in SEED_COFFEES)
    assert any(not c.brew_recommendations for c in SEED_COFFEES)
    assert any(
        brew.ratio is None or brew.grind is None or brew.temperature is None
        for c in SEED_COFFEES
        for brew in c.brew_recommendations
    )


def test_seed_photos_exist_as_static_files():  # SCRUM-12
    photos = {c.photo_url for c in SEED_COFFEES if c.photo_url}

    assert photos
    for photo in photos:
        assert (STATIC_DIR / photo.removeprefix("/static/")).is_file()


def test_init_database_persists_the_whole_seed(tmp_path):  # SCRUM-12
    db_path = tmp_path / "seed.db"

    assert init_database(db_path) is True

    stored = SqliteCoffeeRepository(db_path).list_all()
    assert len(stored) == len(SEED_COFFEES)
    assert init_database(db_path) is False
