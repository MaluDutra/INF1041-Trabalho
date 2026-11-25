"""Caso de uso GetCoffeeRating (SCRUM-19), só com fakes em memória."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from domain.entities.coffee import Coffee
from domain.entities.review import Review
from domain.exceptions import NotFoundError
from domain.value_objects.origin import Origin
from tests.fakes.fixed_clock import FixedClock
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from tests.fakes.in_memory_review_repository import (
    InMemoryReviewRepository,
)
from use_cases.dtos import CreateReviewInput
from use_cases.review.create_review import CreateReview
from use_cases.review.get_coffee_rating import GetCoffeeRating

NOW = datetime(2026, 3, 10, 14, 30)


@pytest.fixture
def coffees():
    return InMemoryCoffeeRepository()


@pytest.fixture
def reviews():
    return InMemoryReviewRepository()


@pytest.fixture
def coffee(coffees):
    return coffees.add(
        Coffee(
            name="Sítio da Torre",
            roaster="Café Lá",
            origin=Origin.BRAZIL,
            added_at=date(2026, 1, 15),
        )
    )


@pytest.fixture
def use_case(coffees, reviews):
    return GetCoffeeRating(coffees, reviews)


def add_reviews(reviews, coffee, ratings):
    for author_id, value in enumerate(ratings, start=1):
        reviews.add(
            Review(
                author_id=author_id,
                coffee_id=coffee.id,
                rating=value,
                text=None,
                created_at=NOW,
            )
        )


def test_rating_of_4_4_5_4_is_4_3_with_4_reviews(
    use_case, reviews, coffee
):  # SCRUM-19
    add_reviews(reviews, coffee, [4, 4, 5, 4])

    rating = use_case.execute(coffee.id)

    assert rating.average == Decimal("4.3")
    assert rating.count == 4


def test_single_review_with_rating_1_has_average_1_0(
    use_case, reviews, coffee
):  # SCRUM-19
    add_reviews(reviews, coffee, [1])

    rating = use_case.execute(coffee.id)

    assert rating.average == Decimal("1.0")
    assert rating.count == 1


def test_coffee_without_reviews_has_no_average_and_empty_histogram(
    use_case, coffee
):  # SCRUM-19
    rating = use_case.execute(coffee.id)

    assert rating.average is None
    assert rating.count == 0
    assert [(b.rating, b.count, b.percentage) for b in rating.histogram] == [
        (1, 0, 0),
        (2, 0, 0),
        (3, 0, 0),
        (4, 0, 0),
        (5, 0, 0),
    ]


def test_histogram_of_5_5_4_1_has_counts_and_percentages(
    use_case, reviews, coffee
):  # SCRUM-19
    add_reviews(reviews, coffee, [5, 5, 4, 1])

    rating = use_case.execute(coffee.id)

    assert [(b.rating, b.count, b.percentage) for b in rating.histogram] == [
        (1, 1, 25),
        (2, 0, 0),
        (3, 0, 0),
        (4, 1, 25),
        (5, 2, 50),
    ]


def test_ratings_of_other_coffees_are_ignored(
    use_case, coffees, reviews, coffee
):  # SCRUM-19
    other = coffees.add(
        Coffee(
            name="Outro",
            roaster="Café Lá",
            origin=Origin.PERU,
            added_at=date(2026, 1, 16),
        )
    )
    add_reviews(reviews, other, [1, 1])
    add_reviews(reviews, coffee, [5])

    rating = use_case.execute(coffee.id)

    assert rating.average == Decimal("5.0")
    assert rating.count == 1


def test_unknown_coffee_raises_not_found(use_case):  # SCRUM-19
    with pytest.raises(NotFoundError):
        use_case.execute(999)


def test_rating_is_recalculated_after_create_review(
    use_case, coffees, reviews, coffee
):  # SCRUM-19
    create = CreateReview(reviews, coffees, FixedClock(NOW))
    create.execute(CreateReviewInput(1, coffee.id, 5, None))
    assert use_case.execute(coffee.id).average == Decimal("5.0")

    create.execute(CreateReviewInput(2, coffee.id, 2, None))
    rating = use_case.execute(coffee.id)

    assert rating.count == 2
    assert rating.average == Decimal("3.5")
    assert [b.count for b in rating.histogram] == [0, 1, 0, 0, 1]
