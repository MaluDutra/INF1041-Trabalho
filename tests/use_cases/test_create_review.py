"""CreateReview, a partir dos critérios de aceite do SCRUM-14."""

from datetime import date, datetime

import pytest

from domain.entities.coffee import Coffee
from domain.exceptions import ConflictError, NotFoundError, ValidationError
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

NOW = datetime(2026, 3, 10, 14, 30)


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
def create_review(coffees, reviews):
    return CreateReview(reviews, coffees, FixedClock(NOW))


def make_input(**overrides):
    data = {"user_id": 7, "coffee_id": 1, "rating": 4, "text": None}
    data.update(overrides)
    return CreateReviewInput(**data)


def test_create_review_with_rating_and_text(create_review, reviews):
    # SCRUM-14
    result = create_review.execute(make_input(text="Achocolatado."))

    assert result.rating == 4
    assert result.text == "Achocolatado."
    assert result.created_at == NOW
    assert result.edited is False
    stored = reviews.get_by_author_and_coffee(7, 1)
    assert stored.id == result.id
    assert stored.created_at == NOW


def test_create_review_with_rating_only(create_review, reviews):  # SCRUM-14
    result = create_review.execute(make_input(text=None))

    assert result.rating == 4
    assert result.text is None
    assert reviews.get_by_author_and_coffee(7, 1).text is None


def test_create_review_with_blank_text_stores_no_text(
    create_review, reviews
):  # SCRUM-14
    result = create_review.execute(make_input(text="   \n "))

    assert result.text is None
    assert reviews.get_by_author_and_coffee(7, 1).text is None


@pytest.mark.parametrize("rating", [0, 6])
def test_create_review_rejects_a_rating_out_of_scale(
    create_review, reviews, rating
):  # SCRUM-14
    with pytest.raises(ValidationError, match="nota"):
        create_review.execute(make_input(rating=rating))

    assert reviews.list_by_coffee(1) == []


def test_create_review_without_rating_is_rejected(create_review):
    # SCRUM-14
    with pytest.raises(ValidationError, match="nota"):
        create_review.execute(make_input(rating=None))


def test_create_review_accepts_text_with_1000_characters(
    create_review,
):  # SCRUM-14
    result = create_review.execute(make_input(text="a" * 1000))

    assert len(result.text) == 1000


def test_create_review_rejects_text_with_1001_characters(
    create_review, reviews
):  # SCRUM-14
    with pytest.raises(ValidationError, match="1000"):
        create_review.execute(make_input(text="a" * 1001))

    assert reviews.list_by_coffee(1) == []


def test_create_review_rejects_an_unknown_coffee(
    create_review, reviews
):  # SCRUM-14
    with pytest.raises(NotFoundError):
        create_review.execute(make_input(coffee_id=999))

    assert reviews.list_by_coffee(999) == []


def test_create_review_rejects_second_review_same_coffee(
    create_review, reviews
):  # SCRUM-14
    create_review.execute(make_input(rating=5))

    with pytest.raises(ConflictError):
        create_review.execute(make_input(rating=1))

    only_review = reviews.list_by_coffee(1)
    assert [review.rating for review in only_review] == [5]


def test_two_users_can_review_the_same_coffee(create_review, reviews):
    # SCRUM-14
    create_review.execute(make_input(user_id=7))
    create_review.execute(make_input(user_id=8))

    assert len(reviews.list_by_coffee(1)) == 2


def test_same_user_can_review_different_coffees(
    create_review, coffees, reviews
):  # SCRUM-14
    other = coffees.add(
        Coffee(
            name="Outro",
            roaster="Café Lá",
            origin=Origin.PERU,
            added_at=date(2026, 1, 16),
        )
    )

    create_review.execute(make_input(coffee_id=1))
    create_review.execute(make_input(coffee_id=other.id))

    assert reviews.get_by_author_and_coffee(7, other.id) is not None
