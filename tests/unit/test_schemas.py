import pytest
from pydantic import ValidationError
from app.schemas import UserCreate


def test_user_create_valid():
    user = UserCreate(username="dariel", email="dariel@example.com", password="secret123")
    assert user.username == "dariel"
    assert user.email == "dariel@example.com"


def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(username="dariel", email="not-an-email", password="secret123")