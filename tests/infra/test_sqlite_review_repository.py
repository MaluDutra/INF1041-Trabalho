"""O repositório SQLite de reviews cumpre o contrato do port (LSP)."""

from datetime import date, datetime

import pytest

from domain.entities.coffee import Coffee
from domain.entities.review import Review
from domain.entities.user import User
from domain.exceptions import ConflictError
from domain.value_objects.origin import Origin
from infra.db.database import connect, init_schema
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)
from infra.repositories.review_repository_sqlite import (
    SqliteReviewRepository,
)
from infra.repositories.user_repository_sqlite import SqliteUserRepository

NOW = datetime(2026, 3, 10, 14, 30, 5)


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    connection = connect(path)
    init_schema(connection)
    connection.close()
    return path


@pytest.fixture
def repository(db_path):
    return SqliteReviewRepository(db_path)


@pytest.fixture
def user(db_path):
    return SqliteUserRepository(db_path).add(User("Ana", "ana@x.com", "h"))


@pytest.fixture
def coffee(db_path):
    return SqliteCoffeeRepository(db_path).add(
        Coffee(
            name="Blend",
            roaster="Café Lá",
            origin=Origin.BRAZIL,
            added_at=date(2026, 1, 15),
        )
    )


def make_review(user, coffee, **overrides):
    data = {
        "author_id": user.id,
        "coffee_id": coffee.id,
        "rating": 4,
        "text": "Bom.",
        "created_at": NOW,
    }
    data.update(overrides)
    return Review(**data)


def test_round_trip_keeps_every_attribute(repository, user, coffee):
    # SCRUM-14
    stored = repository.add(make_review(user, coffee))

    assert stored.id is not None
    assert repository.get_by_author_and_coffee(user.id, coffee.id) == stored
    assert stored.created_at == NOW
    assert stored.edited is False


def test_review_without_text_round_trips_as_none(
    repository, user, coffee
):  # SCRUM-14
    repository.add(make_review(user, coffee, text=None))

    found = repository.get_by_author_and_coffee(user.id, coffee.id)

    assert found.text is None


def test_get_by_author_and_coffee_returns_none_when_missing(
    repository, user, coffee
):  # SCRUM-14
    assert repository.get_by_author_and_coffee(user.id, coffee.id) is None


def test_second_review_of_the_same_user_and_coffee_is_rejected(
    repository, user, coffee
):  # SCRUM-14
    repository.add(make_review(user, coffee))

    with pytest.raises(ConflictError):
        repository.add(make_review(user, coffee, rating=1))

    assert len(repository.list_by_coffee(coffee.id)) == 1


def test_list_by_coffee_returns_only_that_coffee(
    repository, user, coffee, db_path
):  # SCRUM-14
    other = SqliteCoffeeRepository(db_path).add(
        Coffee(
            name="Outro",
            roaster="Café Lá",
            origin=Origin.PERU,
            added_at=date(2026, 1, 16),
        )
    )
    mine = repository.add(make_review(user, coffee))
    repository.add(make_review(user, other))

    assert repository.list_by_coffee(coffee.id) == [mine]


def test_database_rejects_a_review_of_an_unknown_coffee(
    repository, user
):  # SCRUM-14
    unknown = Coffee(
        name="X",
        roaster="Y",
        origin=Origin.BRAZIL,
        added_at=date(2026, 1, 1),
        id=999,
    )

    with pytest.raises(Exception, match="FOREIGN KEY"):
        repository.add(make_review(user, unknown))


def test_unique_constraint_lives_in_the_database(db_path, user, coffee):
    # SCRUM-14 / ADR 0002
    connection = connect(db_path)
    sql = (
        "INSERT INTO reviews (user_id, coffee_id, rating, text, created_at)"
        " VALUES (?, ?, 4, NULL, '2026-03-10T14:30:05')"
    )
    connection.execute(sql, (user.id, coffee.id))
    with pytest.raises(Exception, match="UNIQUE"):
        connection.execute(sql, (user.id, coffee.id))
    connection.close()
