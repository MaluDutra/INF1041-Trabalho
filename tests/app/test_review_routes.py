"""Rotas de avaliação, com Flask e SQLite temporário."""

import re
from datetime import date

import pytest

from app.main import create_app
from domain.entities.coffee import Coffee
from domain.value_objects.origin import Origin
from infra.db.database import connect, init_schema
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)

FORM_OPEN = re.compile(r'<details[^>]*id="avaliar"[^>]*\sopen\b')


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "reviews.db"
    connection = connect(path)
    init_schema(connection)
    connection.close()
    return path


@pytest.fixture
def app(db_path):
    return create_app({"DATABASE": str(db_path), "SECRET_KEY": "test"})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def coffee(db_path):
    return SqliteCoffeeRepository(db_path).add(
        Coffee(
            name="Sítio da Torre",
            roaster="Café Lá",
            origin=Origin.BRAZIL,
            added_at=date(2026, 1, 15),
        )
    )


def sign_up(client, name="Ana", email="ana@x.com"):
    return client.post(
        "/cadastro",
        data={
            "display_name": name,
            "email": email,
            "password": "abcd1234",
        },
    )


def review_url(coffee):
    return f"/cafes/{coffee.id}/avaliar"


def count_reviews(db_path):
    connection = connect(db_path)
    try:
        row = connection.execute("SELECT COUNT(*) FROM reviews").fetchone()
        return row[0]
    finally:
        connection.close()


def page(client, coffee):
    return client.get(f"/cafes/{coffee.id}").get_data(as_text=True)


def test_visitor_sees_the_review_button_but_no_form(client, coffee):
    # SCRUM-14
    html = page(client, coffee)

    assert f'href="{review_url(coffee)}"' in html
    assert "Avaliar" in html
    assert 'name="rating"' not in html
    assert "Editar minha avaliação" not in html


def test_user_without_review_sees_the_form(client, coffee):  # SCRUM-14
    sign_up(client)

    html = page(client, coffee)

    assert 'name="rating"' in html
    assert 'name="text"' in html
    assert f'action="{review_url(coffee)}"' in html
    assert "Editar minha avaliação" not in html


def test_valid_review_is_created_and_shown_at_the_top(
    client, coffee, db_path
):  # SCRUM-14
    sign_up(client, name="Ana")

    response = client.post(review_url(coffee), data={"rating": "4"})

    assert response.status_code == 302
    assert response.headers["Location"].startswith(f"/cafes/{coffee.id}")
    assert count_reviews(db_path) == 1
    html = page(client, coffee)
    assert "4 de 5" in html
    assert "Ana" in html
    assert re.search(r"\d{2}/\d{2}/\d{4}", html)
    assert "Ainda não há avaliações" not in html


def test_review_text_is_shown_escaped(client, coffee):  # SCRUM-14
    sign_up(client)

    client.post(
        review_url(coffee), data={"rating": "5", "text": "Achocolatado <b>"}
    )

    html = page(client, coffee)
    assert "Achocolatado &lt;b&gt;" in html


def test_blank_text_is_stored_as_no_text(client, coffee, db_path):
    # SCRUM-14
    sign_up(client)

    client.post(review_url(coffee), data={"rating": "3", "text": "   "})

    connection = connect(db_path)
    row = connection.execute("SELECT rating, text FROM reviews").fetchone()
    connection.close()
    assert (row["rating"], row["text"]) == (3, None)
    assert "3 de 5" in page(client, coffee)


@pytest.mark.parametrize("rating", ["0", "6", "", "abc", "4.5"])
def test_invalid_rating_shows_an_error_in_the_form(
    client, coffee, db_path, rating
):  # SCRUM-14
    sign_up(client)

    response = client.post(
        review_url(coffee), data={"rating": rating, "text": "Meu texto"}
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "A nota deve ser um número inteiro de 1 a 5." in html
    assert "Meu texto" in html
    assert count_reviews(db_path) == 0


def test_missing_rating_field_shows_an_error(client, coffee, db_path):
    # SCRUM-14
    sign_up(client)

    response = client.post(review_url(coffee), data={})

    assert response.status_code == 400
    assert "A nota deve ser" in response.get_data(as_text=True)
    assert count_reviews(db_path) == 0


def test_text_with_1000_characters_is_accepted(client, coffee, db_path):
    # SCRUM-14
    sign_up(client)

    response = client.post(
        review_url(coffee), data={"rating": "4", "text": "a" * 1000}
    )

    assert response.status_code == 302
    assert count_reviews(db_path) == 1


def test_text_with_1001_characters_is_rejected(client, coffee, db_path):
    # SCRUM-14
    sign_up(client)

    response = client.post(
        review_url(coffee), data={"rating": "4", "text": "a" * 1001}
    )

    assert response.status_code == 400
    assert "no máximo 1000 caracteres" in response.get_data(as_text=True)
    assert count_reviews(db_path) == 0


def test_user_with_review_sees_edit_button_instead_of_the_form(
    client, coffee
):  # SCRUM-14
    sign_up(client)
    client.post(review_url(coffee), data={"rating": "4"})

    html = page(client, coffee)

    assert "Editar minha avaliação" in html
    assert 'href="#minha-avaliacao"' in html
    assert 'id="minha-avaliacao"' in html
    assert 'name="rating"' not in html


def test_resubmitting_the_form_shows_an_error_and_keeps_one_review(
    client, coffee, db_path
):  # SCRUM-14
    sign_up(client)
    client.post(review_url(coffee), data={"rating": "4"})

    response = client.post(review_url(coffee), data={"rating": "1"})

    assert response.status_code == 409
    assert "Você já avaliou este café." in response.get_data(as_text=True)
    assert count_reviews(db_path) == 1


def test_review_of_an_unknown_coffee_returns_404(client, db_path):
    # SCRUM-14
    sign_up(client)

    response = client.post("/cafes/999/avaliar", data={"rating": "4"})

    assert response.status_code == 404
    assert "Café não encontrado" in response.get_data(as_text=True)
    assert count_reviews(db_path) == 0


def test_get_of_an_unknown_coffee_review_form_returns_404(client):
    # SCRUM-14
    sign_up(client)

    assert client.get("/cafes/999/avaliar").status_code == 404


def test_visitor_posting_a_review_is_sent_to_login(
    client, coffee, db_path
):  # SCRUM-14
    response = client.post(review_url(coffee), data={"rating": "4"})

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/entrar?next=")
    assert count_reviews(db_path) == 0


def test_visitor_clicking_review_goes_to_login_and_back_with_form_open(
    client, coffee
):  # SCRUM-14
    login_redirect = client.get(review_url(coffee))
    assert login_redirect.status_code == 302
    assert login_redirect.headers["Location"] == (
        f"/entrar?next=/cafes/{coffee.id}/avaliar"
    )
    sign_up(client)  # cria a conta (e entra); depois sai da sessão
    client.post("/sair")

    login = client.post(
        "/entrar",
        data={
            "email": "ana@x.com",
            "password": "abcd1234",
            "next": review_url(coffee),
        },
    )
    assert login.headers["Location"] == review_url(coffee)
    back = client.get(login.headers["Location"])
    assert back.status_code == 302
    target = back.headers["Location"]
    assert target.startswith(f"/cafes/{coffee.id}?avaliar=1")
    assert FORM_OPEN.search(client.get(target).get_data(as_text=True))


def test_signup_path_also_returns_to_the_coffee_with_form_open(
    client, coffee
):  # SCRUM-14
    login_page = client.get(
        f"/entrar?next=/cafes/{coffee.id}/avaliar"
    ).get_data(as_text=True)
    assert "/cadastro?next=" in login_page

    signup = client.post(
        "/cadastro",
        data={
            "display_name": "Bia",
            "email": "bia@x.com",
            "password": "abcd1234",
            "next": review_url(coffee),
        },
    )

    assert signup.headers["Location"] == review_url(coffee)
    back = client.get(signup.headers["Location"])
    html = client.get(back.headers["Location"]).get_data(as_text=True)
    assert FORM_OPEN.search(html)


def test_form_is_closed_without_the_marker(client, coffee):  # SCRUM-14
    sign_up(client)

    assert not FORM_OPEN.search(page(client, coffee))


def test_logged_user_clicking_review_gets_the_form_open(client, coffee):
    # SCRUM-14
    sign_up(client)

    response = client.get(review_url(coffee))

    assert response.status_code == 302
    assert response.headers["Location"].startswith(
        f"/cafes/{coffee.id}?avaliar=1"
    )


def test_user_who_already_reviewed_clicking_review_goes_to_the_review(
    client, coffee
):  # SCRUM-14
    sign_up(client)
    client.post(review_url(coffee), data={"rating": "4"})

    response = client.get(review_url(coffee))

    assert response.status_code == 302
    assert response.headers["Location"].endswith("#minha-avaliacao")


def test_reviews_are_listed_newest_first_with_own_review_on_top(
    client, coffee
):  # SCRUM-14
    for name, email, rating in [
        ("Bia", "bia@x.com", "2"),
        ("Caio", "caio@x.com", "5"),
        ("Ana", "ana@x.com", "4"),
    ]:
        sign_up(client, name=name, email=email)
        client.post(review_url(coffee), data={"rating": rating})
        client.post("/sair")
    client.post("/entrar", data={"email": "bia@x.com", "password": "abcd1234"})

    html = page(client, coffee)

    authors = re.findall(r'class="review-author">([^<]+)<', html)
    assert authors == ["Bia", "Ana", "Caio"]
    assert "review-own" in html
    assert "ana@x.com" not in html
    assert "bia@x.com" not in html
    assert "caio@x.com" not in html


def test_author_email_never_appears_for_visitors(client, coffee):
    # SCRUM-12
    sign_up(client)
    client.post(review_url(coffee), data={"rating": "4"})
    client.post("/sair")

    html = page(client, coffee)

    assert "Ana" in html
    assert "ana@x.com" not in html
