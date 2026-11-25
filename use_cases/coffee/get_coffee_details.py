"""Consulta da página de um café (SCRUM-12 e SCRUM-14)."""

from domain.entities.coffee import Coffee
from domain.entities.review import Review
from domain.exceptions import NotFoundError
from domain.value_objects.coffee_rating import CoffeeRating
from use_cases.dtos import (
    BrewRecommendationDTO,
    CoffeeDetailsDTO,
    CoffeeRatingDTO,
    ReviewDTO,
)
from use_cases.ports.coffee_repository import CoffeeRepository
from use_cases.ports.review_repository import ReviewRepository
from use_cases.ports.user_repository import UserRepository
from use_cases.review.rating_dto import to_rating_dto


class GetCoffeeDetails:
    """Devolve o café, seus reviews e a nota agregada.

    Lança ``NotFoundError`` se o café não existe. Os reviews vêm do mais
    recente para o mais antigo, com o do usuário logado (se ``user_id``
    for dado) em primeiro. A nota agregada é calculada a cada leitura a
    partir desses mesmos reviews (SCRUM-19).
    """

    def __init__(
        self,
        coffee_repository: CoffeeRepository,
        review_repository: ReviewRepository,
        user_repository: UserRepository,
    ) -> None:
        self._coffee_repository = coffee_repository
        self._review_repository = review_repository
        self._user_repository = user_repository

    def execute(
        self, coffee_id: int, user_id: int | None = None
    ) -> CoffeeDetailsDTO:
        coffee = self._coffee_repository.get_by_id(coffee_id)
        if coffee is None:
            raise NotFoundError("Café não encontrado.")
        reviews = self._ordered_reviews(coffee_id, user_id)
        rating = CoffeeRating.from_ratings(r.rating for r in reviews)
        return self._to_dto(
            coffee,
            to_rating_dto(rating),
            tuple(self._to_review_dto(r, user_id) for r in reviews),
            user_has_reviewed=any(r.author_id == user_id for r in reviews),
        )

    def _ordered_reviews(
        self, coffee_id: int, user_id: int | None
    ) -> list[Review]:
        reviews = sorted(
            self._review_repository.list_by_coffee(coffee_id),
            key=lambda review: (review.created_at, review.id),
            reverse=True,
        )
        # sorted() é estável: o do usuário sobe sem mexer na ordem dos outros
        return sorted(reviews, key=lambda r: r.author_id != user_id)

    def _to_review_dto(self, review: Review, user_id: int | None) -> ReviewDTO:
        author = self._user_repository.get_by_id(review.author_id)
        return ReviewDTO(
            id=review.id,
            author_id=review.author_id,
            author_name=author.display_name,
            rating=review.rating,
            text=review.text,
            created_at=review.created_at,
            edited=review.edited,
            is_own=review.author_id == user_id,
        )

    @staticmethod
    def _to_dto(
        coffee: Coffee,
        rating: CoffeeRatingDTO,
        reviews: tuple[ReviewDTO, ...],
        user_has_reviewed: bool,
    ) -> CoffeeDetailsDTO:
        return CoffeeDetailsDTO(
            id=coffee.id,
            name=coffee.name,
            roaster=coffee.roaster,
            origin=coffee.origin.value,
            producer=coffee.producer,
            variety=coffee.variety,
            process=coffee.process.value if coffee.process else None,
            altitude=coffee.altitude,
            roast=coffee.roast.value if coffee.roast else None,
            sensory_notes=tuple(note.value for note in coffee.sensory_notes),
            photo_url=coffee.photo_url,
            story=coffee.story,
            brew_recommendations=tuple(
                BrewRecommendationDTO(
                    method=brew.method,
                    ratio=brew.ratio,
                    grind=brew.grind,
                    temperature=brew.temperature,
                )
                for brew in coffee.brew_recommendations
            ),
            rating=rating,
            reviews=reviews,
            user_has_reviewed=user_has_reviewed,
        )
