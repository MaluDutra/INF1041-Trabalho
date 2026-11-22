"""Fake em memória do ReviewRepository, reaproveitado pelos testes."""

from collections.abc import Collection
from dataclasses import replace

from domain.entities.review import Review
from domain.exceptions import ConflictError, NotFoundError
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

    def get_by_id(self, review_id: int) -> Review | None:
        return self._reviews.get(review_id)

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

    def list_by_author(self, author_id: int) -> list[Review]:
        return [
            review
            for review in self._reviews.values()
            if review.author_id == author_id
        ]

    def list_ratings_by_coffee(self, coffee_id: int) -> list[int]:
        return [review.rating for review in self.list_by_coffee(coffee_id)]

    def list_ratings_by_coffees(
        self, coffee_ids: Collection[int]
    ) -> dict[int, list[int]]:
        grouped: dict[int, list[int]] = {}
        for review in self._reviews.values():
            if review.coffee_id in coffee_ids:
                grouped.setdefault(review.coffee_id, []).append(review.rating)
        return grouped

    def update(self, review: Review) -> Review:
        if review.id not in self._reviews:
            raise NotFoundError("Avaliação não encontrada.")
        self._reviews[review.id] = review
        return review

    def delete(self, review_id: int) -> None:
        if review_id not in self._reviews:
            raise NotFoundError("Avaliação não encontrada.")
        del self._reviews[review_id]
