from datetime import date

import pytest

from domain.entities.coffee import Coffee
from domain.exceptions import DomainError, ValidationError
from domain.value_objects.brew_recommendation import BrewRecommendation
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote

ADDED_AT = date(2026, 1, 15)


def make_coffee(**overrides):
    data = {
        "name": "Sítio da Torre",
        "roaster": "Café Lá",
        "origin": Origin.BRAZIL,
        "added_at": ADDED_AT,
    }
    data.update(overrides)
    return Coffee(**data)


def test_validation_error_is_a_domain_error():  # SCRUM-12
    assert issubclass(ValidationError, DomainError)


@pytest.mark.parametrize("name", ["", "   ", None])
def test_coffee_requires_name(name):  # SCRUM-13
    with pytest.raises(ValidationError):
        make_coffee(name=name)


@pytest.mark.parametrize("roaster", ["", "   ", None])
def test_coffee_requires_roaster(roaster):  # SCRUM-13
    with pytest.raises(ValidationError):
        make_coffee(roaster=roaster)


@pytest.mark.parametrize("origin", ["", "   ", None, "Atlântida"])
def test_coffee_requires_a_known_origin(origin):  # SCRUM-13
    with pytest.raises(ValidationError):
        make_coffee(origin=origin)


def test_coffee_accepts_origin_given_as_its_label():  # SCRUM-13
    coffee = make_coffee(origin="  Etiópia ")

    assert coffee.origin is Origin.ETHIOPIA


def test_coffee_keeps_the_catalog_entry_date():  # SCRUM-13
    assert make_coffee().added_at == ADDED_AT


def test_coffee_identity_ignores_accents_case_and_spaces():  # ADR 0003
    first = make_coffee(name="Sítio da Torre", roaster="Café Lá")
    second = make_coffee(name=" sitio da torre", roaster="CAFÉ LA ")

    assert first.identity == second.identity


def test_same_name_from_another_roaster_is_another_coffee():  # ADR 0003
    first = make_coffee(roaster="Café Lá")
    second = make_coffee(roaster="Torra Cá")

    assert first.identity != second.identity


def test_coffee_optional_attributes_default_to_empty():  # SCRUM-12
    coffee = make_coffee()

    assert coffee.producer is None
    assert coffee.variety is None
    assert coffee.process is None
    assert coffee.altitude is None
    assert coffee.roast is None
    assert coffee.sensory_notes == ()
    assert coffee.photo_url is None
    assert coffee.story is None
    assert coffee.brew_recommendations == ()


def test_coffee_keeps_every_optional_attribute():  # SCRUM-12
    brew = BrewRecommendation(method="V60", ratio="1:15")

    coffee = make_coffee(
        producer="Família Silva",
        variety="Bourbon",
        process=Process.NATURAL,
        altitude=1200,
        roast=Roast.MEDIUM,
        sensory_notes=[SensoryNote.CHOCOLATE, SensoryNote.CARAMEL],
        photo_url="/static/photos/a.svg",
        story="Uma história.",
        brew_recommendations=[brew],
    )

    assert coffee.producer == "Família Silva"
    assert coffee.variety == "Bourbon"
    assert coffee.process is Process.NATURAL
    assert coffee.altitude == 1200
    assert coffee.roast is Roast.MEDIUM
    assert coffee.sensory_notes == (
        SensoryNote.CHOCOLATE,
        SensoryNote.CARAMEL,
    )
    assert coffee.photo_url == "/static/photos/a.svg"
    assert coffee.story == "Uma história."
    assert coffee.brew_recommendations == (brew,)


def test_coffee_blank_free_text_becomes_none():  # SCRUM-12
    coffee = make_coffee(producer="  ", variety="", story="   ")

    assert coffee.producer is None
    assert coffee.variety is None
    assert coffee.story is None


def test_coffee_accepts_enum_labels_as_text():  # SCRUM-12
    coffee = make_coffee(
        process="lavado",
        roast="Média-escura",
        sensory_notes=["frutas vermelhas"],
    )

    assert coffee.process is Process.WASHED
    assert coffee.roast is Roast.MEDIUM_DARK
    assert coffee.sensory_notes == (SensoryNote.RED_FRUITS,)


@pytest.mark.parametrize("process", ["Defumado", 42])
def test_coffee_rejects_process_outside_the_closed_set(process):  # SCRUM-12
    with pytest.raises(ValidationError):
        make_coffee(process=process)


@pytest.mark.parametrize("roast", ["Carvão", 3])
def test_coffee_rejects_roast_outside_the_closed_set(roast):  # SCRUM-12
    with pytest.raises(ValidationError):
        make_coffee(roast=roast)


def test_coffee_rejects_sensory_note_outside_the_closed_set():  # SCRUM-12
    with pytest.raises(ValidationError):
        make_coffee(sensory_notes=["Chocolate", "Bacon"])


def test_coffee_rejects_repeated_sensory_notes():  # SCRUM-12
    with pytest.raises(ValidationError):
        make_coffee(
            sensory_notes=[SensoryNote.FLORAL, "floral"],
        )


@pytest.mark.parametrize("altitude", [0, -100, 1.5, "alto", True])
def test_coffee_rejects_non_positive_altitude(altitude):  # SCRUM-12
    with pytest.raises(ValidationError):
        make_coffee(altitude=altitude)


def test_coffee_rejects_invalid_brew_recommendation():  # SCRUM-12
    with pytest.raises(ValidationError):
        make_coffee(brew_recommendations=["V60"])


def test_coffee_rejects_free_text_that_is_not_a_string():  # SCRUM-12
    with pytest.raises(ValidationError):
        make_coffee(producer=123)
