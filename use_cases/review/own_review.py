"""Busca de um review que só o autor pode alterar (SCRUM-14)."""

from domain.entities.review import Review
from domain.exceptions import NotFoundError, PermissionDeniedError
from use_cases.ports.review_repository import ReviewRepository


def load_own_review(
    repository: ReviewRepository,
    user_id: int,
    coffee_id: int,
    review_id: int,
) -> Review:
    """Devolve o review do café ou lança o erro que a regra pede.

    ``NotFoundError`` se o review não existe ou é de outro café, e
    ``PermissionDeniedError`` se quem pede não é o autor.
    """
    review = repository.get_by_id(review_id)
    if review is None or review.coffee_id != coffee_id:
        raise NotFoundError("Avaliação não encontrada.")
    if review.author_id != user_id:
        raise PermissionDeniedError("Só o autor pode alterar esta avaliação.")
    return review
