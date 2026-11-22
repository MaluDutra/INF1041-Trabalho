"""Rotas do catálogo, com Flask e SQLite temporário (não é caso de uso)."""

from datetime import date

import pytest

from app.main import create_app
from domain.entities.coffee import Coffee
from domain.value_objects.brew_recommendation import BrewRecommendation
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
from infra.db.database import connect, init_schema
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)


@pytest.fixture
def repository(tmp_path):
    db_path = tmp_path / "routes.db"
    connection = connect(db_path)
    init_schema(connection)
    connection.close()
    return SqliteCoffeeRepository(db_path)


@pytest.fixture
def client(repository, tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "routes.db")})
    return app.test_client()


def add_full_coffee(repository):
    return repository.add(
        Coffee(
            name="Sítio da Torre",
            roaster="Café Lá",
            origin=Origin.BRAZIL,
            added_at=date(2026, 1, 15),
            producer="Família Silva",
            variety="Bourbon Amarelo",
            process=Process.NATURAL,
            altitude=1100,
            roast=Roast.MEDIUM,
            sensory_notes=(SensoryNote.CHOCOLATE, SensoryNote.CARAMEL),
            photo_url="/static/photos/torra-media.svg",
            story="Cultivado há três gerações.",
            brew_recommendations=(
                BrewRecommendation("V60", "1:15", "Média", "92 °C"),
            ),
        )
    )


def add_bare_coffee(repository):
    return repository.add(
        Coffee(
            name="Blend",
            roaster="Café Lá",
            origin=Origin.PERU,
            added_at=date(2026, 1, 16),
        )
    )


def test_page_shows_every_attribute_of_a_full_coffee(
    client, repository
):  # SCRUM-12
    stored = add_full_coffee(repository)

    response = client.get(f"/cafes/{stored.id}")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    for text in [
        "Sítio da Torre",
        "Café Lá",
        "Brasil",
        "Família Silva",
        "Bourbon Amarelo",
        "Natural",
        "1.100 m",
        "Média",
        "Chocolate, Caramelo",
        "Cultivado há três gerações.",
        "V60",
        "1:15",
        "92 °C",
        "/static/photos/torra-media.svg",
    ]:
        assert text in html
    assert "Não informado" not in html


def test_page_of_a_bare_coffee_shows_not_informed(
    client, repository
):  # SCRUM-12
    stored = add_bare_coffee(repository)

    response = client.get(f"/cafes/{stored.id}")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert html.count("Não informado") >= 8
    assert "<img" not in html


def test_unknown_coffee_shows_friendly_404(client):  # SCRUM-12
    response = client.get("/cafes/999")

    html = response.get_data(as_text=True)
    assert response.status_code == 404
    assert "Café não encontrado" in html
    assert "Traceback" not in html


def test_non_numeric_address_shows_friendly_404(client):  # SCRUM-12
    response = client.get("/cafes/abc")

    assert response.status_code == 404
    assert "Página não encontrada" in response.get_data(as_text=True)


def test_home_cards_link_to_the_coffee_page(client, repository):  # SCRUM-12
    stored = add_full_coffee(repository)

    html = client.get("/").get_data(as_text=True)

    assert f'href="/cafes/{stored.id}"' in html
