"""Filtro de nota mínima (SCRUM-13) no caso de uso SearchCoffees."""

from datetime import date

from domain.entities.coffee import Coffee
from domain.value_objects.origin import Origin
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from tests.fakes.in_memory_review_repository import (
    InMemoryReviewRepository,
)
from tests.use_cases.test_search_coffees import rate
from use_cases.coffee.search_coffees import SearchCoffees
from use_cases.coffee.search_criteria import term_criterion
from use_cases.coffee.search_filters import FILTER_CRITERION_FACTORIES
from use_cases.coffee.search_min_rating import min_rating_criterion
from use_cases.dtos import SearchCoffeesInput

FACTORIES = (
    term_criterion,
    *FILTER_CRITERION_FACTORIES,
    min_rating_criterion,
)


def add(repository, name, origin=Origin.BRAZIL):
    return repository.add(
        Coffee(
            name=name,
            roaster="Café Lá",
            origin=origin,
            added_at=date(2026, 1, 15),
        )
    )


def search(repository, reviews, **fields):
    use_case = SearchCoffees(
        repository, reviews, criterion_factories=FACTORIES
    )
    return [
        result.name
        for result in use_case.execute(SearchCoffeesInput(**fields))
    ]


def test_min_rating_keeps_coffees_with_average_at_or_above():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add(repository, "Alto"), 5, 4)
    rate(reviews, add(repository, "Baixo"), 4, 3)

    assert search(repository, reviews, min_rating=4) == ["Alto"]


def test_min_rating_compares_the_rounded_average():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    # 99 / 25 = 3,96, exibida como "4,0".
    rate(reviews, add(repository, "Quase quatro"), *([4] * 24 + [3]))
    # 197 / 50 = 3,94, exibida como "3,9".
    rate(reviews, add(repository, "Abaixo"), *([4] * 47 + [3] * 3))

    assert search(repository, reviews, min_rating=4) == ["Quase quatro"]


def test_min_rating_excludes_coffees_without_reviews():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add(repository, "Avaliado"), 5)
    add(repository, "Sem avaliações")

    for minimum in (2, 3, 4):
        assert search(repository, reviews, min_rating=minimum) == ["Avaliado"]


def test_any_rating_does_not_filter_and_keeps_unrated_coffees():
    # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add(repository, "Avaliado"), 2)
    add(repository, "Sem avaliações")

    assert sorted(search(repository, reviews, min_rating=None)) == [
        "Avaliado",
        "Sem avaliações",
    ]


def test_each_min_rating_option_keeps_its_own_threshold():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add(repository, "Dois"), 2)
    rate(reviews, add(repository, "Tres"), 3)
    rate(reviews, add(repository, "Quatro"), 4)

    assert sorted(search(repository, reviews, min_rating=2)) == [
        "Dois",
        "Quatro",
        "Tres",
    ]
    assert sorted(search(repository, reviews, min_rating=3)) == [
        "Quatro",
        "Tres",
    ]
    assert search(repository, reviews, min_rating=4) == ["Quatro"]


def test_min_rating_outside_the_options_does_not_filter():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add(repository, "Avaliado"), 1)
    add(repository, "Sem avaliações")

    for unknown in (0, 1, 5, 6, -4):
        assert sorted(search(repository, reviews, min_rating=unknown)) == [
            "Avaliado",
            "Sem avaliações",
        ]


def test_min_rating_combines_with_term_filters_and_sort():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add(repository, "Bourbon A"), 4, 4, 4)
    rate(reviews, add(repository, "Bourbon B"), 5)
    rate(reviews, add(repository, "Bourbon C", Origin.PERU), 5)
    rate(reviews, add(repository, "Bourbon D"), 2)
    rate(reviews, add(repository, "Geisha"), 5)

    assert search(
        repository,
        reviews,
        term="bourbon",
        origins=("Brasil",),
        min_rating=4,
    ) == ["Bourbon B", "Bourbon A"]
    assert search(
        repository,
        reviews,
        term="bourbon",
        origins=("Brasil",),
        min_rating=4,
        sort="mais-avaliados",
    ) == ["Bourbon A", "Bourbon B"]
