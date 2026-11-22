"""DeleteReview, a partir dos critérios de aceite do SCRUM-14 e 19."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from domain.entities.coffee import Coffee
from domain.entities.review import Review
from domain.exceptions import NotFoundError, PermissionDeniedError
from domain.value_objects.origin import Origin
from tests.fakes.fixed_clock import FixedClock
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from tests.fakes.in_memory_review_repository import (
    InMemoryReviewRepository,
)
from use_cases.dtos import CreateReviewInput, DeleteReviewInput
from use_cases.review.create_review import CreateReview
from use_cases.review.delete_review import DeleteReview
from use_cases.review.get_coffee_rating import GetCoffeeRating

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


def add_review(reviews, author_id, rating):
    return reviews.add(
        Review(
            author_id=author_id,
            coffee_id=1,
            rating=rating,
            text=None,
            created_at=CREATED,
        )
    )


@pytest.fixture
def own_review(reviews):
    return add_review(reviews, author_id=7, rating=3)


@pytest.fixture
def delete_review(reviews):
    return DeleteReview(reviews)


def make_input(review, **overrides):
    data = {"user_id": 7, "coffee_id": 1, "review_id": review.id}
    data.update(overrides)
    return DeleteReviewInput(**data)


def test_delete_review_removes_it_from_the_coffee(
    delete_review, reviews, own_review
):  # SCRUM-14
    delete_review.execute(make_input(own_review))

    assert reviews.get_by_id(own_review.id) is None
    assert reviews.list_by_coffee(1) == []


def test_delete_review_of_someone_else_is_denied(
    delete_review, reviews, own_review
):  # SCRUM-14
    with pytest.raises(PermissionDeniedError):
        delete_review.execute(make_input(own_review, user_id=8))

    assert reviews.get_by_id(own_review.id) == own_review


def test_delete_review_of_an_unknown_review_is_not_found(
    delete_review, own_review
):  # SCRUM-14
    with pytest.raises(NotFoundError):
        delete_review.execute(make_input(own_review, review_id=999))


def test_delete_review_through_another_coffee_is_not_found(
    delete_review, reviews, own_review
):  # SCRUM-14
    with pytest.raises(NotFoundError):
        delete_review.execute(make_input(own_review, coffee_id=2))

    assert reviews.get_by_id(own_review.id) == own_review


def test_deleting_twice_is_not_found(delete_review, own_review):
    # SCRUM-14
    delete_review.execute(make_input(own_review))

    with pytest.raises(NotFoundError):
        delete_review.execute(make_input(own_review))


def test_author_can_review_the_coffee_again_after_deleting(
    delete_review, coffees, reviews, own_review
):  # SCRUM-14 / ADR 0002
    delete_review.execute(make_input(own_review))

    CreateReview(reviews, coffees, FixedClock(CREATED)).execute(
        CreateReviewInput(7, 1, 4, None)
    )

    assert reviews.get_by_author_and_coffee(7, 1).rating == 4


def test_rating_is_recalculated_after_deleting_a_review(
    delete_review, coffees, reviews, own_review
):  # SCRUM-14 / SCRUM-19
    add_review(reviews, author_id=8, rating=5)
    get_rating = GetCoffeeRating(coffees, reviews)
    assert get_rating.execute(1).count == 2

    delete_review.execute(make_input(own_review))

    rating = get_rating.execute(1)
    assert rating.count == 1
    assert rating.average == Decimal("5.0")
    assert [b.count for b in rating.histogram] == [0, 0, 0, 0, 1]


def test_deleting_the_last_review_leaves_the_coffee_without_rating(
    delete_review, coffees, reviews, own_review
):  # SCRUM-14 / SCRUM-19
    delete_review.execute(make_input(own_review))

    rating = GetCoffeeRating(coffees, reviews).execute(1)

    assert rating.count == 0
    assert rating.average is None
