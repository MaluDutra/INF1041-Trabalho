"""Entidade Café."""

from dataclasses import dataclass
from datetime import date

from domain.exceptions import ValidationError
from domain.text import normalize_text
from domain.value_objects.origin import Origin


@dataclass(frozen=True)
class Coffee:
    """Produto de uma torrefação, identificado por (nome, torrefação).

    A entidade só valida o próprio estado. O ``id`` é atribuído pelo
    repositório ao gravar.
    """

    name: str
    roaster: str
    origin: Origin
    added_at: date
    id: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", self._required(self.name, "nome"))
        object.__setattr__(
            self, "roaster", self._required(self.roaster, "torrefação")
        )
        object.__setattr__(self, "origin", self._parse_origin(self.origin))

    @property
    def normalized_name(self) -> str:
        return normalize_text(self.name)

    @property
    def identity(self) -> tuple[str, str]:
        """Par (nome, torrefação) normalizado (ADR 0003)."""
        return self.normalized_name, normalize_text(self.roaster)

    @staticmethod
    def _required(value: str | None, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"O campo {field} é obrigatório.")
        return value.strip()

    @staticmethod
    def _parse_origin(value: Origin | str | None) -> Origin:
        if isinstance(value, Origin):
            return value
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("O campo origem é obrigatório.")
        return Origin.parse(value)
