"""Formata notas para a interface."""

from domain.entities.review import RATING_SCALE
from use_cases.dtos import CoffeeRatingDTO

NO_RATING = "Sem avaliações"


def format_rating(rating: int) -> str:
    """Devolve a nota como ``"4 de 5"``, com o teto vindo da escala."""
    return f"{rating} de {max(RATING_SCALE)}"


def format_rating_summary(rating: CoffeeRatingDTO) -> str:
    """Devolve a Nota agregada como ``"4,3 ★ · 12 avaliações"``."""
    if rating.average is None:
        return NO_RATING
    noun = "avaliação" if rating.count == 1 else "avaliações"
    average = str(rating.average).replace(".", ",")
    return f"{average} ★ · {rating.count} {noun}"
