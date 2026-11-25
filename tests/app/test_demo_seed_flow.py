"""O seed de demonstração funcionando na aplicação (SCRUM-14, SCRUM-19)."""

import pytest

from app.main import create_app
from infra.db.seed import init_database
from infra.db.seed_demo import DEMO_PASSWORD, DEMO_USERS
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("flow") / "flow.db"
    init_database(path)
    return path


@pytest.fixture
def client(db_path):
    app = create_app({"DATABASE": str(db_path), "SECRET_KEY": "test"})
    return app.test_client()


def home(client, **query):
    return client.get("/", query_string=query).get_data(as_text=True)


def test_demo_user_logs_in_and_sees_their_own_reviews(client):  # SCRUM-14
    ana = DEMO_USERS[0]

    response = client.post(
        "/entrar", data={"email": ana.email, "password": DEMO_PASSWORD}
    )
    html = client.get("/minhas-avaliacoes").get_data(as_text=True)

    assert response.status_code == 302
    assert "Sítio da Torre" in html
    assert "Doce e redondo" in html
    assert "Equilibrado." not in html  # review do Bruno


def test_home_orders_best_rated_with_tie_broken_by_review_count(
    client,
):  # SCRUM-19
    html = home(client)

    names = ("Tarrazú Honey", "Yirgacheffe", "Sítio da Torre", "Santa Inês")
    positions = [html.index(name) for name in names]
    assert positions == sorted(positions)


def test_home_shows_no_reviews_for_the_unrated_coffee(client):  # SCRUM-19
    html = home(client, q="Mandheling")

    assert "Mandheling Sumatra" in html
    assert "Sem avaliações" in html


def test_min_rating_filter_drops_low_and_unrated_coffees(client):  # SCRUM-19
    html = home(client, nota_minima="4")

    assert "Yirgacheffe" in html
    assert "Kirinyaga" not in html
    assert "Mandheling" not in html


def test_split_coffee_page_shows_one_review_of_each_rating(
    client, db_path
):  # SCRUM-19
    coffee = next(
        c
        for c in SqliteCoffeeRepository(db_path).list_all()
        if c.name == "Kirinyaga AA"
    )

    html = client.get(f"/cafes/{coffee.id}").get_data(as_text=True)

    assert html.count('class="histogram-row"') == 5
    assert html.count('<span class="histogram-count">1</span>') == 5
    assert "editado" in html
