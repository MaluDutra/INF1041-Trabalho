"""Usuários e reviews de demonstração do seed (SCRUM-14, SCRUM-19)."""

import pytest

from domain.value_objects.coffee_rating import CoffeeRating
from infra.db.seed import init_database
from infra.db.seed_demo import DEMO_PASSWORD, DEMO_REVIEWS, DEMO_USERS
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)
from infra.repositories.review_repository_sqlite import (
    SqliteReviewRepository,
)
from infra.repositories.user_repository_sqlite import SqliteUserRepository
from infra.security.werkzeug_password_hasher import WerkzeugPasswordHasher
from use_cases.dtos import AuthenticateUserInput
from use_cases.user.authenticate_user import AuthenticateUser


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
    """Banco semeado uma vez; os testes só leem (o hash da senha é lento)."""
    path = tmp_path_factory.mktemp("demo") / "demo.db"
    init_database(path)
    return path


@pytest.fixture(scope="module")
def reviews(db_path):
    repository = SqliteReviewRepository(db_path)
    return [
        review
        for user in DEMO_USERS
        for review in repository.list_by_author(
            SqliteUserRepository(db_path).get_by_email(user.email).id
        )
    ]


@pytest.fixture(scope="module")
def ratings(db_path):
    """Nota agregada de cada café do seed, pelo nome."""
    coffees = SqliteCoffeeRepository(db_path).list_all()
    stored = SqliteReviewRepository(db_path).list_ratings_by_coffees(
        [coffee.id for coffee in coffees]
    )
    return {
        coffee.name: CoffeeRating.from_ratings(stored.get(coffee.id, []))
        for coffee in coffees
    }


def test_demo_users_can_log_in_with_the_documented_password(
    db_path,
):  # SCRUM-11
    authenticate = AuthenticateUser(
        SqliteUserRepository(db_path), WerkzeugPasswordHasher()
    )

    for demo_user in DEMO_USERS:
        user = authenticate.execute(
            AuthenticateUserInput(demo_user.email, DEMO_PASSWORD)
        )

        assert user.display_name == demo_user.display_name


def test_demo_passwords_are_stored_only_as_hashes(db_path):  # SCRUM-11
    users = SqliteUserRepository(db_path)

    for demo_user in DEMO_USERS:
        stored = users.get_by_email(demo_user.email)

        assert stored.password_hash != DEMO_PASSWORD
        assert DEMO_PASSWORD not in stored.password_hash


def test_some_coffees_are_left_without_reviews(ratings):  # SCRUM-19
    assert any(rating.count == 0 for rating in ratings.values())
    assert any(rating.count > 0 for rating in ratings.values())


def test_some_coffee_has_a_split_histogram(ratings):  # SCRUM-19
    def distinct_ratings(rating):
        return sum(1 for count in rating.histogram.values() if count)

    assert any(distinct_ratings(r) >= 3 for r in ratings.values())


def test_two_coffees_tie_on_average_with_different_counts(
    ratings,
):  # SCRUM-19
    rated = [r for r in ratings.values() if r.count]

    assert any(
        first.average == second.average and first.count != second.count
        for first in rated
        for second in rated
    )


def test_reviews_come_with_and_without_text(reviews):  # SCRUM-14
    assert any(review.text for review in reviews)
    assert any(review.text is None for review in reviews)


def test_some_review_is_marked_as_edited(reviews):  # SCRUM-14
    assert any(review.edited for review in reviews)
    assert not all(review.edited for review in reviews)


def test_reviews_have_distinct_creation_dates(reviews):  # SCRUM-14
    dates = [review.created_at for review in reviews]

    assert len(set(dates)) == len(dates)


def test_init_database_twice_does_not_duplicate_demo_data(
    tmp_path,
):  # SCRUM-14
    path = tmp_path / "twice.db"
    init_database(path)
    users = SqliteUserRepository(path)
    first = users.get_by_email(DEMO_USERS[0].email)

    assert init_database(path) is False

    assert users.get_by_email(DEMO_USERS[0].email) == first
    assert len(SqliteReviewRepository(path).list_by_author(first.id)) > 0


def test_demo_reviews_have_one_per_user_per_coffee():  # SCRUM-14
    pairs = [(r.coffee_name, r.user_email) for r in DEMO_REVIEWS]

    assert len(set(pairs)) == len(pairs)
