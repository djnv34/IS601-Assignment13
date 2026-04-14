import pytest
from pydantic import ValidationError
from app.schemas import CalculationCreate


def test_calculation_create_valid():
    calc = CalculationCreate(a=10, b=5, type="Add")
    assert calc.a == 10
    assert calc.b == 5
    assert calc.type == "Add"


def test_calculation_invalid_type():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=5, type="BadType")


def test_divide_by_zero():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=0, type="Divide")