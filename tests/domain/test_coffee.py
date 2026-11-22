from datetime import date

import pytest

from domain.entities.coffee import Coffee
from domain.exceptions import DomainError, ValidationError
from domain.value_objects.origin import Origin

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
