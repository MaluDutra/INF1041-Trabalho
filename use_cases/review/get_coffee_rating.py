"""Consulta da nota agregada de um café (SCRUM-19)."""

from domain.exceptions import NotFoundError
from domain.value_objects.coffee_rating import CoffeeRating
from use_cases.dtos import CoffeeRatingDTO
from use_cases.ports.coffee_repository import CoffeeRepository
from use_cases.ports.review_repository import ReviewRepository
from use_cases.review.rating_dto import to_rating_dto


class GetCoffeeRating:
    """Devolve a nota agregada do café, ou lança ``NotFoundError``.

    A nota é calculada a cada leitura a partir dos reviews atuais e
    nunca é gravada, então não fica desatualizada.
    """

    def __init__(
        self,
        coffee_repository: CoffeeRepository,
        review_repository: ReviewRepository,
    ) -> None:
        self._coffee_repository = coffee_repository
        self._review_repository = review_repository

    def execute(self, coffee_id: int) -> CoffeeRatingDTO:
        if self._coffee_repository.get_by_id(coffee_id) is None:
            raise NotFoundError("Café não encontrado.")
        ratings = self._review_repository.list_ratings_by_coffee(coffee_id)
        return to_rating_dto(CoffeeRating.from_ratings(ratings))
