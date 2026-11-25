"""Entidade Café."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from domain.exceptions import ValidationError
from domain.text import normalize_text
from domain.value_objects.brew_recommendation import BrewRecommendation
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote


@dataclass(frozen=True)
class Coffee:
    """Produto de uma torrefação, identificado por (nome, torrefação).

    A entidade só valida o próprio estado. O ``id`` é atribuído pelo
    repositório ao gravar. Os atributos opcionais vazios ficam como
    ``None`` (ou tupla vazia); como exibi-los é assunto das camadas
    externas.
    """

    name: str
    roaster: str
    origin: Origin
    added_at: date
    id: int | None = None
    producer: str | None = None
    variety: str | None = None
    process: Process | None = None
    altitude: int | None = None
    roast: Roast | None = None
    sensory_notes: tuple[SensoryNote, ...] = ()
    photo_url: str | None = None
    story: str | None = None
    brew_recommendations: tuple[BrewRecommendation, ...] = ()

    def __post_init__(self) -> None:
        self._set("name", self._required(self.name, "nome"))
        self._set("roaster", self._required(self.roaster, "torrefação"))
        self._set("origin", self._parse_origin(self.origin))
        for field in ("producer", "variety", "photo_url", "story"):
            self._set(field, self._optional_text(getattr(self, field)))
        self._set("process", self._optional_member(Process, self.process))
        self._set("roast", self._optional_member(Roast, self.roast))
        self._set("altitude", self._parse_altitude(self.altitude))
        self._set("sensory_notes", self._parse_notes(self.sensory_notes))
        self._set(
            "brew_recommendations",
            self._parse_brews(self.brew_recommendations),
        )

    @property
    def normalized_name(self) -> str:
        return normalize_text(self.name)

    @property
    def identity(self) -> tuple[str, str]:
        """Par (nome, torrefação) normalizado (ADR 0003)."""
        return self.normalized_name, normalize_text(self.roaster)

    def _set(self, field: str, value: object) -> None:
        object.__setattr__(self, field, value)

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

    @staticmethod
    def _optional_text(value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValidationError("O texto informado é inválido.")
        return value.strip() or None

    @staticmethod
    def _optional_member(enum_class, value):
        return None if value is None else enum_class.parse(value)

    @staticmethod
    def _parse_altitude(value: int | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError("A altitude deve ser um número inteiro.")
        if value <= 0:
            raise ValidationError("A altitude deve ser maior que zero.")
        return value

    @staticmethod
    def _parse_notes(
        values: Iterable[SensoryNote | str],
    ) -> tuple[SensoryNote, ...]:
        notes = tuple(SensoryNote.parse(value) for value in values)
        if len(set(notes)) != len(notes):
            raise ValidationError("Notas sensoriais não podem se repetir.")
        return notes

    @staticmethod
    def _parse_brews(
        values: Iterable[BrewRecommendation],
    ) -> tuple[BrewRecommendation, ...]:
        brews = tuple(values)
        if not all(isinstance(brew, BrewRecommendation) for brew in brews):
            raise ValidationError("Recomendação de preparo inválida.")
        return brews
