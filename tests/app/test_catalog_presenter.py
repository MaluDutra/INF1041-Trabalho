from app.presenters.catalog_presenter import (
    present_cards,
    present_sort_options,
)
from tests.app.test_coffee_presenter import make_rating
from use_cases.coffee.search_sorting import (
    BestRated,
    MostRecent,
    MostReviewed,
)
from use_cases.dtos import CoffeeSummaryDTO

STRATEGIES = (BestRated(), MostReviewed(), MostRecent())


def make_summary(rating):
    return CoffeeSummaryDTO(
        id=7,
        name="Sítio da Torre",
        roaster="Café Lá",
        origin="Brasil",
        rating=rating,
    )


def card_summary(average, counts):
    (card,) = present_cards([make_summary(make_rating(average, counts))])
    return card.rating_summary


def test_card_shows_average_with_comma_and_plural():  # SCRUM-13
    assert card_summary("4.3", [0, 0, 1, 1, 10]) == "4,3 ★ · 12 avaliações"


def test_card_shows_singular_for_one_review():  # SCRUM-13
    assert card_summary("5.0", [0, 0, 0, 0, 1]) == "5,0 ★ · 1 avaliação"


def test_card_without_reviews_says_no_reviews():  # SCRUM-13
    assert card_summary(None, [0, 0, 0, 0, 0]) == "Sem avaliações"


def test_card_keeps_the_identifying_fields():  # SCRUM-13
    (card,) = present_cards([make_summary(make_rating(None, [0] * 5))])

    assert (card.id, card.name, card.roaster, card.origin) == (
        7,
        "Sítio da Torre",
        "Café Lá",
        "Brasil",
    )


def test_sort_options_mark_the_chosen_one():  # SCRUM-13
    options = present_sort_options(STRATEGIES, "mais-avaliados")

    assert [(o.id, o.label, o.selected) for o in options] == [
        ("melhor-avaliados", "Melhor avaliados", False),
        ("mais-avaliados", "Mais avaliados", True),
        ("mais-recentes", "Mais recentes", False),
    ]


def test_sort_options_mark_the_default_for_unknown_values():  # SCRUM-13
    for chosen in ["", "inexistente"]:
        options = present_sort_options(STRATEGIES, chosen)

        assert [o.id for o in options if o.selected] == ["melhor-avaliados"]
