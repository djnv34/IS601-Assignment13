from app.operations import add, subtract, multiply, divide


class CalculationFactory:
    @staticmethod
    def compute(a: float, b: float, calculation_type: str) -> float:
        if calculation_type == "Add":
            return add(a, b)
        if calculation_type == "Sub":
            return subtract(a, b)
        if calculation_type == "Multiply":
            return multiply(a, b)
        if calculation_type == "Divide":
            return divide(a, b)
        raise ValueError("Invalid calculation type.")