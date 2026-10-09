def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b


def power(a, b):
    return a**b


def modulo(a, b):
    if b == 0:
        raise ValueError("Modulo by zero")
    return a % b
