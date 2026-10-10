import pytest

from calculator import add, divide, modulo, multiply, power, subtract


def test_add():
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(8, 3) == 5


def test_multiply():
    assert multiply(4, 3) == 12


def test_divide():
    assert divide(10, 2) == 5


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)


def test_power():
    assert power(2, 3) == 8


def test_modulo():
    assert modulo(7, 3) == 1


def test_modulo_by_zero():
    with pytest.raises(ValueError):
        modulo(5, 0)
