"""Listagem dos reviews de um usuário (SCRUM-14)."""

from domain.entities.review import Review
from use_cases.dtos import UserReviewDTO
from use_cases.ports.coffee_repository import CoffeeRepository
from use_cases.ports.review_repository import ReviewRepository


class ListUserReviews:
    """Devolve os reviews do usuário, do mais recente para o mais antigo.

    Cada item traz o id e o nome do café. Os cafés vêm numa única
    consulta, sem uma por review. Quem não avaliou nada recebe uma
    tupla vazia.
    """

    def __init__(
        self,
        review_repository: ReviewRepository,
        coffee_repository: CoffeeRepository,
    ) -> None:
        self._review_repository = review_repository
        self._coffee_repository = coffee_repository

    def execute(self, user_id: int) -> tuple[UserReviewDTO, ...]:
        reviews = sorted(
            self._review_repository.list_by_author(user_id),
            key=lambda review: (review.created_at, review.id),
            reverse=True,
        )
        names = {
            coffee.id: coffee.name
            for coffee in self._coffee_repository.list_by_ids(
                {review.coffee_id for review in reviews}
            )
        }
        return tuple(self._to_dto(review, names) for review in reviews)

    @staticmethod
    def _to_dto(review: Review, names: dict[int, str]) -> UserReviewDTO:
        return UserReviewDTO(
            id=review.id,
            coffee_id=review.coffee_id,
            coffee_name=names[review.coffee_id],
            rating=review.rating,
            text=review.text,
            created_at=review.created_at,
            edited=review.edited,
        )
