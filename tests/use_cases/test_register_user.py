"""Casos de uso de cadastro, só com fakes (SCRUM-11)."""

import pytest

from domain.exceptions import ConflictError, ValidationError
from tests.fakes.fake_password_hasher import FakePasswordHasher
from tests.fakes.in_memory_user_repository import InMemoryUserRepository
from use_cases.dtos import RegisterUserInput
from use_cases.user.register_user import RegisterUser


@pytest.fixture
def repository():
    return InMemoryUserRepository()


@pytest.fixture
def register(repository):
    return RegisterUser(repository, FakePasswordHasher())


def data(**overrides):
    values = {
        "display_name": "Ana",
        "email": "ana@x.com",
        "password": "abcd1234",
    }
    values.update(overrides)
    return RegisterUserInput(**values)


def test_register_user_creates_the_account(register, repository):  # SCRUM-11
    created = register.execute(data())

    assert created.id is not None
    assert created.display_name == "Ana"
    stored = repository.get_by_id(created.id)
    assert stored.email == "ana@x.com"


def test_register_user_stores_only_the_hash(register, repository):  # SCRUM-11
    created = register.execute(data())

    stored = repository.get_by_id(created.id)
    assert stored.password_hash == FakePasswordHasher().hash("abcd1234")
    assert "abcd1234" not in stored.password_hash


def test_register_user_rejects_duplicate_email(register, repository):
    register.execute(data())  # SCRUM-11

    with pytest.raises(ConflictError):
        register.execute(data(display_name="Outra"))

    assert len(repository.list_all()) == 1


def test_register_user_treats_email_case_and_spaces_as_same(
    register, repository
):  # SCRUM-11
    register.execute(data())

    with pytest.raises(ConflictError):
        register.execute(data(email=" Ana@X.com "))

    assert len(repository.list_all()) == 1


def test_register_user_lowercases_the_email(register, repository):
    created = register.execute(data(email=" Bia@X.COM "))  # SCRUM-11

    assert repository.get_by_id(created.id).email == "bia@x.com"


@pytest.mark.parametrize(
    "password",
    ["abc1234", "abcdefgh", "12345678"],
    ids=["short", "no-digit", "no-letter"],
)
def test_register_user_rejects_weak_passwords(
    register, repository, password
):  # SCRUM-11
    with pytest.raises(ValidationError, match="pelo menos 8 caracteres"):
        register.execute(data(password=password))

    assert repository.list_all() == []


def test_register_user_accepts_a_password_at_the_limit(register):
    assert register.execute(data(password="abcd1234")).id  # SCRUM-11


@pytest.mark.parametrize("name", ["A", "a" * 41])
def test_register_user_rejects_display_names_out_of_range(
    register, repository, name
):  # SCRUM-11
    with pytest.raises(ValidationError, match="nome de exibição"):
        register.execute(data(display_name=name))

    assert repository.list_all() == []


def test_register_user_trims_the_display_name(register):
    created = register.execute(data(display_name="  Ana  "))  # SCRUM-11

    assert created.display_name == "Ana"


def test_register_user_allows_the_same_display_name_twice(register):
    first = register.execute(data(email="a@x.com"))  # SCRUM-11
    second = register.execute(data(email="b@x.com"))

    assert first.display_name == second.display_name
    assert first.id != second.id


def test_register_user_rejects_an_invalid_email(register, repository):
    with pytest.raises(ValidationError, match="e-mail"):  # SCRUM-11
        register.execute(data(email="sem-arroba"))

    assert repository.list_all() == []
