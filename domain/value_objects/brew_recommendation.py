"""Recomendação de preparo: objeto de valor de um café."""

from dataclasses import dataclass

from domain.exceptions import ValidationError


@dataclass(frozen=True)
class BrewRecommendation:
    """Método obrigatório; proporção, moagem e temperatura opcionais."""

    method: str
    ratio: str | None = None
    grind: str | None = None
    temperature: str | None = None

    def __post_init__(self) -> None:
        method = self._clean(self.method)
        if method is None:
            raise ValidationError("A recomendação de preparo exige um método.")
        object.__setattr__(self, "method", method)
        for field in ("ratio", "grind", "temperature"):
            object.__setattr__(self, field, self._clean(getattr(self, field)))

    @staticmethod
    def _clean(value: str | None) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return None
        return value.strip()
