import pytest
from app.factory import CalculationFactory


def test_factory_add():
    assert CalculationFactory.compute(2, 3, "Add") == 5


def test_factory_sub():
    assert CalculationFactory.compute(5, 3, "Sub") == 2


def test_factory_multiply():
    assert CalculationFactory.compute(4, 5, "Multiply") == 20


def test_factory_divide():
    assert CalculationFactory.compute(10, 2, "Divide") == 5


def test_factory_invalid_type():
    with pytest.raises(ValueError, match="Invalid calculation type."):
        CalculationFactory.compute(1, 2, "BadType")