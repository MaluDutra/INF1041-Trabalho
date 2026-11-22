"""Rotas do catálogo, com Flask e SQLite temporário (não é caso de uso)."""

import re
from datetime import date, datetime

import pytest

from app.main import create_app
from domain.entities.coffee import Coffee
from domain.entities.review import Review
from domain.entities.user import User
from domain.value_objects.brew_recommendation import BrewRecommendation
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
from infra.db.database import connect, init_schema
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)
from infra.repositories.review_repository_sqlite import (
    SqliteReviewRepository,
)
from infra.repositories.user_repository_sqlite import SqliteUserRepository


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


def test_home_search_lists_only_matching_coffees(client, repository):
    # SCRUM-13
    add_full_coffee(repository)
    add_bare_coffee(repository)

    html = client.get("/?q=sitio").get_data(as_text=True)

    assert "Sítio da Torre" in html
    assert "Blend" not in html


@pytest.mark.parametrize("term", ["a", "+a+"])
def test_home_short_term_shows_warning_and_does_not_search(
    client, repository, term
):  # SCRUM-13
    add_full_coffee(repository)

    response = client.get("/", query_string={"q": term.replace("+", " ")})

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "pelo menos 2 caracteres" in html
    assert "Sítio da Torre" not in html
    assert "Nenhum café encontrado" not in html


def test_home_without_matches_shows_tips_instead_of_empty_list(
    client, repository
):  # SCRUM-13
    add_full_coffee(repository)

    html = client.get("/?q=inexistente").get_data(as_text=True)

    assert "Nenhum café encontrado" in html
    assert "grafia" in html
    assert "termo mais curto" in html
    assert "filtros" in html
    assert "coffee-grid" not in html
    assert "O catálogo ainda não tem cafés" not in html


def test_home_keeps_the_term_in_the_search_field(client, repository):
    # SCRUM-13
    add_full_coffee(repository)

    html = client.get("/?q=Sítio").get_data(as_text=True)

    assert 'name="q"' in html
    assert 'value="Sítio"' in html


def test_home_escapes_the_term_in_the_search_field(client):  # SCRUM-13
    html = client.get('/?q="><script>').get_data(as_text=True)

    assert "<script>" not in html


@pytest.mark.parametrize("term", ["", "   "])
def test_home_blank_term_lists_whole_catalog_without_warning(
    client, repository, term
):  # SCRUM-13
    add_full_coffee(repository)
    add_bare_coffee(repository)

    html = client.get("/", query_string={"q": term}).get_data(as_text=True)

    assert "Sítio da Torre" in html
    assert "Blend" in html
    assert "caracteres" not in html
    assert "Nenhum café encontrado" not in html


def add_review(tmp_path, coffee, *ratings):
    """Grava um review por nota, cada um de um usuário novo."""
    db_path = tmp_path / "routes.db"
    users = SqliteUserRepository(db_path)
    reviews = SqliteReviewRepository(db_path)
    for number, rating in enumerate(ratings, start=1):
        email = f"ana{number}-{coffee.id}@x.com"
        user = users.add(User(f"Ana{number}", email, "h"))
        reviews.add(
            Review(
                author_id=user.id,
                coffee_id=coffee.id,
                rating=rating,
                text=None,
                created_at=datetime(2026, 3, 10, 14, 30),
            )
        )


def test_home_cards_show_the_aggregate_rating(
    client, repository, tmp_path
):  # SCRUM-13
    rated = add_full_coffee(repository)
    add_bare_coffee(repository)
    add_review(tmp_path, rated, 5, 4)

    html = client.get("/").get_data(as_text=True)

    assert "4,5 ★ · 2 avaliações" in html
    assert "Sem avaliações" in html


def add_named_coffee(repository, name, added_at=date(2026, 1, 15)):
    return repository.add(
        Coffee(
            name=name,
            roaster="Café Lá",
            origin=Origin.BRAZIL,
            added_at=added_at,
        )
    )


def card_order(html, *names):
    return sorted(names, key=html.index)


def test_home_sorts_by_best_rated_by_default(
    client, repository, tmp_path
):  # SCRUM-13
    add_review(tmp_path, add_named_coffee(repository, "Abacaxi"), 3)
    add_review(tmp_path, add_named_coffee(repository, "Zebra"), 5)

    html = client.get("/").get_data(as_text=True)

    assert card_order(html, "Abacaxi", "Zebra") == ["Zebra", "Abacaxi"]


def test_home_sorts_by_the_chosen_option_and_term(
    client, repository, tmp_path
):  # SCRUM-13
    add_review(tmp_path, add_named_coffee(repository, "Bourbon A"), 5)
    add_review(tmp_path, add_named_coffee(repository, "Bourbon B"), 3, 3, 3)
    add_named_coffee(repository, "Geisha")

    html = client.get(
        "/", query_string={"q": "bourbon", "ordenar": "mais-avaliados"}
    ).get_data(as_text=True)

    assert card_order(html, "Bourbon A", "Bourbon B") == [
        "Bourbon B",
        "Bourbon A",
    ]
    assert "Geisha" not in html


def test_home_sorts_by_most_recent(client, repository):  # SCRUM-13
    add_named_coffee(repository, "Antigo", date(2026, 1, 1))
    add_named_coffee(repository, "Novo", date(2026, 6, 1))

    html = client.get("/?ordenar=mais-recentes").get_data(as_text=True)

    assert card_order(html, "Antigo", "Novo") == ["Novo", "Antigo"]


def selected_options(html):
    return re.findall(r'<option value="([^"]+)" selected>', html)


def test_home_lists_the_sort_options_with_the_default_marked(
    client,
):  # SCRUM-13
    html = client.get("/").get_data(as_text=True)

    for label in ["Melhor avaliados", "Mais avaliados", "Mais recentes"]:
        assert label in html
    assert 'name="ordenar"' in html
    assert selected_options(html) == ["melhor-avaliados"]


def test_home_keeps_the_chosen_sort_marked(client, repository):  # SCRUM-13
    add_named_coffee(repository, "Bourbon")

    for query in [
        "/?ordenar=mais-recentes",
        "/?q=bourbon&ordenar=mais-recentes",
    ]:
        html = client.get(query).get_data(as_text=True)

        assert selected_options(html) == ["mais-recentes"]


def test_home_keeps_the_chosen_sort_when_the_term_is_short(client):
    # SCRUM-13
    html = client.get("/?q=a&ordenar=mais-avaliados").get_data(as_text=True)

    assert "pelo menos 2 caracteres" in html
    assert selected_options(html) == ["mais-avaliados"]


def test_home_unknown_sort_falls_back_to_the_default(
    client, repository, tmp_path
):  # SCRUM-13
    add_review(tmp_path, add_named_coffee(repository, "Abacaxi"), 3)
    add_review(tmp_path, add_named_coffee(repository, "Zebra"), 5)

    response = client.get("/?ordenar=<script>")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert card_order(html, "Abacaxi", "Zebra") == ["Zebra", "Abacaxi"]
    assert selected_options(html) == ["melhor-avaliados"]
    assert "<script>" not in html
