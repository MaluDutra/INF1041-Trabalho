"""Formata "Minhas avaliações" para a view: só apresentação."""

from dataclasses import dataclass

from app.presenters.date_presenter import format_date
from app.presenters.rating_presenter import format_rating
from use_cases.dtos import UserReviewDTO


@dataclass(frozen=True)
class UserReviewView:
    id: int
    coffee_id: int
    coffee_name: str
    rating_label: str
    date: str
    text: str | None
    edited: bool


def present_user_reviews(
    reviews: tuple[UserReviewDTO, ...],
) -> tuple[UserReviewView, ...]:
    return tuple(
        UserReviewView(
            id=review.id,
            coffee_id=review.coffee_id,
            coffee_name=review.coffee_name,
            rating_label=format_rating(review.rating),
            date=format_date(review.created_at),
            text=review.text,
            edited=review.edited,
        )
        for review in reviews
    )
