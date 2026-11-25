"""Exclusão de um review (SCRUM-14)."""

from use_cases.dtos import DeleteReviewInput
from use_cases.ports.review_repository import ReviewRepository
from use_cases.review.own_review import load_own_review


class DeleteReview:
    """Exclui o review do próprio autor, em definitivo.

    Os erros são ``NotFoundError`` e ``PermissionDeniedError``. Depois
    da exclusão o autor pode avaliar o café de novo (ADR 0002).
    """

    def __init__(self, review_repository: ReviewRepository) -> None:
        self._review_repository = review_repository

    def execute(self, data: DeleteReviewInput) -> None:
        review = load_own_review(
            self._review_repository,
            data.user_id,
            data.coffee_id,
            data.review_id,
        )
        self._review_repository.delete(review.id)
