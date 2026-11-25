"""Consulta do usuário da sessão, só com fakes (SCRUM-11)."""

import pytest

from domain.exceptions import NotFoundError
from tests.fakes.fake_password_hasher import FakePasswordHasher
from tests.fakes.in_memory_user_repository import InMemoryUserRepository
from use_cases.dtos import RegisterUserInput
from use_cases.user.get_user import GetUser
from use_cases.user.register_user import RegisterUser


def test_get_user_returns_only_the_public_data():  # SCRUM-11
    repository = InMemoryUserRepository()
    created = RegisterUser(repository, FakePasswordHasher()).execute(
        RegisterUserInput("Ana", "ana@x.com", "abcd1234")
    )

    found = GetUser(repository).execute(created.id)

    assert found == created
    assert not hasattr(found, "email")


def test_get_user_raises_for_an_unknown_id():  # SCRUM-11
    with pytest.raises(NotFoundError):
        GetUser(InMemoryUserRepository()).execute(42)
