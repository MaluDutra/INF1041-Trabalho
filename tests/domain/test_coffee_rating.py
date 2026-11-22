"""Objeto de valor CoffeeRating, a Nota agregada (SCRUM-19)."""

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from domain.entities.review import RATING_SCALE
from domain.exceptions import ValidationError
from domain.value_objects.coffee_rating import CoffeeRating


def test_average_of_4_4_5_4_is_exactly_4_25_and_rounds_half_up():
    # SCRUM-19
    rating = CoffeeRating.from_ratings([4, 4, 5, 4])

    assert rating.average == 4.25
    assert rating.rounded_average == Decimal("4.3")


def test_rounding_is_half_up_and_not_bankers_rounding():  # SCRUM-19
    # média 4,35 (87 / 20): o round() do Python daria 4,3 (float e par)
    rating = CoffeeRating.from_ratings([4] * 13 + [5] * 7)

    assert rating.average == pytest.approx(4.35)
    assert rating.rounded_average == Decimal("4.4")


def test_average_below_the_half_rounds_down():  # SCRUM-19
    rating = CoffeeRating.from_ratings([1, 1, 2])

    assert rating.rounded_average == Decimal("1.3")


def test_single_review_has_an_average_with_no_minimum_count():
    # SCRUM-19
    rating = CoffeeRating.from_ratings([1])

    assert rating.count == 1
    assert rating.rounded_average == Decimal("1.0")
    assert str(rating.rounded_average) == "1.0"


def test_no_ratings_means_no_average():  # SCRUM-19
    rating = CoffeeRating.from_ratings([])

    assert rating.count == 0
    assert rating.average is None
    assert rating.rounded_average is None


def test_histogram_has_one_bucket_per_value_of_the_scale():  # SCRUM-19
    rating = CoffeeRating.from_ratings([5, 5, 4, 1])

    assert dict(rating.histogram) == {1: 1, 2: 0, 3: 0, 4: 1, 5: 2}
    assert list(rating.histogram) == list(RATING_SCALE)


def test_percentage_of_each_rating():  # SCRUM-19
    rating = CoffeeRating.from_ratings([5, 5, 4, 1])

    assert [rating.percentage(value) for value in (5, 4, 3, 2, 1)] == [
        50,
        25,
        0,
        0,
        25,
    ]


def test_percentage_rounds_half_up_to_an_integer():  # SCRUM-19
    thirds = CoffeeRating.from_ratings([1, 2, 3])
    eighths = CoffeeRating.from_ratings([5, 4, 4, 4, 4, 4, 4, 4])

    assert thirds.percentage(1) == 33
    assert eighths.percentage(5) == 13  # 12,5% sobe


def test_percentages_without_ratings_are_zero_with_no_division_by_zero():
    # SCRUM-19
    rating = CoffeeRating.from_ratings([])

    assert dict(rating.histogram) == {value: 0 for value in RATING_SCALE}
    assert [rating.percentage(value) for value in RATING_SCALE] == [0] * 5


def test_rating_outside_the_scale_is_rejected():  # SCRUM-19
    with pytest.raises(ValidationError):
        CoffeeRating.from_ratings([4, 6])


def test_rating_is_immutable():  # SCRUM-19
    rating = CoffeeRating.from_ratings([4])

    with pytest.raises(FrozenInstanceError):
        rating.histogram = {}
