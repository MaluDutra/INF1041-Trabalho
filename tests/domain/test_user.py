"""Invariantes da entidade Usuário (SCRUM-11)."""

import pytest

from domain.entities.user import User
from domain.exceptions import ValidationError


def make_user(**overrides):
    data = {
        "display_name": "Ana",
        "email": "ana@x.com",
        "password_hash": "hash",
    }
    data.update(overrides)
    return User(**data)


def test_user_trims_the_display_name():  # SCRUM-11
    assert make_user(display_name="  Ana  ").display_name == "Ana"


@pytest.mark.parametrize("name", ["A", " A ", "", "   "])
def test_user_rejects_a_display_name_shorter_than_2(name):  # SCRUM-11
    with pytest.raises(ValidationError, match="nome de exibição"):
        make_user(display_name=name)


def test_user_accepts_display_names_at_both_limits():  # SCRUM-11
    assert make_user(display_name="Al").display_name == "Al"
    assert len(make_user(display_name="a" * 40).display_name) == 40


def test_user_rejects_a_display_name_longer_than_40():  # SCRUM-11
    with pytest.raises(ValidationError, match="nome de exibição"):
        make_user(display_name=f"  {'a' * 41}  ")


def test_user_counts_the_limit_after_trimming():  # SCRUM-11
    assert len(make_user(display_name=f" {'a' * 40} ").display_name) == 40


def test_user_stores_the_email_lowercase_and_trimmed():  # SCRUM-11
    assert make_user(email=" Ana@X.com ").email == "ana@x.com"


@pytest.mark.parametrize("email", ["", "   ", "ana", "ana@", "@x.com"])
def test_user_rejects_an_invalid_email(email):  # SCRUM-11
    with pytest.raises(ValidationError, match="e-mail"):
        make_user(email=email)


def test_two_users_may_share_the_display_name():  # SCRUM-11
    first = make_user(email="a@x.com")
    second = make_user(email="b@x.com")

    assert first.display_name == second.display_name


def test_valid_password_is_accepted():  # SCRUM-11
    User.validate_password("abcd1234")


@pytest.mark.parametrize(
    "password", ["abc1234", "abcdefgh", "12345678", "", "abc"]
)
def test_invalid_passwords_are_rejected_with_the_rule(password):  # SCRUM-11
    with pytest.raises(ValidationError, match="pelo menos 8 caracteres"):
        User.validate_password(password)
