from dataclasses import FrozenInstanceError
from datetime import date, datetime
from decimal import Decimal

import pytest

from domain.entities.coffee import Coffee
from domain.entities.review import Review
from domain.entities.user import User
from domain.exceptions import NotFoundError
from domain.value_objects.brew_recommendation import BrewRecommendation
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from tests.fakes.in_memory_review_repository import (
    InMemoryReviewRepository,
)
from tests.fakes.in_memory_user_repository import InMemoryUserRepository
from use_cases.coffee.get_coffee_details import GetCoffeeDetails


def make_use_case(coffees, reviews=None, users=None) -> GetCoffeeDetails:
    return GetCoffeeDetails(
        coffees,
        reviews or InMemoryReviewRepository(),
        users or InMemoryUserRepository(),
    )


def full_coffee():
    return Coffee(
        name="Sítio da Torre",
        roaster="Café Lá",
        origin=Origin.BRAZIL,
        added_at=date(2026, 1, 15),
        producer="Família Silva",
        variety="Bourbon Amarelo",
        process=Process.NATURAL,
        altitude=1100,
        roast=Roast.MEDIUM,
        sensory_notes=(SensoryNote.CHOCOLATE, SensoryNote.CARAMEL),
        photo_url="/static/photos/torra-media.svg",
        story="Cultivado há três gerações.",
        brew_recommendations=(
            BrewRecommendation(
                method="V60",
                ratio="1:15",
                grind="Média",
                temperature="92 °C",
            ),
            BrewRecommendation(method="Prensa francesa"),
        ),
    )


def test_get_details_returns_every_attribute_of_the_coffee():  # SCRUM-12
    repository = InMemoryCoffeeRepository()
    stored = repository.add(full_coffee())

    details = make_use_case(repository).execute(stored.id)

    assert details.id == stored.id
    assert details.name == "Sítio da Torre"
    assert details.roaster == "Café Lá"
    assert details.origin == "Brasil"
    assert details.producer == "Família Silva"
    assert details.variety == "Bourbon Amarelo"
    assert details.process == "Natural"
    assert details.altitude == 1100
    assert details.roast == "Média"
    assert details.sensory_notes == ("Chocolate", "Caramelo")
    assert details.photo_url == "/static/photos/torra-media.svg"
    assert details.story == "Cultivado há três gerações."
    assert [
        (b.method, b.ratio, b.grind, b.temperature)
        for b in details.brew_recommendations
    ] == [
        ("V60", "1:15", "Média", "92 °C"),
        ("Prensa francesa", None, None, None),
    ]


def test_get_details_leaves_missing_attributes_empty():  # SCRUM-12
    repository = InMemoryCoffeeRepository()
    stored = repository.add(
        Coffee(
            name="Blend",
            roaster="Café Lá",
            origin=Origin.BRAZIL,
            added_at=date(2026, 1, 15),
        )
    )

    details = make_use_case(repository).execute(stored.id)

    assert details.producer is None
    assert details.variety is None
    assert details.process is None
    assert details.altitude is None
    assert details.roast is None
    assert details.sensory_notes == ()
    assert details.photo_url is None
    assert details.story is None
    assert details.brew_recommendations == ()


def test_get_details_of_unknown_id_raises_not_found():  # SCRUM-12
    repository = InMemoryCoffeeRepository()
    repository.add(full_coffee())

    with pytest.raises(NotFoundError):
        make_use_case(repository).execute(999)


def test_details_dto_is_immutable():  # SCRUM-12
    repository = InMemoryCoffeeRepository()
    stored = repository.add(full_coffee())

    details = make_use_case(repository).execute(stored.id)

    with pytest.raises(FrozenInstanceError):
        details.name = "Outro"


def make_world():
    """Um café, três usuários e um use case ligado a fakes."""
    coffees = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    users = InMemoryUserRepository()
    coffee = coffees.add(full_coffee())
    ana = users.add(User("Ana", "ana@x.com", "h"))
    bia = users.add(User("Bia", "bia@x.com", "h"))
    caio = users.add(User("Caio", "caio@x.com", "h"))
    return coffees, reviews, users, coffee, ana, bia, caio


def add_review(reviews, coffee, author, rating, day, text=None):
    return reviews.add(
        Review(
            author_id=author.id,
            coffee_id=coffee.id,
            rating=rating,
            text=text,
            created_at=datetime(2026, 3, day, 10, 0),
        )
    )


def test_details_without_reviews_have_an_empty_list():  # SCRUM-14
    coffees, reviews, users, coffee, *_ = make_world()

    details = make_use_case(coffees, reviews, users).execute(coffee.id)

    assert details.reviews == ()
    assert details.user_has_reviewed is False


def test_reviews_are_listed_from_newest_to_oldest():  # SCRUM-14
    coffees, reviews, users, coffee, ana, bia, caio = make_world()
    add_review(reviews, coffee, ana, 3, day=1)
    add_review(reviews, coffee, caio, 5, day=20)
    add_review(reviews, coffee, bia, 4, day=10, text="Gostei.")

    details = make_use_case(coffees, reviews, users).execute(coffee.id)

    assert [r.author_name for r in details.reviews] == [
        "Caio",
        "Bia",
        "Ana",
    ]
    assert [r.rating for r in details.reviews] == [5, 4, 3]
    assert details.reviews[1].text == "Gostei."
    assert details.reviews[1].created_at == datetime(2026, 3, 10, 10, 0)
    assert details.reviews[0].edited is False


def test_reviews_made_at_the_same_moment_keep_a_stable_order():
    # SCRUM-14
    coffees, reviews, users, coffee, ana, bia, _ = make_world()
    add_review(reviews, coffee, ana, 3, day=5)
    add_review(reviews, coffee, bia, 4, day=5)

    details = make_use_case(coffees, reviews, users).execute(coffee.id)

    assert [r.author_name for r in details.reviews] == ["Bia", "Ana"]


def test_logged_user_review_comes_first_and_is_marked():  # SCRUM-14
    coffees, reviews, users, coffee, ana, bia, caio = make_world()
    add_review(reviews, coffee, ana, 3, day=1)
    add_review(reviews, coffee, bia, 4, day=10)
    add_review(reviews, coffee, caio, 5, day=20)

    details = make_use_case(coffees, reviews, users).execute(
        coffee.id, user_id=ana.id
    )

    assert [r.author_name for r in details.reviews] == [
        "Ana",
        "Caio",
        "Bia",
    ]
    assert [r.is_own for r in details.reviews] == [True, False, False]
    assert details.user_has_reviewed is True


def test_user_who_did_not_review_sees_no_own_review():  # SCRUM-14
    coffees, reviews, users, coffee, ana, bia, _ = make_world()
    add_review(reviews, coffee, bia, 4, day=10)

    details = make_use_case(coffees, reviews, users).execute(
        coffee.id, user_id=ana.id
    )

    assert details.user_has_reviewed is False
    assert [r.is_own for r in details.reviews] == [False]


def test_visitor_sees_no_own_review():  # SCRUM-14
    coffees, reviews, users, coffee, ana, *_ = make_world()
    add_review(reviews, coffee, ana, 4, day=10)

    details = make_use_case(coffees, reviews, users).execute(coffee.id)

    assert details.user_has_reviewed is False
    assert [r.is_own for r in details.reviews] == [False]


def test_reviews_of_other_coffees_are_not_listed():  # SCRUM-14
    coffees, reviews, users, coffee, ana, *_ = make_world()
    other = coffees.add(
        Coffee(
            name="Outro",
            roaster="Café Lá",
            origin=Origin.PERU,
            added_at=date(2026, 1, 16),
        )
    )
    add_review(reviews, other, ana, 4, day=10)

    details = make_use_case(coffees, reviews, users).execute(coffee.id)

    assert details.reviews == ()


def test_review_dto_does_not_expose_the_author_email():  # SCRUM-12
    coffees, reviews, users, coffee, ana, *_ = make_world()
    add_review(reviews, coffee, ana, 4, day=10)

    details = make_use_case(coffees, reviews, users).execute(coffee.id)

    assert "ana@x.com" not in repr(details)


def test_details_include_the_aggregated_rating():  # SCRUM-19
    coffees, reviews, users, coffee, ana, bia, caio = make_world()
    add_review(reviews, coffee, ana, 4, day=10)
    add_review(reviews, coffee, bia, 4, day=11)
    add_review(reviews, coffee, caio, 5, day=12)

    details = make_use_case(coffees, reviews, users).execute(coffee.id)

    assert details.rating.average == Decimal("4.3")
    assert details.rating.count == 3
    assert [b.count for b in details.rating.histogram] == [0, 0, 0, 2, 1]


def test_details_of_a_coffee_without_reviews_have_no_average():
    # SCRUM-19
    coffees, reviews, users, coffee, *_ = make_world()

    details = make_use_case(coffees, reviews, users).execute(coffee.id)

    assert details.rating.average is None
    assert details.rating.count == 0
    assert [b.percentage for b in details.rating.histogram] == [0] * 5
