"""Formata a nota de um review para a interface."""

from domain.entities.review import RATING_SCALE


def format_rating(rating: int) -> str:
    """Devolve a nota como ``"4 de 5"``, com o teto vindo da escala."""
    return f"{rating} de {max(RATING_SCALE)}"
