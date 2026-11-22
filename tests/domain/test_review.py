"""Invariantes da entidade Review (SCRUM-14)."""

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from domain.entities.review import RATING_SCALE, TEXT_MAX, Review
from domain.exceptions import ValidationError

NOW = datetime(2026, 3, 10, 14, 30)


def make_review(**overrides):
    data = {
        "author_id": 1,
        "coffee_id": 2,
        "rating": 4,
        "text": None,
        "created_at": NOW,
    }
    data.update(overrides)
    return Review(**data)


def test_new_review_is_not_edited_and_has_no_id():  # SCRUM-14
    review = make_review()

    assert review.edited is False
    assert review.id is None
    assert review.created_at == NOW


def test_rating_scale_is_1_to_5():  # SCRUM-14 / ADR 0001
    assert list(RATING_SCALE) == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
def test_review_accepts_every_rating_of_the_scale(rating):  # SCRUM-14
    assert make_review(rating=rating).rating == rating


@pytest.mark.parametrize("rating", [0, 6, -1, None, 3.5, "4", True])
def test_review_rejects_a_rating_out_of_the_scale(rating):  # SCRUM-14
    with pytest.raises(ValidationError, match="nota"):
        make_review(rating=rating)


def test_text_is_optional():  # SCRUM-14
    assert make_review(text=None).text is None


@pytest.mark.parametrize("text", ["", "   ", "\n\t "])
def test_blank_text_becomes_no_text(text):  # SCRUM-14
    assert make_review(text=text).text is None


def test_text_is_trimmed():  # SCRUM-14
    assert make_review(text="  Muito bom  ").text == "Muito bom"


def test_text_with_1000_characters_is_accepted():  # SCRUM-14
    assert len(make_review(text="a" * TEXT_MAX).text) == 1000


def test_text_with_1001_characters_is_rejected():  # SCRUM-14
    with pytest.raises(ValidationError, match="1000"):
        make_review(text="a" * (TEXT_MAX + 1))


def test_review_is_immutable():  # SCRUM-14
    with pytest.raises(FrozenInstanceError):
        make_review().rating = 5
