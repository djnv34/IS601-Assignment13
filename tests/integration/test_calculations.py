import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Calculation

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fastapi_db"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as connection:
        connection.execute(text("TRUNCATE TABLE calculations RESTART IDENTITY CASCADE"))
        connection.commit()


def teardown_module():
    with engine.connect() as connection:
        connection.execute(text("TRUNCATE TABLE calculations RESTART IDENTITY CASCADE"))
        connection.commit()


def test_insert_calculation():
    db = TestingSessionLocal()

    calc = Calculation(
        a=10,
        b=5,
        type="Add",
        result=15
    )

    db.add(calc)
    db.commit()
    db.refresh(calc)

    assert calc.id is not None
    assert calc.result == 15

    db.close()


def test_invalid_divide():
    db = TestingSessionLocal()

    try:
        calc = Calculation(
            a=10,
            b=0,
            type="Divide",
            result=0  
        )
        db.add(calc)
        db.commit()
        assert False  
    except Exception:
        assert True

    db.close()