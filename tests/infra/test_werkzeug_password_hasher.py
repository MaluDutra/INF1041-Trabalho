"""O hasher com werkzeug cumpre o contrato do port (SCRUM-11)."""

from infra.security.werkzeug_password_hasher import WerkzeugPasswordHasher


def test_hash_is_not_the_plain_password():  # SCRUM-11
    password_hash = WerkzeugPasswordHasher().hash("abcd1234")

    assert "abcd1234" not in password_hash


def test_verify_accepts_the_right_password_only():  # SCRUM-11
    hasher = WerkzeugPasswordHasher()
    password_hash = hasher.hash("abcd1234")

    assert hasher.verify("abcd1234", password_hash)
    assert not hasher.verify("abcd12345", password_hash)
