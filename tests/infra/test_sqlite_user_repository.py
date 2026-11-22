"""O repositório SQLite de usuários cumpre o contrato do port (LSP)."""

import pytest

from domain.entities.user import User
from domain.exceptions import ConflictError
from infra.db.database import connect, init_schema
from infra.repositories.user_repository_sqlite import SqliteUserRepository


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    connection = connect(path)
    init_schema(connection)
    connection.close()
    return path


@pytest.fixture
def repository(db_path):
    return SqliteUserRepository(db_path)


def make_user(**overrides):
    data = {
        "display_name": "Ana",
        "email": "ana@x.com",
        "password_hash": "hash-da-ana",
    }
    data.update(overrides)
    return User(**data)


def test_round_trip_keeps_every_attribute(repository):  # SCRUM-11
    stored = repository.add(make_user())

    assert stored.id is not None
    assert repository.get_by_id(stored.id) == stored


def test_get_by_id_returns_none_for_unknown_id(repository):  # SCRUM-11
    assert repository.get_by_id(999) is None


def test_duplicate_email_is_rejected(repository):  # SCRUM-11
    repository.add(make_user())

    with pytest.raises(ConflictError):
        repository.add(make_user(display_name="Outra"))


def test_database_stores_the_hash_and_normalized_email(
    repository, db_path
):  # SCRUM-11
    repository.add(make_user(email=" Ana@X.com "))

    connection = connect(db_path)
    row = connection.execute("SELECT * FROM users").fetchone()
    connection.close()
    assert row["email"] == "ana@x.com"
    assert row["password_hash"] == "hash-da-ana"
    assert list(row.keys()) == ["id", "display_name", "email", "password_hash"]
