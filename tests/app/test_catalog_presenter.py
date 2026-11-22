from app.presenters.catalog_presenter import (
    FILTER_FIELDS,
    has_active_filters,
    parse_min_rating,
    present_cards,
    present_filter_groups,
    present_min_rating_options,
    present_sort_options,
)
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
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


def test_filter_groups_list_the_options_of_each_domain_set():  # SCRUM-13
    groups = present_filter_groups({})

    options = {g.param: [o.value for o in g.options] for g in groups}
    assert [g.label for g in groups] == [
        "Origem",
        "Processo",
        "Torra",
        "Nota sensorial",
    ]
    assert options == {
        "origem": [m.value for m in Origin],
        "processo": [m.value for m in Process],
        "torra": [m.value for m in Roast],
        "nota": [m.value for m in SensoryNote],
    }
    assert not any(o.checked for g in groups for o in g.options)


def test_filter_groups_check_the_selected_values():  # SCRUM-13
    groups = present_filter_groups(
        {"origem": ["Brasil", "etiopia"], "nota": ["Frutado"]}
    )

    checked = {
        g.param: [o.value for o in g.options if o.checked] for g in groups
    }
    assert checked == {
        "origem": ["Brasil", "Etiópia"],
        "processo": [],
        "torra": [],
        "nota": ["Frutado"],
    }


def test_filter_groups_ignore_unknown_selected_values():  # SCRUM-13
    groups = present_filter_groups({"origem": ["Atlântida"], "torra": [""]})

    assert not has_active_filters(groups)


def test_has_active_filters_is_true_with_any_checked_option():
    # SCRUM-13
    assert has_active_filters(present_filter_groups({"torra": ["Clara"]}))
    assert not has_active_filters(present_filter_groups({}))


def test_filter_fields_name_the_search_input_attributes():  # SCRUM-13
    assert {f.param: f.input_field for f in FILTER_FIELDS} == {
        "origem": "origins",
        "processo": "processes",
        "torra": "roasts",
        "nota": "sensory_notes",
    }


def test_min_rating_options_list_any_and_the_scale_thresholds():
    # SCRUM-13
    options = present_min_rating_options(None)

    assert [(o.value, o.label, o.selected) for o in options] == [
        ("", "Qualquer", True),
        ("4", "4+", False),
        ("3", "3+", False),
        ("2", "2+", False),
    ]


def test_min_rating_options_mark_the_chosen_one():  # SCRUM-13
    options = present_min_rating_options(3)

    assert [o.value for o in options if o.selected] == ["3"]


def test_parse_min_rating_accepts_only_the_listed_options():  # SCRUM-13
    assert parse_min_rating("4") == 4
    assert parse_min_rating("2") == 2
    for raw in ["", "1", "5", "9", "-3", "abc", "4.5", "<script>", " 4"]:
        assert parse_min_rating(raw) is None


def test_a_min_rating_counts_as_an_active_filter():  # SCRUM-13
    groups = present_filter_groups({})

    assert has_active_filters(groups, min_rating=4)
    assert not has_active_filters(groups, min_rating=None)
