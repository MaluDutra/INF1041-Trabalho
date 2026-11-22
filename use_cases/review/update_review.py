"""Edição de um review (SCRUM-14)."""

from use_cases.dtos import SavedReviewDTO, UpdateReviewInput
from use_cases.ports.review_repository import ReviewRepository
from use_cases.review.own_review import load_own_review


class UpdateReview:
    """Troca a nota e o texto do review do próprio autor.

    Os erros são ``NotFoundError``, ``PermissionDeniedError`` e
    ``ValidationError`` (nota ou texto inválidos, com as mesmas regras
    da criação). A data de criação é mantida e o review passa a constar
    como editado.
    """

    def __init__(self, review_repository: ReviewRepository) -> None:
        self._review_repository = review_repository

    def execute(self, data: UpdateReviewInput) -> SavedReviewDTO:
        review = load_own_review(
            self._review_repository,
            data.user_id,
            data.coffee_id,
            data.review_id,
        )
        stored = self._review_repository.update(
            review.edit(rating=data.rating, text=data.text)
        )
        return SavedReviewDTO(
            id=stored.id,
            rating=stored.rating,
            text=stored.text,
            created_at=stored.created_at,
            edited=stored.edited,
        )
