"""Página "Minhas avaliações", com Flask e SQLite temporário."""

from datetime import date, datetime

import pytest

from app.main import create_app
from domain.entities.coffee import Coffee
from domain.entities.review import Review
from domain.value_objects.origin import Origin
from infra.db.database import connect, init_schema
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)
from infra.repositories.review_repository_sqlite import (
    SqliteReviewRepository,
)

PAGE = "/minhas-avaliacoes"


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "my_reviews.db"
    connection = connect(path)
    init_schema(connection)
    connection.close()
    return path


@pytest.fixture
def client(db_path):
    app = create_app({"DATABASE": str(db_path), "SECRET_KEY": "test"})
    return app.test_client()


@pytest.fixture
def coffees(db_path):
    repository = SqliteCoffeeRepository(db_path)
    return [
        repository.add(
            Coffee(
                name=name,
                roaster="Café Lá",
                origin=Origin.BRAZIL,
                added_at=date(2026, 1, 15),
            )
        )
        for name in ("Sítio da Torre", "Blend da Casa", "Reserva")
    ]


def add_review(db_path, user_id, coffee, day, rating=4, text=None, **extra):
    """Grava um review direto no banco, com data conhecida."""
    return SqliteReviewRepository(db_path).add(
        Review(
            author_id=user_id,
            coffee_id=coffee.id,
            rating=rating,
            text=text,
            created_at=datetime(2026, 3, day, 10, 0),
            **extra,
        )
    )


def page(client):
    return client.get(PAGE).get_data(as_text=True)


def sign_up(client, name="Ana", email="ana@x.com"):
    return client.post(
        "/cadastro",
        data={
            "display_name": name,
            "email": email,
            "password": "abcd1234",
        },
    )


def test_visitor_is_sent_to_login_and_comes_back_to_the_page(
    client,
):  # SCRUM-14
    sign_up(client)
    client.post("/sair")

    response = client.get(PAGE)

    assert response.status_code == 302
    assert response.headers["Location"] == f"/entrar?next={PAGE}"
    login = client.post(
        "/entrar",
        data={
            "email": "ana@x.com",
            "password": "abcd1234",
            "next": PAGE,
        },
    )
    assert login.headers["Location"] == PAGE


def test_page_lists_the_reviews_from_newest_to_oldest(
    client, db_path, coffees
):  # SCRUM-14
    sign_up(client)
    add_review(db_path, 1, coffees[0], day=5, rating=2, text="Amargo")
    add_review(db_path, 1, coffees[1], day=20, rating=5, text="Doce")
    add_review(db_path, 1, coffees[2], day=12, rating=3)

    html = page(client)

    positions = [
        html.index(name) for name in ("Blend da Casa", "Reserva", "Sítio")
    ]
    assert positions == sorted(positions)
    assert f'href="/cafes/{coffees[1].id}"' in html
    assert "5 de 5" in html and "Doce" in html
    assert "20/03/2026" in html
    assert "2 de 5" in html and "Amargo" in html


def test_page_never_shows_reviews_of_other_people(
    client, db_path, coffees
):  # SCRUM-14
    sign_up(client)
    sign_up(client, name="Bia", email="bia@x.com")
    client.post("/sair")
    add_review(db_path, 2, coffees[1], day=6, text="Segredo da Bia")
    add_review(db_path, 1, coffees[0], day=5, text="Meu texto")
    client.post("/entrar", data={"email": "ana@x.com", "password": "abcd1234"})

    html = page(client)

    assert "Meu texto" in html
    assert "Segredo da Bia" not in html
    assert "Blend da Casa" not in html


def test_page_marks_an_edited_review_and_only_that_one(
    client, db_path, coffees
):  # SCRUM-14
    sign_up(client)
    add_review(db_path, 1, coffees[0], day=5, edited=True)
    add_review(db_path, 1, coffees[1], day=6)

    html = page(client)

    assert html.count("editado") == 1


def test_page_invites_a_user_without_reviews_to_explore_the_catalog(
    client,
):  # SCRUM-14
    sign_up(client)

    html = page(client)

    assert "Você ainda não avaliou nenhum café." in html
    assert 'href="/"' in html
    assert "review-list" not in html


def test_header_links_to_the_page_only_for_a_logged_in_user(
    client,
):  # SCRUM-14
    assert f'href="{PAGE}"' not in client.get("/").get_data(as_text=True)

    sign_up(client)

    html = client.get("/").get_data(as_text=True)
    assert f'href="{PAGE}"' in html
    assert "Minhas avaliações" in html


def edit_url(coffee, review_id):
    return f"/cafes/{coffee.id}/avaliacoes/{review_id}/editar"


def delete_url(coffee, review_id):
    return f"/cafes/{coffee.id}/avaliacoes/{review_id}/excluir"


@pytest.fixture
def reviewed(client, db_path, coffees):
    """Ana logada, com um review no primeiro café."""
    sign_up(client)
    return add_review(db_path, 1, coffees[0], day=5, rating=2, text="Velho")


def test_each_item_has_edit_and_delete_actions_that_return_here(
    client, coffees, reviewed
):  # SCRUM-14
    html = page(client)

    assert f'href="{edit_url(coffees[0], reviewed.id)}?next={PAGE}"' in html
    assert f'action="{delete_url(coffees[0], reviewed.id)}"' in html
    assert f'name="next" value="{PAGE}"' in html


def test_edit_link_opens_the_form_on_the_coffee_page_keeping_the_next(
    client, coffees, reviewed
):  # SCRUM-14
    response = client.get(
        edit_url(coffees[0], reviewed.id), query_string={"next": PAGE}
    )

    assert response.status_code == 302
    location = response.headers["Location"]
    assert location.startswith(f"/cafes/{coffees[0].id}?")
    assert "editar=1" in location
    html = client.get(location).get_data(as_text=True)
    assert f'name="next" value="{PAGE}"' in html


def test_saving_an_edit_started_here_returns_to_the_page(
    client, coffees, reviewed
):  # SCRUM-14
    response = client.post(
        edit_url(coffees[0], reviewed.id),
        data={"rating": "5", "text": "Novo texto", "next": PAGE},
    )

    assert response.status_code == 302
    assert response.headers["Location"] == PAGE
    html = page(client)
    assert "Novo texto" in html and "5 de 5" in html
    assert "Velho" not in html
    assert "editado" in html


def test_edit_without_next_still_returns_to_the_coffee_page(
    client, coffees, reviewed
):  # SCRUM-14
    response = client.post(
        edit_url(coffees[0], reviewed.id), data={"rating": "5"}
    )

    assert response.headers["Location"].startswith(f"/cafes/{coffees[0].id}")


@pytest.mark.parametrize("target", ["//evil.com", "https://evil.com", "x"])
def test_edit_ignores_a_next_that_is_not_an_internal_path(
    client, coffees, reviewed, target
):  # SCRUM-14
    response = client.post(
        edit_url(coffees[0], reviewed.id),
        data={"rating": "5", "next": target},
    )

    assert response.headers["Location"].startswith(f"/cafes/{coffees[0].id}")


def test_invalid_edit_keeps_the_next_in_the_form(
    client, coffees, reviewed
):  # SCRUM-14
    response = client.post(
        edit_url(coffees[0], reviewed.id),
        data={"rating": "9", "next": PAGE},
    )

    assert response.status_code == 400
    assert f'name="next" value="{PAGE}"' in response.get_data(as_text=True)


def test_deleting_from_the_page_returns_to_it_without_the_review(
    client, coffees, reviewed
):  # SCRUM-14
    response = client.post(
        delete_url(coffees[0], reviewed.id), data={"next": PAGE}
    )

    assert response.status_code == 302
    assert response.headers["Location"] == PAGE
    assert "Sítio da Torre" not in page(client)


@pytest.mark.parametrize("target", ["//evil.com", "https://evil.com"])
def test_delete_ignores_a_next_that_is_not_an_internal_path(
    client, coffees, reviewed, target
):  # SCRUM-14
    response = client.post(
        delete_url(coffees[0], reviewed.id), data={"next": target}
    )

    assert response.headers["Location"] == f"/cafes/{coffees[0].id}"
