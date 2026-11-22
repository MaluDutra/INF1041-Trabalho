"""Contrato de get_by_id, update e delete do ReviewRepository.

O fake em memória e o repositório SQLite passam pelos mesmos testes: um
substitui o outro sem o caso de uso notar (LSP).
"""

from dataclasses import replace
from datetime import date, datetime

import pytest

from domain.entities.coffee import Coffee
from domain.entities.review import Review
from domain.entities.user import User
from domain.exceptions import NotFoundError
from domain.value_objects.origin import Origin
from infra.db.database import connect, init_schema
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)
from infra.repositories.review_repository_sqlite import (
    SqliteReviewRepository,
)
from infra.repositories.user_repository_sqlite import SqliteUserRepository
from tests.fakes.in_memory_review_repository import (
    InMemoryReviewRepository,
)

NOW = datetime(2026, 3, 10, 14, 30, 5)


@pytest.fixture
def sqlite_db(tmp_path):
    path = tmp_path / "contract.db"
    connection = connect(path)
    init_schema(connection)
    connection.close()
    SqliteUserRepository(path).add(User("Ana", "ana@x.com", "h"))
    SqliteCoffeeRepository(path).add(
        Coffee(
            name="Blend",
            roaster="Café Lá",
            origin=Origin.BRAZIL,
            added_at=date(2026, 1, 15),
        )
    )
    return path


@pytest.fixture(params=["memory", "sqlite"])
def repository(request, sqlite_db):
    if request.param == "memory":
        return InMemoryReviewRepository()
    return SqliteReviewRepository(sqlite_db)


@pytest.fixture
def stored(repository):
    return repository.add(
        Review(
            author_id=1,
            coffee_id=1,
            rating=3,
            text="Ok",
            created_at=NOW,
        )
    )


def test_get_by_id_returns_the_stored_review(repository, stored):
    # SCRUM-14
    assert repository.get_by_id(stored.id) == stored


def test_get_by_id_returns_none_when_missing(repository):  # SCRUM-14
    assert repository.get_by_id(999) is None


def test_update_persists_rating_text_and_edited_flag(repository, stored):
    # SCRUM-14
    changed = stored.edit(rating=5, text="Melhor")

    result = repository.update(changed)

    assert result == changed
    found = repository.get_by_id(stored.id)
    assert (found.rating, found.text, found.edited) == (5, "Melhor", True)
    assert found.created_at == NOW


def test_update_can_clear_the_text(repository, stored):  # SCRUM-14
    repository.update(stored.edit(rating=3, text=None))

    assert repository.get_by_id(stored.id).text is None


def test_update_of_a_missing_review_raises_not_found(repository, stored):
    # SCRUM-14
    ghost = replace(stored, id=999)

    with pytest.raises(NotFoundError):
        repository.update(ghost)


def test_delete_removes_the_review(repository, stored):  # SCRUM-14
    repository.delete(stored.id)

    assert repository.get_by_id(stored.id) is None
    assert repository.list_by_coffee(1) == []
    assert repository.list_ratings_by_coffee(1) == []


def test_delete_frees_the_author_to_review_again(repository, stored):
    # SCRUM-14 / ADR 0002
    repository.delete(stored.id)

    again = repository.add(
        Review(author_id=1, coffee_id=1, rating=2, text=None, created_at=NOW)
    )

    assert again.rating == 2


def test_delete_of_a_missing_review_raises_not_found(repository):
    # SCRUM-14
    with pytest.raises(NotFoundError):
        repository.delete(999)
