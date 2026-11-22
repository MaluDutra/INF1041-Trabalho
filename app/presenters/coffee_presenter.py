"""Formata o café para a view: só apresentação, sem regra de negócio."""

from dataclasses import dataclass

from app.presenters.date_presenter import format_date
from app.presenters.rating_presenter import (
    format_rating,
    format_rating_summary,
)
from use_cases.dtos import CoffeeDetailsDTO, CoffeeRatingDTO, ReviewDTO

NOT_INFORMED = "Não informado"
NO_REVIEWS = "Ainda não há avaliações."


@dataclass(frozen=True)
class BrewRecommendationView:
    method: str
    ratio: str
    grind: str
    temperature: str


@dataclass(frozen=True)
class ReviewView:
    id: int
    rating: int
    rating_label: str
    author_name: str
    date: str
    text: str | None
    is_own: bool
    edited: bool


@dataclass(frozen=True)
class HistogramRowView:
    label: str
    count: int
    percentage: int
    percentage_label: str


@dataclass(frozen=True)
class RatingView:
    summary: str
    has_reviews: bool
    histogram: tuple[HistogramRowView, ...]


@dataclass(frozen=True)
class CoffeeDetailsView:
    id: int
    name: str
    roaster: str
    origin: str
    producer: str
    variety: str
    process: str
    altitude: str
    roast: str
    sensory_notes: str
    photo_url: str | None
    story: str
    brew_recommendations: tuple[BrewRecommendationView, ...]
    brew_empty_message: str | None
    rating: RatingView
    reviews: tuple[ReviewView, ...]
    reviews_empty_message: str | None
    user_has_reviewed: bool
    own_review: ReviewView | None


def present_details(details: CoffeeDetailsDTO) -> CoffeeDetailsView:
    reviews = tuple(_present_review(review) for review in details.reviews)
    return CoffeeDetailsView(
        id=details.id,
        name=details.name,
        roaster=details.roaster,
        origin=details.origin,
        producer=_or_not_informed(details.producer),
        variety=_or_not_informed(details.variety),
        process=_or_not_informed(details.process),
        altitude=_format_altitude(details.altitude),
        roast=_or_not_informed(details.roast),
        sensory_notes=_or_not_informed(", ".join(details.sensory_notes)),
        photo_url=details.photo_url,
        story=_or_not_informed(details.story),
        brew_recommendations=tuple(
            BrewRecommendationView(
                method=brew.method,
                ratio=_or_not_informed(brew.ratio),
                grind=_or_not_informed(brew.grind),
                temperature=_or_not_informed(brew.temperature),
            )
            for brew in details.brew_recommendations
        ),
        brew_empty_message=(
            None if details.brew_recommendations else NOT_INFORMED
        ),
        rating=_present_rating(details.rating),
        reviews=reviews,
        reviews_empty_message=None if details.reviews else NO_REVIEWS,
        user_has_reviewed=details.user_has_reviewed,
        own_review=next((r for r in reviews if r.is_own), None),
    )


def _present_rating(rating: CoffeeRatingDTO) -> RatingView:
    return RatingView(
        summary=format_rating_summary(rating),
        has_reviews=rating.count > 0,
        histogram=tuple(
            HistogramRowView(
                label=f"{bucket.rating}★",
                count=bucket.count,
                percentage=bucket.percentage,
                percentage_label=f"{bucket.percentage}%",
            )
            for bucket in reversed(rating.histogram)
        ),
    )


def _present_review(review: ReviewDTO) -> ReviewView:
    return ReviewView(
        id=review.id,
        rating=review.rating,
        rating_label=format_rating(review.rating),
        author_name=review.author_name,
        date=format_date(review.created_at),
        text=review.text,
        is_own=review.is_own,
        edited=review.edited,
    )


def _or_not_informed(value: str | None) -> str:
    return value if value else NOT_INFORMED


def _format_altitude(altitude: int | None) -> str:
    if altitude is None:
        return NOT_INFORMED
    return f"{altitude:,}".replace(",", ".") + " m"
