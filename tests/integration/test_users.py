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
        connection.execute(text("TRUNCATE TABLE calculations RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        connection.commit()


def teardown_module():
    with engine.connect() as connection:
        connection.execute(text("TRUNCATE TABLE calculations RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        connection.commit()


def test_register_user():
    response = client.post("/users/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"


def test_login_user():
    response = client.post("/users/login", json={
        "username": "alice",
        "password": "secret123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"


def test_login_invalid_password():
    response = client.post("/users/login", json={
        "username": "alice",
        "password": "wrongpassword"
    })
    assert response.status_code == 400
    assert response.json()["error"] == "Invalid username or password"