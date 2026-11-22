"""Entidade Usuário."""

import re
from dataclasses import dataclass

from domain.exceptions import ValidationError

DISPLAY_NAME_MIN = 2
DISPLAY_NAME_MAX = 40
PASSWORD_MIN = 8
_EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
PASSWORD_RULE = (
    f"A senha deve ter pelo menos {PASSWORD_MIN} caracteres, com pelo "
    "menos uma letra e um número."
)


@dataclass(frozen=True)
class User:
    """Pessoa com conta no Cafeteca.

    A entidade só valida o próprio estado e guarda apenas o hash da
    senha. O ``id`` é atribuído pelo repositório ao gravar. O e-mail é
    guardado em minúsculas e sem espaços nas pontas.
    """

    display_name: str
    email: str
    password_hash: str
    id: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "display_name", self._parse_name(self.display_name)
        )
        object.__setattr__(self, "email", self._parse_email(self.email))

    @staticmethod
    def validate_password(password: str) -> None:
        """Valida a regra da senha em texto, antes do hash."""
        if (
            len(password) < PASSWORD_MIN
            or not any(char.isalpha() for char in password)
            or not any(char.isdigit() for char in password)
        ):
            raise ValidationError(PASSWORD_RULE)

    @staticmethod
    def _parse_name(value: str) -> str:
        name = value.strip() if isinstance(value, str) else ""
        if not DISPLAY_NAME_MIN <= len(name) <= DISPLAY_NAME_MAX:
            raise ValidationError(
                "O nome de exibição deve ter entre "
                f"{DISPLAY_NAME_MIN} e {DISPLAY_NAME_MAX} caracteres."
            )
        return name

    @staticmethod
    def normalize_email(value: str) -> str:
        """Põe o e-mail em minúsculas e tira os espaços das pontas."""
        return value.strip().lower() if isinstance(value, str) else ""

    @staticmethod
    def _parse_email(value: str) -> str:
        email = User.normalize_email(value)
        if not _EMAIL_PATTERN.fullmatch(email):
            raise ValidationError("Informe um e-mail válido.")
        return email
