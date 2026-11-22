"""Criação de um review (SCRUM-14)."""

from domain.entities.review import Review
from domain.exceptions import ConflictError, NotFoundError
from use_cases.dtos import CreatedReviewDTO, CreateReviewInput
from use_cases.ports.clock import Clock
from use_cases.ports.coffee_repository import CoffeeRepository
from use_cases.ports.review_repository import ReviewRepository


class CreateReview:
    """Cria o review do usuário sobre um café.

    O café precisa existir e o usuário não pode ter avaliado esse café
    antes (ADR 0002). Os erros são ``NotFoundError``, ``ValidationError``
    (nota ou texto inválidos) e ``ConflictError``.
    """

    def __init__(
        self,
        review_repository: ReviewRepository,
        coffee_repository: CoffeeRepository,
        clock: Clock,
    ) -> None:
        self._review_repository = review_repository
        self._coffee_repository = coffee_repository
        self._clock = clock

    def execute(self, data: CreateReviewInput) -> CreatedReviewDTO:
        if self._coffee_repository.get_by_id(data.coffee_id) is None:
            raise NotFoundError("Café não encontrado.")
        review = Review(
            author_id=data.user_id,
            coffee_id=data.coffee_id,
            rating=data.rating,
            text=data.text,
            created_at=self._clock.now(),
        )
        if self._review_repository.get_by_author_and_coffee(
            data.user_id, data.coffee_id
        ):
            raise ConflictError("Você já avaliou este café.")
        stored = self._review_repository.add(review)
        return CreatedReviewDTO(
            id=stored.id,
            rating=stored.rating,
            text=stored.text,
            created_at=stored.created_at,
            edited=stored.edited,
        )
