import pytest
from src.calculator import Calculator

def test_add_positive_numbers():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_add_negative_numbers():
    calc = Calculator()
    assert calc.add(-1, -1) == -2

def test_add_mixed_numbers():
    calc = Calculator()
    assert calc.add(-1, 5) == 4

def test_add_floats():
    calc = Calculator()
    assert calc.add(1.5, 2.5) == 4.0

def test_divide_positive_numbers():
    calc = Calculator()
    assert calc.divide(6, 3) == 2

def test_divide_by_zero(capsys):
    calc = Calculator()
    result = calc.divide(10, 0)
    assert result is None
    captured = capsys.readouterr()
    assert "Cannot divide by zero\n" == captured.out

def test_divide_float_result():
    calc = Calculator()
    assert calc.divide(5, 2) == 2.5

def test_divide_negative_numbers():
    calc = Calculator()
    assert calc.divide(-10, 2) == -5
    assert calc.divide(10, -2) == -5
    assert calc.divide(-10, -2) == 5
