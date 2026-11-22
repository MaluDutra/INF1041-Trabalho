from dataclasses import FrozenInstanceError
from datetime import date, datetime
from decimal import Decimal

import pytest

from domain.entities.coffee import Coffee
from domain.entities.review import Review
from domain.exceptions import ValidationError
from domain.value_objects.origin import Origin
from tests.fakes.in_memory_coffee_repository import (
    InMemoryCoffeeRepository,
)
from tests.fakes.in_memory_review_repository import (
    InMemoryReviewRepository,
)
from use_cases.coffee.search_coffees import SearchCoffees
from use_cases.coffee.search_criteria import SearchCriterion, term_criterion
from use_cases.coffee.search_sorting import BestRated, SortStrategy
from use_cases.dtos import SearchCoffeesInput


def add_coffee(
    repository,
    name,
    roaster="Café Lá",
    origin=Origin.BRAZIL,
    producer=None,
    added_at=date(2026, 1, 15),
):
    return repository.add(
        Coffee(
            name=name,
            roaster=roaster,
            origin=origin,
            added_at=added_at,
            producer=producer,
        )
    )


def rate(reviews, coffee, *ratings):
    """Grava um review por nota, cada um de um autor diferente."""
    for author_id, rating in enumerate(ratings, start=1):
        reviews.add(
            Review(
                author_id=author_id,
                coffee_id=coffee.id,
                rating=rating,
                text=None,
                created_at=datetime(2026, 3, 10, 14, 30),
            )
        )


def make_search(repository, reviews=None, **kwargs):
    reviews = InMemoryReviewRepository() if reviews is None else reviews
    return SearchCoffees(repository, reviews, **kwargs)


def search_names(repository, term):
    results = make_search(repository).execute(SearchCoffeesInput(term))
    return [result.name for result in results]


def test_search_with_empty_term_returns_whole_catalog():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon", "Torra Cá", Origin.COLOMBIA)
    add_coffee(repository, "Geisha", "Café Lá", Origin.ETHIOPIA)

    results = make_search(repository).execute(SearchCoffeesInput())

    assert [(r.name, r.roaster, r.origin) for r in results] == [
        ("Bourbon", "Torra Cá", "Colômbia"),
        ("Geisha", "Café Lá", "Etiópia"),
    ]


def test_search_orders_by_normalized_name():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    for name in ["Zebra", "Éclair", "banana", "Abacaxi"]:
        add_coffee(repository, name)

    results = make_search(repository).execute(SearchCoffeesInput())

    assert [r.name for r in results] == [
        "Abacaxi",
        "banana",
        "Éclair",
        "Zebra",
    ]


def test_search_of_empty_catalog_returns_nothing():  # SCRUM-13
    assert (
        make_search(InMemoryCoffeeRepository()).execute(SearchCoffeesInput())
        == []
    )


def test_search_results_are_immutable_dtos():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    stored = add_coffee(repository, "Bourbon")

    (result,) = make_search(repository).execute(SearchCoffeesInput())

    assert result.id == stored.id
    with pytest.raises(FrozenInstanceError):
        result.name = "Outro"


def test_search_term_matches_name_ignoring_accents_and_case():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Sítio da Torre")
    add_coffee(repository, "Geisha")

    assert search_names(repository, "sitio") == ["Sítio da Torre"]


def test_search_term_is_matched_as_a_whole_phrase():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Sítio da Torre")

    assert search_names(repository, "SITIO DA") == ["Sítio da Torre"]
    assert search_names(repository, "torre sítio") == []


def test_search_term_matches_roaster():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon", roaster="Torrefação Ágata")
    add_coffee(repository, "Geisha", roaster="Café Lá")

    assert search_names(repository, "agata") == ["Bourbon"]


def test_search_term_matches_producer():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon", producer="Fazenda São João")
    add_coffee(repository, "Geisha")

    assert search_names(repository, "sao joao") == ["Bourbon"]


@pytest.mark.parametrize("term", ["a", " a ", "á"])
def test_search_rejects_a_term_with_one_useful_character(term):  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon")

    with pytest.raises(ValidationError, match="2 caracteres"):
        make_search(repository).execute(SearchCoffeesInput(term))


@pytest.mark.parametrize("term", ["", "   "])
def test_search_with_blank_term_returns_whole_catalog(term):  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon")
    add_coffee(repository, "Geisha")

    assert search_names(repository, term) == ["Bourbon", "Geisha"]


def test_search_without_a_match_returns_nothing():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon")

    assert search_names(repository, "inexistente") == []


def test_search_accepts_extra_criteria_without_changing_the_use_case():
    # SCRUM-13: OCP, filtros novos entram como novas fábricas
    class OnlyColombia(SearchCriterion):
        def matches(self, coffee):
            return coffee.origin == Origin.COLOMBIA

    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Bourbon", origin=Origin.COLOMBIA)
    add_coffee(repository, "Bourbon Rosa", origin=Origin.BRAZIL)
    use_case = make_search(
        repository,
        criterion_factories=(term_criterion, lambda search: OnlyColombia()),
    )

    results = use_case.execute(SearchCoffeesInput("bourbon"))

    assert [r.name for r in results] == ["Bourbon"]


def test_search_result_carries_the_aggregate_rating():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    bourbon = add_coffee(repository, "Bourbon")
    add_coffee(repository, "Geisha")
    rate(reviews, bourbon, 5, 4, 4)

    results = make_search(repository, reviews).execute(SearchCoffeesInput())

    rated, unrated = results
    assert (rated.rating.average, rated.rating.count) == (Decimal("4.3"), 3)
    assert (unrated.rating.average, unrated.rating.count) == (None, 0)


def names_sorted_by(repository, reviews, sort="", term=""):
    use_case = make_search(repository, reviews)
    results = use_case.execute(SearchCoffeesInput(term, sort))
    return [result.name for result in results]


def test_default_sort_puts_the_higher_average_first():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add_coffee(repository, "Abacaxi"), 4, 4)
    rate(reviews, add_coffee(repository, "Zebra"), 5, 4)

    assert names_sorted_by(repository, reviews) == ["Zebra", "Abacaxi"]


def test_best_rated_breaks_equal_averages_by_review_count():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add_coffee(repository, "Abacaxi"), 4, 4)
    rate(reviews, add_coffee(repository, "Zebra"), 4, 4, 4)

    assert names_sorted_by(repository, reviews) == ["Zebra", "Abacaxi"]


def test_best_rated_breaks_full_ties_by_normalized_name():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    for name in ["Zebra", "Éclair", "banana"]:
        rate(reviews, add_coffee(repository, name), 4, 5)

    assert names_sorted_by(repository, reviews) == [
        "banana",
        "Éclair",
        "Zebra",
    ]


def test_best_rated_puts_unrated_coffees_last_in_alphabetical_order():
    # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    add_coffee(repository, "Zebra")
    rate(reviews, add_coffee(repository, "Mediano"), 1)
    add_coffee(repository, "Abacaxi")

    assert names_sorted_by(repository, reviews) == [
        "Mediano",
        "Abacaxi",
        "Zebra",
    ]


def test_best_rated_uses_the_exact_average_not_the_rounded_one():
    # SCRUM-13: 4,26 e 4,34 aparecem ambos como "4,3"
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add_coffee(repository, "Abacaxi"), *([4] * 37 + [5] * 13))
    rate(reviews, add_coffee(repository, "Zebra"), *([4] * 33 + [5] * 17))

    results = make_search(repository, reviews).execute(SearchCoffeesInput())

    assert [r.name for r in results] == ["Zebra", "Abacaxi"]
    assert {r.rating.average for r in results} == {Decimal("4.3")}


MOST_REVIEWED = "mais-avaliados"


def test_most_reviewed_puts_the_coffee_with_more_reviews_first():
    # SCRUM-13: 10 reviews vencem 3, mesmo com média menor
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add_coffee(repository, "Abacaxi"), 5, 5, 5)
    rate(reviews, add_coffee(repository, "Zebra"), *([3] * 10))

    assert names_sorted_by(repository, reviews, MOST_REVIEWED) == [
        "Zebra",
        "Abacaxi",
    ]


def test_most_reviewed_breaks_equal_counts_by_average_then_name():
    # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add_coffee(repository, "Zebra"), 5, 5)
    rate(reviews, add_coffee(repository, "Abacaxi"), 4, 4)
    rate(reviews, add_coffee(repository, "Banana"), 4, 4)

    assert names_sorted_by(repository, reviews, MOST_REVIEWED) == [
        "Zebra",
        "Abacaxi",
        "Banana",
    ]


def test_most_reviewed_puts_unrated_coffees_last_in_alphabetical_order():
    # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    add_coffee(repository, "Zebra")
    rate(reviews, add_coffee(repository, "Mediano"), 1)
    add_coffee(repository, "Abacaxi")

    assert names_sorted_by(repository, reviews, MOST_REVIEWED) == [
        "Mediano",
        "Abacaxi",
        "Zebra",
    ]


MOST_RECENT = "mais-recentes"


def test_most_recent_puts_the_latest_catalog_entry_first():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    add_coffee(repository, "Abacaxi", added_at=date(2026, 1, 10))
    add_coffee(repository, "Zebra", added_at=date(2026, 3, 1))
    add_coffee(repository, "Mediano", added_at=date(2026, 2, 1))

    assert names_sorted_by(repository, reviews, MOST_RECENT) == [
        "Zebra",
        "Mediano",
        "Abacaxi",
    ]


def test_most_recent_breaks_equal_dates_by_normalized_name():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    for name in ["Zebra", "Éclair", "banana"]:
        add_coffee(repository, name, added_at=date(2026, 3, 1))

    assert names_sorted_by(repository, reviews, MOST_RECENT) == [
        "banana",
        "Éclair",
        "Zebra",
    ]


def test_most_recent_ignores_the_ratings():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add_coffee(repository, "Antigo"), 5, 5)
    add_coffee(repository, "Novo", added_at=date(2026, 6, 1))

    assert names_sorted_by(repository, reviews, MOST_RECENT) == [
        "Novo",
        "Antigo",
    ]


def test_sort_combines_with_the_term():  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add_coffee(repository, "Bourbon Azul"), 3)
    rate(reviews, add_coffee(repository, "Bourbon Rosa"), 5, 5)
    rate(reviews, add_coffee(repository, "Geisha"), 5, 5, 5, 5)

    assert names_sorted_by(repository, reviews, term="bourbon") == [
        "Bourbon Rosa",
        "Bourbon Azul",
    ]
    assert names_sorted_by(
        repository, reviews, MOST_REVIEWED, term="bourbon"
    ) == ["Bourbon Rosa", "Bourbon Azul"]


@pytest.mark.parametrize("sort", ["", "inexistente", "MAIS-RECENTES"])
def test_unknown_sort_falls_back_to_best_rated(sort):  # SCRUM-13
    repository = InMemoryCoffeeRepository()
    reviews = InMemoryReviewRepository()
    rate(reviews, add_coffee(repository, "Abacaxi"), 3)
    rate(
        reviews,
        add_coffee(repository, "Zebra", added_at=date(2020, 1, 1)),
        5,
    )

    assert names_sorted_by(repository, reviews, sort) == ["Zebra", "Abacaxi"]


def test_search_accepts_a_new_sort_without_changing_the_use_case():
    # SCRUM-13: OCP, ordenação nova é classe nova
    class ByRoaster(SortStrategy):
        id = "torrefacao"
        label = "Torrefação"

        def key(self, coffee, rating):
            return (coffee.roaster,)

    repository = InMemoryCoffeeRepository()
    add_coffee(repository, "Abacaxi", roaster="Zeta")
    add_coffee(repository, "Zebra", roaster="Alfa")
    use_case = make_search(
        repository, sort_strategies=(BestRated(), ByRoaster())
    )

    results = use_case.execute(SearchCoffeesInput(sort="torrefacao"))

    assert [r.name for r in results] == ["Zebra", "Abacaxi"]
