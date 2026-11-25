"""Entidade Review."""

from dataclasses import dataclass, replace
from datetime import datetime

from domain.exceptions import ValidationError

# Única definição da escala da nota (ADR 0001). Trocar a escala é mudar
# só esta linha.
RATING_SCALE = range(1, 6)
TEXT_MAX = 1000
RATING_RULE = (
    f"A nota deve ser um número inteiro de {min(RATING_SCALE)} a "
    f"{max(RATING_SCALE)}."
)


@dataclass(frozen=True)
class Review:
    """Opinião de um usuário sobre um café: nota e texto opcional.

    A entidade só valida o próprio estado. O ``id`` é atribuído pelo
    repositório ao gravar. Um texto só com espaços vira ``None``.
    """

    author_id: int
    coffee_id: int
    rating: int
    text: str | None
    created_at: datetime
    edited: bool = False
    id: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "rating", self._parse_rating(self.rating))
        object.__setattr__(self, "text", self._parse_text(self.text))

    def edit(self, rating: int | None, text: str | None) -> "Review":
        """Devolve o review com nota e texto novos, marcado como editado.

        Vale a mesma validação da criação. Id, autor, café e data de
        criação não mudam, e não há histórico de versões.
        """
        return replace(self, rating=rating, text=text, edited=True)

    @staticmethod
    def _parse_rating(value: int) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value not in RATING_SCALE
        ):
            raise ValidationError(RATING_RULE)
        return value

    @staticmethod
    def _parse_text(value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValidationError("O texto informado é inválido.")
        text = value.strip()
        if len(text) > TEXT_MAX:
            raise ValidationError(
                f"O texto deve ter no máximo {TEXT_MAX} caracteres."
            )
        return text or None
