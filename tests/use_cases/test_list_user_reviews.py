"""ListUserReviews, a partir dos critérios de aceite do SCRUM-14."""

from datetime import date, datetime

import pytest

from domain.entities.coffee import Coffee
from domain.value_objects.origin import Origin
from tests.fakes.fixed_clock import FixedClock
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from tests.fakes.in_memory_review_repository import (
    InMemoryReviewRepository,
)
from use_cases.dtos import CreateReviewInput, UpdateReviewInput
from use_cases.review.create_review import CreateReview
from use_cases.review.list_user_reviews import ListUserReviews
from use_cases.review.update_review import UpdateReview

ANA = 1
BIA = 2


@pytest.fixture
def coffees():
    repository = InMemoryCoffeeRepository()
    for name in ("Sítio da Torre", "Blend da Casa", "Reserva"):
        repository.add(
            Coffee(
                name=name,
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
def list_user_reviews(reviews, coffees):
    return ListUserReviews(reviews, coffees)


@pytest.fixture
def clock():
    return FixedClock(datetime(2026, 3, 1, 10, 0))


@pytest.fixture
def add_review(reviews, coffees, clock):
    """Cria um review pelo caso de uso, com o relógio no dia pedido."""
    create_review = CreateReview(reviews, coffees, clock)

    def add(author_id, coffee_id, day, rating=4, text=None):
        clock.moment = datetime(2026, 3, day, 10, 0)
        saved = create_review.execute(
            CreateReviewInput(author_id, coffee_id, rating, text)
        )
        return reviews.get_by_id(saved.id)

    return add


def test_user_reviews_come_from_newest_to_oldest(
    list_user_reviews, add_review
):  # SCRUM-14
    add_review(ANA, coffee_id=1, day=5)
    add_review(ANA, coffee_id=2, day=20)
    add_review(ANA, coffee_id=3, day=12)

    result = list_user_reviews.execute(ANA)

    assert [item.coffee_id for item in result] == [2, 3, 1]


def test_only_the_users_own_reviews_are_listed(
    list_user_reviews, add_review
):  # SCRUM-14
    mine = add_review(ANA, coffee_id=1, day=5)
    add_review(BIA, coffee_id=1, day=6)
    add_review(BIA, coffee_id=2, day=7)

    result = list_user_reviews.execute(ANA)

    assert [item.id for item in result] == [mine.id]


def test_each_item_carries_the_coffee_id_and_name(
    list_user_reviews, add_review
):  # SCRUM-14
    add_review(ANA, coffee_id=2, day=5)
    add_review(ANA, coffee_id=3, day=6)

    result = list_user_reviews.execute(ANA)

    assert [(i.coffee_id, i.coffee_name) for i in result] == [
        (3, "Reserva"),
        (2, "Blend da Casa"),
    ]


def test_each_item_carries_rating_text_date_and_edited_flag(
    list_user_reviews, add_review, reviews
):  # SCRUM-14
    stored = add_review(ANA, coffee_id=1, day=5, rating=2, text="Amargo")
    UpdateReview(reviews).execute(
        UpdateReviewInput(ANA, 1, stored.id, rating=3, text="Melhorou")
    )

    (item,) = list_user_reviews.execute(ANA)

    assert item.id == stored.id
    assert (item.rating, item.text) == (3, "Melhorou")
    assert item.created_at == datetime(2026, 3, 5, 10, 0)
    assert item.edited is True


def test_reviews_made_at_the_same_moment_keep_the_latest_id_first(
    list_user_reviews, add_review
):  # SCRUM-14
    first = add_review(ANA, coffee_id=1, day=5)
    second = add_review(ANA, coffee_id=2, day=5)

    result = list_user_reviews.execute(ANA)

    assert [item.id for item in result] == [second.id, first.id]


def test_user_without_reviews_gets_an_empty_list(
    list_user_reviews, add_review
):  # SCRUM-14
    add_review(BIA, coffee_id=1, day=5)

    assert list_user_reviews.execute(ANA) == ()
