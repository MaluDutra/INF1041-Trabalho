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
    assert 'id="minha-avaliacao"' in html
    assert f'action="{review_url(coffee)}"' not in html


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


def sign_in_new_user(client, name, email):
    client.post("/sair")
    sign_up(client, name=name, email=email)


def test_page_without_reviews_shows_no_reviews_and_an_empty_histogram(
    client, coffee
):  # SCRUM-19
    html = page(client, coffee)

    assert "Sem avaliações" in html
    assert "★ ·" not in html
    assert html.count('class="histogram-row"') == 5
    assert html.count(">0%<") == 5


def test_single_review_shows_the_average_with_one_decimal(
    client, coffee
):  # SCRUM-19
    sign_up(client)
    client.post(review_url(coffee), data={"rating": "1"})

    html = page(client, coffee)

    assert "1,0 ★ · 1 avaliação" in html
    assert "1,0 ★ · 1 avaliações" not in html
    assert "Sem avaliações" not in html


def test_aggregate_and_histogram_update_after_a_new_review(
    client, coffee
):  # SCRUM-19
    sign_up(client)
    client.post(review_url(coffee), data={"rating": "5"})
    assert "5,0 ★ · 1 avaliação" in page(client, coffee)

    sign_in_new_user(client, "Bia", "bia@x.com")
    client.post(review_url(coffee), data={"rating": "4"})
    html = page(client, coffee)

    assert "4,5 ★ · 2 avaliações" in html
    assert re.findall(r'class="histogram-label">([^<]+)<', html) == [
        "5★",
        "4★",
        "3★",
        "2★",
        "1★",
    ]
    assert re.findall(r'class="histogram-percentage">([^<]+)<', html) == [
        "50%",
        "50%",
        "0%",
        "0%",
        "0%",
    ]


def test_page_follows_spec_then_rating_then_review_order(
    client, coffee
):  # SCRUM-19
    sign_up(client)
    client.post(review_url(coffee), data={"rating": "4"})

    html = page(client, coffee)

    spec = html.index("Ficha técnica")
    rating = html.index("4,0 ★ · 1 avaliação")
    button = html.index("Editar minha avaliação")
    reviews = html.index("4 de 5")
    assert spec < rating < button < reviews


def test_visitor_sees_the_review_button_before_the_reviews(
    client, coffee
):  # SCRUM-19
    html = page(client, coffee)

    assert (
        html.index("Sem avaliações")
        < html.index(f'href="{review_url(coffee)}"')
        < html.index("Ainda não há avaliações")
    )


EDIT_OPEN = re.compile(r'<details[^>]*id="editar"[^>]*\sopen\b')


def own_review_id(db_path):
    connection = connect(db_path)
    try:
        return connection.execute("SELECT id FROM reviews").fetchone()["id"]
    finally:
        connection.close()


def edit_url(coffee, review_id):
    return f"/cafes/{coffee.id}/avaliacoes/{review_id}/editar"


def delete_url(coffee, review_id):
    return f"/cafes/{coffee.id}/avaliacoes/{review_id}/excluir"


def stored_review(db_path):
    connection = connect(db_path)
    try:
        return connection.execute(
            "SELECT rating, text, created_at, edited FROM reviews"
        ).fetchone()
    finally:
        connection.close()


@pytest.fixture
def reviewed(client, coffee, db_path):
    """Ana logada, com um review de nota 3 e texto "Ok"."""
    sign_up(client, name="Ana")
    client.post(review_url(coffee), data={"rating": "3", "text": "Ok"})
    return own_review_id(db_path)


def test_edit_form_is_prefilled_with_the_current_review(
    client, coffee, reviewed
):  # SCRUM-14
    html = client.get(f"/cafes/{coffee.id}?editar=1").get_data(as_text=True)

    assert EDIT_OPEN.search(html)
    assert f'action="{edit_url(coffee, reviewed)}"' in html
    assert re.search(r'value="3"\s+required\s+checked', html)
    assert re.search(r"<textarea[^>]*>Ok</textarea>", html)


def test_edit_form_is_closed_without_the_marker(client, coffee, reviewed):
    # SCRUM-14
    html = page(client, coffee)

    assert 'id="editar"' in html
    assert not EDIT_OPEN.search(html)


def test_edit_changes_the_review_and_shows_the_edited_badge(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    original = stored_review(db_path)["created_at"]

    response = client.post(
        edit_url(coffee, reviewed), data={"rating": "5", "text": "Novo"}
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("#minha-avaliacao")
    html = page(client, coffee)
    assert "5 de 5" in html
    assert "3 de 5" not in html
    assert "Novo" in html
    assert 'class="review-edited"' in html
    saved = stored_review(db_path)
    assert saved["created_at"] == original
    assert saved["edited"] == 1


def test_review_never_edited_has_no_edited_badge(client, coffee, reviewed):
    # SCRUM-14
    assert 'class="review-edited"' not in page(client, coffee)


def test_edit_keeps_the_original_date_shown(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    before = re.search(r"\d{2}/\d{2}/\d{4}", page(client, coffee)).group()

    client.post(edit_url(coffee, reviewed), data={"rating": "5"})

    after = re.search(r"\d{2}/\d{2}/\d{4}", page(client, coffee)).group()
    assert after == before


@pytest.mark.parametrize("rating", ["0", "6", "", "abc", "4.5"])
def test_edit_with_invalid_rating_shows_the_error_and_keeps_the_review(
    client, coffee, reviewed, db_path, rating
):  # SCRUM-14
    response = client.post(
        edit_url(coffee, reviewed),
        data={"rating": rating, "text": "Meu texto"},
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "A nota deve ser um número inteiro de 1 a 5." in html
    assert EDIT_OPEN.search(html)
    assert "Meu texto" in html
    saved = stored_review(db_path)
    assert (saved["rating"], saved["text"], saved["edited"]) == (3, "Ok", 0)


def test_edit_with_text_over_1000_characters_is_rejected(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    response = client.post(
        edit_url(coffee, reviewed),
        data={"rating": "4", "text": "a" * 1001},
    )

    assert response.status_code == 400
    assert "no máximo 1000 caracteres" in response.get_data(as_text=True)
    assert stored_review(db_path)["text"] == "Ok"


def test_edit_with_blank_text_stores_no_text(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    client.post(
        edit_url(coffee, reviewed), data={"rating": "4", "text": "   "}
    )

    saved = stored_review(db_path)
    assert (saved["rating"], saved["text"]) == (4, None)


def test_editing_a_review_of_someone_else_returns_403(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    client.post("/sair")
    sign_up(client, name="Bia", email="bia@x.com")

    response = client.post(
        edit_url(coffee, reviewed), data={"rating": "1", "text": "Hack"}
    )

    assert response.status_code == 403
    saved = stored_review(db_path)
    assert (saved["rating"], saved["text"], saved["edited"]) == (3, "Ok", 0)


def test_editing_an_unknown_review_returns_404(client, coffee, reviewed):
    # SCRUM-14
    response = client.post(edit_url(coffee, 999), data={"rating": "4"})

    assert response.status_code == 404
    assert "Avaliação não encontrada" in response.get_data(as_text=True)


def test_editing_through_another_coffee_returns_404(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    response = client.post(
        f"/cafes/999/avaliacoes/{reviewed}/editar", data={"rating": "1"}
    )

    assert response.status_code == 404
    assert stored_review(db_path)["rating"] == 3


def test_visitor_posting_an_edit_is_sent_to_login(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    client.post("/sair")

    response = client.post(edit_url(coffee, reviewed), data={"rating": "1"})

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/entrar?next=")
    assert stored_review(db_path)["rating"] == 3


def test_get_of_the_edit_path_leads_back_to_the_open_edit_form(
    client, coffee, reviewed
):  # SCRUM-14
    response = client.get(edit_url(coffee, reviewed))

    assert response.status_code == 302
    assert response.headers["Location"].startswith(
        f"/cafes/{coffee.id}?editar=1"
    )


def test_visitor_get_of_the_edit_path_is_sent_to_login(
    client, coffee, reviewed
):  # SCRUM-14
    client.post("/sair")

    response = client.get(edit_url(coffee, reviewed))

    assert response.headers["Location"] == (
        f"/entrar?next={edit_url(coffee, reviewed)}"
    )


def test_aggregate_is_updated_after_editing_3_to_5(
    client, coffee, db_path
):  # SCRUM-14 / SCRUM-19
    sign_up(client, name="Ana")
    client.post(review_url(coffee), data={"rating": "5"})
    sign_in_new_user(client, "Bia", "bia@x.com")
    client.post(review_url(coffee), data={"rating": "3"})
    assert "4,0 ★ · 2 avaliações" in page(client, coffee)
    connection = connect(db_path)
    review = connection.execute(
        "SELECT id FROM reviews WHERE rating = 3"
    ).fetchone()
    connection.close()

    client.post(edit_url(coffee, review["id"]), data={"rating": "5"})

    html = page(client, coffee)
    assert "5,0 ★ · 2 avaliações" in html
    assert re.findall(r'class="histogram-count">([^<]+)<', html) == [
        "2",
        "0",
        "0",
        "0",
        "0",
    ]


def count_reviews_of(db_path, coffee):
    connection = connect(db_path)
    try:
        return connection.execute(
            "SELECT COUNT(*) FROM reviews WHERE coffee_id = ?", (coffee.id,)
        ).fetchone()[0]
    finally:
        connection.close()


def test_own_review_has_a_delete_confirmation_with_a_post_form(
    client, coffee, reviewed
):  # SCRUM-14
    html = page(client, coffee)

    assert "definitivo" in html
    assert f'action="{delete_url(coffee, reviewed)}"' in html
    assert "Confirmar exclusão" in html


def test_delete_button_is_not_shown_for_other_people_reviews(
    client, coffee, reviewed
):  # SCRUM-14
    client.post("/sair")

    html = page(client, coffee)

    assert "Confirmar exclusão" not in html
    assert delete_url(coffee, reviewed) not in html


def test_confirmed_delete_removes_the_review_and_brings_back_the_button(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    response = client.post(delete_url(coffee, reviewed))

    assert response.status_code == 302
    assert response.headers["Location"] == f"/cafes/{coffee.id}"
    assert count_reviews(db_path) == 0
    html = page(client, coffee)
    assert "Ainda não há avaliações" in html
    assert "Editar minha avaliação" not in html
    assert 'name="rating"' in html
    assert "Sem avaliações" in html


def test_get_of_the_delete_path_never_deletes(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    response = client.get(delete_url(coffee, reviewed))

    assert response.status_code == 302
    assert response.headers["Location"] == f"/cafes/{coffee.id}"
    assert count_reviews(db_path) == 1


def test_visitor_get_of_the_delete_path_is_sent_to_login(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    client.post("/sair")

    response = client.get(delete_url(coffee, reviewed))

    assert response.headers["Location"] == (
        f"/entrar?next={delete_url(coffee, reviewed)}"
    )
    assert count_reviews(db_path) == 1


def test_visitor_posting_a_delete_is_sent_to_login(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    client.post("/sair")

    response = client.post(delete_url(coffee, reviewed))

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/entrar?next=")
    assert count_reviews(db_path) == 1


def test_deleting_a_review_of_someone_else_returns_403(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    client.post("/sair")
    sign_up(client, name="Bia", email="bia@x.com")

    response = client.post(delete_url(coffee, reviewed))

    assert response.status_code == 403
    assert count_reviews(db_path) == 1


def test_deleting_an_unknown_review_returns_404(client, coffee, reviewed):
    # SCRUM-14
    response = client.post(delete_url(coffee, 999))

    assert response.status_code == 404
    assert "Avaliação não encontrada" in response.get_data(as_text=True)


def test_deleting_the_same_review_twice_returns_404(
    client, coffee, reviewed
):  # SCRUM-14
    client.post(delete_url(coffee, reviewed))

    assert client.post(delete_url(coffee, reviewed)).status_code == 404


def test_deleting_through_another_coffee_returns_404(
    client, coffee, reviewed, db_path
):  # SCRUM-14
    response = client.post(f"/cafes/999/avaliacoes/{reviewed}/excluir")

    assert response.status_code == 404
    assert count_reviews(db_path) == 1


def test_aggregate_and_histogram_follow_a_deletion(
    client, coffee, db_path
):  # SCRUM-14 / SCRUM-19
    sign_up(client, name="Ana")
    client.post(review_url(coffee), data={"rating": "5"})
    sign_in_new_user(client, "Bia", "bia@x.com")
    client.post(review_url(coffee), data={"rating": "3"})
    assert "4,0 ★ · 2 avaliações" in page(client, coffee)
    bia_review = own_review_id_for(db_path, rating=3)

    client.post(delete_url(coffee, bia_review))

    html = page(client, coffee)
    assert "5,0 ★ · 1 avaliação" in html
    assert count_reviews_of(db_path, coffee) == 1
    assert re.findall(r'class="histogram-count">([^<]+)<', html) == [
        "1",
        "0",
        "0",
        "0",
        "0",
    ]


def own_review_id_for(db_path, rating):
    connection = connect(db_path)
    try:
        return connection.execute(
            "SELECT id FROM reviews WHERE rating = ?", (rating,)
        ).fetchone()["id"]
    finally:
        connection.close()
