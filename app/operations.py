import logging

logger = logging.getLogger(__name__)


def add(a: float, b: float) -> float:
    result = a + b
    logger.info(f"Add operation: {a} + {b} = {result}")
    return result


def subtract(a: float, b: float) -> float:
    result = a - b
    logger.info(f"Subtract operation: {a} - {b} = {result}")
    return result


def multiply(a: float, b: float) -> float:
    result = a * b
    logger.info(f"Multiply operation: {a} * {b} = {result}")
    return result


def divide(a: float, b: float) -> float:
    if b == 0:
        logger.error(f"Divide operation failed: attempted {a} / {b}")
        raise ValueError("Cannot divide by zero!")
    result = a / b
    logger.info(f"Divide operation: {a} / {b} = {result}")
    return result