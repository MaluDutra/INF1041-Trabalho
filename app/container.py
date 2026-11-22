"""Monta repositórios e casos de uso (injeção de dependências)."""

from dataclasses import dataclass
from pathlib import Path

from infra.clock.system_clock import SystemClock
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)
from infra.repositories.review_repository_sqlite import (
    SqliteReviewRepository,
)
from infra.repositories.user_repository_sqlite import SqliteUserRepository
from infra.security.werkzeug_password_hasher import WerkzeugPasswordHasher
from use_cases.coffee.get_coffee_details import GetCoffeeDetails
from use_cases.coffee.search_coffees import SearchCoffees
from use_cases.review.create_review import CreateReview
from use_cases.user.authenticate_user import AuthenticateUser
from use_cases.user.get_user import GetUser
from use_cases.user.register_user import RegisterUser


@dataclass(frozen=True)
class Container:
    search_coffees: SearchCoffees
    get_coffee_details: GetCoffeeDetails
    register_user: RegisterUser
    authenticate_user: AuthenticateUser
    get_user: GetUser
    create_review: CreateReview


def build_container(db_path: str | Path) -> Container:
    coffee_repository = SqliteCoffeeRepository(db_path)
    user_repository = SqliteUserRepository(db_path)
    review_repository = SqliteReviewRepository(db_path)
    password_hasher = WerkzeugPasswordHasher()
    clock = SystemClock()
    return Container(
        search_coffees=SearchCoffees(coffee_repository),
        get_coffee_details=GetCoffeeDetails(
            coffee_repository, review_repository, user_repository
        ),
        register_user=RegisterUser(user_repository, password_hasher),
        authenticate_user=AuthenticateUser(user_repository, password_hasher),
        get_user=GetUser(user_repository),
        create_review=CreateReview(
            review_repository, coffee_repository, clock
        ),
    )
