"""Rotas de cadastro e logout, com Flask e SQLite temporário."""

import pytest

from app.main import create_app
from infra.db.database import connect, init_schema


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "auth.db"
    connection = connect(path)
    init_schema(connection)
    connection.close()
    return path


@pytest.fixture
def client(db_path):
    app = create_app({"DATABASE": str(db_path), "SECRET_KEY": "test"})
    return app.test_client()


def sign_up(client, **overrides):
    form = {
        "display_name": "Ana",
        "email": "ana@x.com",
        "password": "abcd1234",
    }
    form.update(overrides)
    return client.post("/cadastro", data=form)


def count_users(db_path):
    connection = connect(db_path)
    try:
        return connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        connection.close()


def test_signup_form_is_shown_to_visitors(client):  # SCRUM-11
    response = client.get("/cadastro")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'name="display_name"' in html
    assert 'name="email"' in html
    assert 'type="password"' in html


def test_visitor_header_has_no_user_name_or_logout(client):  # SCRUM-11
    html = client.get("/").get_data(as_text=True)

    assert "Sair" not in html
    assert 'href="/cadastro"' in html


def test_valid_signup_logs_the_user_in(client):  # SCRUM-11
    response = sign_up(client, display_name="  Ana  ")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    html = client.get("/").get_data(as_text=True)
    assert "Ana" in html
    assert "Sair" in html
    assert 'href="/cadastro"' not in html


def test_session_holds_only_the_user_id(client):  # SCRUM-11
    sign_up(client)

    with client.session_transaction() as session:
        assert dict(session) == {"user_id": 1}


def test_email_is_not_shown_on_public_pages(client):  # SCRUM-11
    sign_up(client)

    html = client.get("/").get_data(as_text=True)

    assert "ana@x.com" not in html


def test_duplicate_email_shows_message_with_login_link(
    client, db_path
):  # SCRUM-11
    sign_up(client)
    other = create_app({"DATABASE": str(db_path), "SECRET_KEY": "test"})

    response = sign_up(other.test_client(), email=" Ana@X.com ")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "e-mail já está cadastrado" in html
    assert 'href="/entrar"' in html
    assert count_users(db_path) == 1


@pytest.mark.parametrize("password", ["abc1234", "abcdefgh", "12345678"])
def test_weak_passwords_show_the_rule(client, db_path, password):
    response = sign_up(client, password=password)  # SCRUM-11

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "pelo menos 8 caracteres" in html
    assert count_users(db_path) == 0


def test_strong_password_is_accepted(client, db_path):  # SCRUM-11
    assert sign_up(client, password="abcd1234").status_code == 302
    assert count_users(db_path) == 1


@pytest.mark.parametrize("name", ["A", " A ", "a" * 41])
def test_display_name_out_of_range_shows_message(client, db_path, name):
    response = sign_up(client, display_name=name)  # SCRUM-11

    assert "nome de exibição" in response.get_data(as_text=True)
    assert count_users(db_path) == 0


def test_two_users_can_share_a_display_name(client, db_path):  # SCRUM-11
    sign_up(client, email="a@x.com")
    other = create_app({"DATABASE": str(db_path), "SECRET_KEY": "test"})

    response = sign_up(other.test_client(), email="b@x.com")

    assert response.status_code == 302
    assert count_users(db_path) == 2


def test_database_never_stores_the_plain_password(client, db_path):
    sign_up(client)  # SCRUM-11

    connection = connect(db_path)
    row = connection.execute("SELECT password_hash FROM users").fetchone()
    connection.close()
    assert row["password_hash"] != "abcd1234"
    assert "abcd1234" not in row["password_hash"]


def test_form_keeps_name_and_email_but_never_the_password(client):
    response = sign_up(client, display_name="Bia", password="curta")
    # SCRUM-11
    html = response.get_data(as_text=True)
    assert 'value="Bia"' in html
    assert 'value="ana@x.com"' in html
    assert "curta" not in html


def test_logout_clears_the_session_and_goes_home(client):  # SCRUM-11
    sign_up(client)

    response = client.post("/sair")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    with client.session_transaction() as session:
        assert "user_id" not in session
    assert "Sair" not in client.get("/").get_data(as_text=True)


def test_stale_session_of_a_missing_user_is_ignored(client):  # SCRUM-11
    with client.session_transaction() as session:
        session["user_id"] = 999

    response = client.get("/")

    assert response.status_code == 200
    assert "Sair" not in response.get_data(as_text=True)
