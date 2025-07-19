import pytest
from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.functions.numeric_functions import add, subtract, multiply, divide, modulo, negate
from pyvider.cty.exceptions import CtyFunctionError

def test_add_numbers():
    assert add(CtyNumber().validate(1), CtyNumber().validate(2)).value == 3
    assert add(CtyNumber().validate(-1), CtyNumber().validate(2)).value == 1
    assert add(CtyNumber().validate(1.5), CtyNumber().validate(2.5)).value == 4.0

def test_add_null():
    assert add(CtyValue.null(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert add(CtyNumber().validate(1), CtyValue.null(CtyNumber())).is_unknown

def test_add_unknown():
    assert add(CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert add(CtyNumber().validate(1), CtyValue.unknown(CtyNumber())).is_unknown

def test_add_type_error():
    with pytest.raises(CtyFunctionError):
        add(CtyString().validate("a"), CtyNumber().validate(1))

def test_subtract_numbers():
    assert subtract(CtyNumber().validate(3), CtyNumber().validate(2)).value == 1
    assert subtract(CtyNumber().validate(-1), CtyNumber().validate(2)).value == -3
    assert subtract(CtyNumber().validate(2.5), CtyNumber().validate(1.5)).value == 1.0

def test_multiply_numbers():
    assert multiply(CtyNumber().validate(3), CtyNumber().validate(2)).value == 6
    assert multiply(CtyNumber().validate(-1), CtyNumber().validate(2)).value == -2
    assert multiply(CtyNumber().validate(1.5), CtyNumber().validate(2)).value == 3.0

def test_divide_numbers():
    assert divide(CtyNumber().validate(6), CtyNumber().validate(2)).value == 3
    assert divide(CtyNumber().validate(-4), CtyNumber().validate(2)).value == -2
    assert divide(CtyNumber().validate(5), CtyNumber().validate(2)).value == 2.5

def test_divide_by_zero():
    with pytest.raises(CtyFunctionError, match="divide by zero"):
        divide(CtyNumber().validate(1), CtyNumber().validate(0))

def test_modulo_numbers():
    assert modulo(CtyNumber().validate(5), CtyNumber().validate(2)).value == 1
    assert modulo(CtyNumber().validate(-5), CtyNumber().validate(2)).value == -1
    assert modulo(CtyNumber().validate(5.5), CtyNumber().validate(2)).value == 1.5

def test_modulo_by_zero():
    with pytest.raises(CtyFunctionError, match="modulo by zero"):
        modulo(CtyNumber().validate(1), CtyNumber().validate(0))

def test_negate_number():
    assert negate(CtyNumber().validate(5)).value == -5
    assert negate(CtyNumber().validate(-5)).value == 5
    assert negate(CtyNumber().validate(0)).value == 0
