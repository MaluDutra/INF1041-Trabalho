import pytest

from domain.exceptions import ValidationError
from domain.value_objects.brew_recommendation import BrewRecommendation


@pytest.mark.parametrize("method", ["", "   ", None])
def test_brew_recommendation_requires_method(method):  # SCRUM-12
    with pytest.raises(ValidationError):
        BrewRecommendation(method=method)


def test_brew_recommendation_optional_parts_default_to_none():  # SCRUM-12
    recommendation = BrewRecommendation(method="V60")

    assert recommendation.ratio is None
    assert recommendation.grind is None
    assert recommendation.temperature is None


def test_brew_recommendation_trims_text_and_blank_becomes_none():  # SCRUM-12
    recommendation = BrewRecommendation(
        method="  V60 ", ratio=" 1:15 ", grind="   ", temperature=None
    )

    assert recommendation.method == "V60"
    assert recommendation.ratio == "1:15"
    assert recommendation.grind is None
    assert recommendation.temperature is None
