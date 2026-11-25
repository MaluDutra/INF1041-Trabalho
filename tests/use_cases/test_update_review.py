"""UpdateReview, a partir dos critérios de aceite do SCRUM-14 e 19."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from domain.entities.coffee import Coffee
from domain.entities.review import Review
from domain.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from domain.value_objects.origin import Origin
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from tests.fakes.in_memory_review_repository import (
    InMemoryReviewRepository,
)
from use_cases.dtos import UpdateReviewInput
from use_cases.review.get_coffee_rating import GetCoffeeRating
from use_cases.review.update_review import UpdateReview

CREATED = datetime(2026, 3, 10, 14, 30)


@pytest.fixture
def coffees():
    repository = InMemoryCoffeeRepository()
    repository.add(
        Coffee(
            name="Blend",
            roaster="Café Lá",
            origin=Origin.BRAZIL,
            added_at=date(2026, 1, 15),
        )
    )
    return repository


@pytest.fixture
def reviews():
    return InMemoryReviewRepository()


@pytest.fixture
def own_review(reviews):
    """Review do usuário 7 sobre o café 1, com nota 3."""
    return reviews.add(
        Review(
            author_id=7,
            coffee_id=1,
            rating=3,
            text="Ok.",
            created_at=CREATED,
        )
    )


@pytest.fixture
def update_review(reviews):
    return UpdateReview(reviews)


def make_input(review, **overrides):
    data = {
        "user_id": 7,
        "coffee_id": 1,
        "review_id": review.id,
        "rating": 5,
        "text": "Texto novo.",
    }
    data.update(overrides)
    return UpdateReviewInput(**data)


def test_update_review_changes_rating_and_text(
    update_review, reviews, own_review
):  # SCRUM-14
    result = update_review.execute(make_input(own_review))

    assert (result.rating, result.text) == (5, "Texto novo.")
    stored = reviews.get_by_id(own_review.id)
    assert (stored.rating, stored.text) == (5, "Texto novo.")


def test_update_review_keeps_the_original_date(
    update_review, reviews, own_review
):  # SCRUM-14
    result = update_review.execute(make_input(own_review))

    assert result.created_at == CREATED
    assert reviews.get_by_id(own_review.id).created_at == CREATED


def test_update_review_turns_the_edited_marker_on(
    update_review, reviews, own_review
):  # SCRUM-14
    assert own_review.edited is False

    result = update_review.execute(make_input(own_review))

    assert result.edited is True
    assert reviews.get_by_id(own_review.id).edited is True


def test_update_review_with_blank_text_stores_no_text(
    update_review, reviews, own_review
):  # SCRUM-14
    result = update_review.execute(make_input(own_review, text="  \n "))

    assert result.text is None
    assert reviews.get_by_id(own_review.id).text is None


@pytest.mark.parametrize("rating", [0, 6, None])
def test_update_review_rejects_a_rating_out_of_scale(
    update_review, reviews, own_review, rating
):  # SCRUM-14
    with pytest.raises(ValidationError, match="nota"):
        update_review.execute(make_input(own_review, rating=rating))

    assert reviews.get_by_id(own_review.id) == own_review


def test_update_review_rejects_text_over_1000_characters(
    update_review, reviews, own_review
):  # SCRUM-14
    with pytest.raises(ValidationError, match="1000"):
        update_review.execute(make_input(own_review, text="a" * 1001))

    assert reviews.get_by_id(own_review.id) == own_review


def test_update_review_accepts_text_with_1000_characters(
    update_review, own_review
):  # SCRUM-14
    result = update_review.execute(make_input(own_review, text="a" * 1000))

    assert len(result.text) == 1000


def test_update_review_of_someone_else_is_denied(
    update_review, reviews, own_review
):  # SCRUM-14
    with pytest.raises(PermissionDeniedError):
        update_review.execute(make_input(own_review, user_id=8))

    assert reviews.get_by_id(own_review.id) == own_review


def test_update_review_of_an_unknown_review_is_not_found(
    update_review, own_review
):  # SCRUM-14
    with pytest.raises(NotFoundError):
        update_review.execute(make_input(own_review, review_id=999))


def test_update_review_through_another_coffee_is_not_found(
    update_review, reviews, own_review
):  # SCRUM-14
    with pytest.raises(NotFoundError):
        update_review.execute(make_input(own_review, coffee_id=2))

    assert reviews.get_by_id(own_review.id) == own_review


def test_rating_is_recalculated_after_editing_3_to_5(
    update_review, coffees, reviews, own_review
):  # SCRUM-14 / SCRUM-19
    reviews.add(
        Review(
            author_id=8,
            coffee_id=1,
            rating=5,
            text=None,
            created_at=CREATED,
        )
    )
    get_rating = GetCoffeeRating(coffees, reviews)
    assert get_rating.execute(1).average == Decimal("4.0")

    update_review.execute(make_input(own_review, rating=5))

    rating = get_rating.execute(1)
    assert rating.average == Decimal("5.0")
    assert rating.count == 2
    assert [b.count for b in rating.histogram] == [0, 0, 0, 0, 2]
