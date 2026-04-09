import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from main import app
from app.database import Base, get_db

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fastapi_db"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_module():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as connection:
        connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        connection.commit()


def teardown_module():
    with engine.connect() as connection:
        connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        connection.commit()


def test_create_user():
    response = client.post("/users", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "password_hash" not in data


def test_duplicate_username():
    response = client.post("/users", json={
        "username": "alice",
        "email": "alice2@example.com",
        "password": "secret123"
    })
    assert response.status_code == 400
    assert response.json()["error"] == "Username already exists"


def test_duplicate_email():
    response = client.post("/users", json={
        "username": "alice_new",
        "email": "alice@example.com",
        "password": "secret123"
    })
    assert response.status_code == 400
    assert response.json()["error"] == "Email already exists"


def test_invalid_email():
    response = client.post("/users", json={
        "username": "charlie",
        "email": "bad-email",
        "password": "secret123"
    })
    assert response.status_code == 400
    assert "error" in response.json()