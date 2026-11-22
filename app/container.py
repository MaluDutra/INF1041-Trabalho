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
from use_cases.coffee.search_coffees import (
    DEFAULT_CRITERION_FACTORIES,
    SearchCoffees,
)
from use_cases.coffee.search_filters import FILTER_CRITERION_FACTORIES
from use_cases.coffee.search_sorting import (
    DEFAULT_SORT_STRATEGIES,
    SortStrategy,
)
from use_cases.review.create_review import CreateReview
from use_cases.review.delete_review import DeleteReview
from use_cases.review.list_user_reviews import ListUserReviews
from use_cases.review.update_review import UpdateReview
from use_cases.user.authenticate_user import AuthenticateUser
from use_cases.user.get_user import GetUser
from use_cases.user.register_user import RegisterUser


@dataclass(frozen=True)
class Container:
    search_coffees: SearchCoffees
    sort_strategies: tuple[SortStrategy, ...]
    get_coffee_details: GetCoffeeDetails
    register_user: RegisterUser
    authenticate_user: AuthenticateUser
    get_user: GetUser
    create_review: CreateReview
    update_review: UpdateReview
    delete_review: DeleteReview
    list_user_reviews: ListUserReviews


def build_container(db_path: str | Path) -> Container:
    coffee_repository = SqliteCoffeeRepository(db_path)
    user_repository = SqliteUserRepository(db_path)
    review_repository = SqliteReviewRepository(db_path)
    password_hasher = WerkzeugPasswordHasher()
    clock = SystemClock()
    sort_strategies = DEFAULT_SORT_STRATEGIES
    return Container(
        search_coffees=SearchCoffees(
            coffee_repository,
            review_repository,
            criterion_factories=(
                *DEFAULT_CRITERION_FACTORIES,
                *FILTER_CRITERION_FACTORIES,
            ),
            sort_strategies=sort_strategies,
        ),
        sort_strategies=sort_strategies,
        get_coffee_details=GetCoffeeDetails(
            coffee_repository, review_repository, user_repository
        ),
        register_user=RegisterUser(user_repository, password_hasher),
        authenticate_user=AuthenticateUser(user_repository, password_hasher),
        get_user=GetUser(user_repository),
        create_review=CreateReview(
            review_repository, coffee_repository, clock
        ),
        update_review=UpdateReview(review_repository),
        delete_review=DeleteReview(review_repository),
        list_user_reviews=ListUserReviews(
            review_repository, coffee_repository
        ),
    )
