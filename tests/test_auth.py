import pytest

from presence import auth


def test_password_hash_is_salted_and_verifiable():
    first, second = auth.hash_password("correct horse"), auth.hash_password("correct horse")
    assert first != second
    assert auth.verify_password("correct horse", first)
    assert not auth.verify_password("wrong", first)


def test_verify_rejects_malformed_hash():
    assert not auth.verify_password("x", "5e884898da28047151d0e56f8dc6292773603d0d")


def test_create_and_authenticate():
    auth.create_user("alice", "password123", role="admin")
    user = auth.authenticate("alice", "password123")
    assert user == auth.User("alice", "admin")
    assert user.is_admin
    assert auth.authenticate("alice", "nope") is None
    assert auth.authenticate("bob", "password123") is None


def test_duplicate_username_rejected():
    auth.create_user("alice", "password123")
    with pytest.raises(ValueError, match="already exists"):
        auth.create_user("alice", "password456")


@pytest.mark.parametrize("username,password", [("a", "password123"), ("alice", "short"),
                                               ("bad name", "password123")])
def test_invalid_accounts_rejected(username, password):
    with pytest.raises(ValueError):
        auth.create_user(username, password)


def test_no_default_accounts():
    assert not auth.has_any_user()
