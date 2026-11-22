from app.presenters.coffee_presenter import NOT_INFORMED, present_details
from use_cases.dtos import BrewRecommendationDTO, CoffeeDetailsDTO


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
