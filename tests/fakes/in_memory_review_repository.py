"""Fake em memória do ReviewRepository, reaproveitado pelos testes."""

from dataclasses import replace

from domain.entities.review import Review
from domain.exceptions import ConflictError
from use_cases.ports.review_repository import ReviewRepository


class InMemoryReviewRepository(ReviewRepository):
    def __init__(self) -> None:
        self._reviews: dict[int, Review] = {}
        self._next_id = 1

    def add(self, review: Review) -> Review:
        if self.get_by_author_and_coffee(review.author_id, review.coffee_id):
            raise ConflictError("Você já avaliou este café.")
        stored = replace(review, id=self._next_id)
        self._reviews[self._next_id] = stored
        self._next_id += 1
        return stored

    def get_by_author_and_coffee(
        self, author_id: int, coffee_id: int
    ) -> Review | None:
        for review in self._reviews.values():
            if review.author_id == author_id and review.coffee_id == coffee_id:
                return review
        return None

    def list_by_coffee(self, coffee_id: int) -> list[Review]:
        return [
            review
            for review in self._reviews.values()
            if review.coffee_id == coffee_id
        ]

    def list_ratings_by_coffee(self, coffee_id: int) -> list[int]:
        return [review.rating for review in self.list_by_coffee(coffee_id)]
