from datetime import datetime
from decimal import Decimal

from app.presenters.coffee_presenter import NOT_INFORMED, present_details
from app.presenters.date_presenter import format_date
from use_cases.dtos import (
    BrewRecommendationDTO,
    CoffeeDetailsDTO,
    CoffeeRatingDTO,
    RatingBucketDTO,
    ReviewDTO,
)


def make_rating(average, counts):
    """Nota agregada de teste: ``counts`` vai da nota 1 até a 5."""
    total = sum(counts)
    return CoffeeRatingDTO(
        average=None if average is None else Decimal(average),
        count=total,
        histogram=tuple(
            RatingBucketDTO(
                rating=value,
                count=count,
                percentage=round(100 * count / total) if total else 0,
            )
            for value, count in enumerate(counts, start=1)
        ),
    )


def make_dto(**overrides):
    data = {
        "id": 1,
        "name": "Sítio da Torre",
        "roaster": "Café Lá",
        "origin": "Brasil",
        "producer": None,
        "variety": None,
        "process": None,
        "altitude": None,
        "roast": None,
        "sensory_notes": (),
        "photo_url": None,
        "story": None,
        "brew_recommendations": (),
        "rating": make_rating(None, [0, 0, 0, 0, 0]),
    }
    data.update(overrides)
    return CoffeeDetailsDTO(**data)


def test_empty_attributes_become_not_informed():  # SCRUM-12
    view = present_details(make_dto())

    assert view.producer == NOT_INFORMED
    assert view.variety == NOT_INFORMED
    assert view.process == NOT_INFORMED
    assert view.altitude == NOT_INFORMED
    assert view.roast == NOT_INFORMED
    assert view.sensory_notes == NOT_INFORMED
    assert view.story == NOT_INFORMED
    assert view.photo_url is None
    assert view.brew_recommendations == ()
    assert view.brew_empty_message == NOT_INFORMED


def test_not_informed_text_is_the_expected_one():  # SCRUM-12
    assert NOT_INFORMED == "Não informado"


def test_filled_attributes_are_formatted():  # SCRUM-12
    view = present_details(
        make_dto(
            producer="Família Silva",
            variety="Bourbon",
            process="Natural",
            altitude=1100,
            roast="Média",
            sensory_notes=("Chocolate", "Caramelo"),
            photo_url="/static/photos/a.svg",
            story="Uma história.",
            brew_recommendations=(
                BrewRecommendationDTO("V60", "1:15", "Média", "92 °C"),
            ),
        )
    )

    assert view.producer == "Família Silva"
    assert view.altitude == "1.100 m"
    assert view.sensory_notes == "Chocolate, Caramelo"
    assert view.photo_url == "/static/photos/a.svg"
    assert view.story == "Uma história."
    assert view.brew_empty_message is None


def test_missing_brew_parts_become_not_informed():  # SCRUM-12
    view = present_details(
        make_dto(
            brew_recommendations=(
                BrewRecommendationDTO("V60", "1:15", None, "92 °C"),
            )
        )
    )

    [brew] = view.brew_recommendations
    assert brew.method == "V60"
    assert brew.ratio == "1:15"
    assert brew.grind == NOT_INFORMED
    assert brew.temperature == "92 °C"


def make_review_dto(**overrides):
    data = {
        "id": 1,
        "author_id": 7,
        "author_name": "Ana",
        "rating": 4,
        "text": None,
        "created_at": datetime(2026, 3, 9, 23, 59),
        "edited": False,
        "is_own": False,
    }
    data.update(overrides)
    return ReviewDTO(**data)


def test_review_date_uses_the_brazilian_format():  # SCRUM-14
    view = present_details(make_dto(reviews=(make_review_dto(),)))

    assert view.reviews[0].date == "09/03/2026"


def test_review_shows_rating_author_and_text():  # SCRUM-14
    dto = make_review_dto(text="Achocolatado.")

    view = present_details(make_dto(reviews=(dto,))).reviews[0]

    assert view.rating == 4
    assert view.rating_label == "4 de 5"
    assert view.author_name == "Ana"
    assert view.text == "Achocolatado."


def test_review_without_text_has_no_text_view():  # SCRUM-14
    view = present_details(make_dto(reviews=(make_review_dto(),)))

    assert view.reviews[0].text is None


def test_own_review_is_flagged_and_review_count_is_exposed():
    # SCRUM-14
    view = present_details(
        make_dto(
            reviews=(
                make_review_dto(id=1, is_own=True),
                make_review_dto(id=2),
            ),
            user_has_reviewed=True,
        )
    )

    assert [r.is_own for r in view.reviews] == [True, False]
    assert view.user_has_reviewed is True
    assert view.reviews_empty_message is None


def test_no_reviews_shows_an_empty_message():  # SCRUM-14
    view = present_details(make_dto())

    assert view.reviews == ()
    assert view.reviews_empty_message == "Ainda não há avaliações."


def test_format_date_pads_day_and_month():  # SCRUM-14
    assert format_date(datetime(2026, 1, 5, 8, 0)) == "05/01/2026"


def test_rating_summary_uses_decimal_comma_and_plural():  # SCRUM-19
    rating = make_rating("4.3", [0, 0, 1, 7, 4])

    view = present_details(make_dto(rating=rating))

    assert view.rating.summary == "4,3 ★ · 12 avaliações"
    assert view.rating.has_reviews is True


def test_rating_summary_uses_singular_for_one_review():  # SCRUM-19
    rating = make_rating("1.0", [1, 0, 0, 0, 0])

    view = present_details(make_dto(rating=rating))

    assert view.rating.summary == "1,0 ★ · 1 avaliação"


def test_rating_summary_without_reviews_says_no_reviews():  # SCRUM-19
    view = present_details(make_dto())

    assert view.rating.summary == "Sem avaliações"
    assert view.rating.has_reviews is False


def test_histogram_is_shown_from_5_stars_down_to_1():  # SCRUM-19
    rating = make_rating("4.3", [1, 0, 0, 1, 2])

    rows = present_details(make_dto(rating=rating)).rating.histogram

    assert [row.label for row in rows] == ["5★", "4★", "3★", "2★", "1★"]
    assert [row.count for row in rows] == [2, 1, 0, 0, 1]
    assert [row.percentage_label for row in rows] == [
        "50%",
        "25%",
        "0%",
        "0%",
        "25%",
    ]
    assert [row.percentage for row in rows] == [50, 25, 0, 0, 25]


def test_histogram_without_reviews_shows_every_bar_empty():  # SCRUM-19
    rows = present_details(make_dto()).rating.histogram

    assert [row.label for row in rows] == ["5★", "4★", "3★", "2★", "1★"]
    assert [row.count for row in rows] == [0] * 5
    assert [row.percentage_label for row in rows] == ["0%"] * 5
