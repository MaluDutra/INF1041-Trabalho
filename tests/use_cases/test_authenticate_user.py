"""Caso de uso de login, só com fakes (SCRUM-11)."""

import pytest

from domain.exceptions import InvalidCredentialsError
from tests.fakes.fake_password_hasher import FakePasswordHasher
from tests.fakes.in_memory_user_repository import InMemoryUserRepository
from use_cases.dtos import AuthenticateUserInput, RegisterUserInput
from use_cases.user.authenticate_user import AuthenticateUser
from use_cases.user.register_user import RegisterUser


@pytest.fixture
def repository():
    return InMemoryUserRepository()


@pytest.fixture
def authenticate(repository):
    hasher = FakePasswordHasher()
    RegisterUser(repository, hasher).execute(
        RegisterUserInput(
            display_name="Ana", email="ana@x.com", password="abcd1234"
        )
    )
    return AuthenticateUser(repository, hasher)


def test_authenticate_user_returns_the_user_for_valid_credentials(
    authenticate,
):  # SCRUM-11
    user = authenticate.execute(
        AuthenticateUserInput(email="ana@x.com", password="abcd1234")
    )

    assert user.id == 1
    assert user.display_name == "Ana"


def test_authenticate_user_rejects_a_wrong_password(authenticate):
    with pytest.raises(InvalidCredentialsError):  # SCRUM-11
        authenticate.execute(
            AuthenticateUserInput(email="ana@x.com", password="errada123")
        )


def test_authenticate_user_gives_the_same_error_for_unknown_email(
    authenticate,
):  # SCRUM-11
    with pytest.raises(InvalidCredentialsError) as wrong_password:
        authenticate.execute(
            AuthenticateUserInput(email="ana@x.com", password="errada123")
        )
    with pytest.raises(InvalidCredentialsError) as unknown_email:
        authenticate.execute(
            AuthenticateUserInput(email="zé@x.com", password="abcd1234")
        )

    assert str(unknown_email.value) == str(wrong_password.value)


def test_authenticate_user_ignores_email_case_and_edge_spaces(
    authenticate,
):  # SCRUM-11
    user = authenticate.execute(
        AuthenticateUserInput(email="  Ana@X.COM ", password="abcd1234")
    )

    assert user.display_name == "Ana"


def test_authenticate_user_treats_a_malformed_email_as_invalid_credentials(
    authenticate,
):  # SCRUM-11
    with pytest.raises(InvalidCredentialsError):
        authenticate.execute(
            AuthenticateUserInput(email="sem-arroba", password="abcd1234")
        )
