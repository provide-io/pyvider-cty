import pytest
from pyvider.cty.functions.numeric_functions import (
    add,
    subtract,
    multiply,
    divide,
    modulo,
    negate,
    log_fn,
    pow_fn,
    parseint_fn,
)
from pyvider.cty.values import CtyValue
from pyvider.cty.types import CtyString, CtyNumber
from pyvider.cty.exceptions import CtyFunctionError

def test_add_with_null_and_unknown():
    assert add(CtyValue.null(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert add(CtyNumber().validate(1), CtyValue.null(CtyNumber())).is_unknown
    assert add(CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert add(CtyNumber().validate(1), CtyValue.unknown(CtyNumber())).is_unknown

def test_subtract_with_null_and_unknown():
    assert subtract(CtyValue.null(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert subtract(CtyNumber().validate(1), CtyValue.null(CtyNumber())).is_unknown
    assert subtract(CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert subtract(CtyNumber().validate(1), CtyValue.unknown(CtyNumber())).is_unknown

def test_multiply_with_null_and_unknown():
    assert multiply(CtyValue.null(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert multiply(CtyNumber().validate(1), CtyValue.null(CtyNumber())).is_unknown
    assert multiply(CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert multiply(CtyNumber().validate(1), CtyValue.unknown(CtyNumber())).is_unknown

def test_divide_with_null_and_unknown():
    assert divide(CtyValue.null(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert divide(CtyNumber().validate(1), CtyValue.null(CtyNumber())).is_unknown
    assert divide(CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert divide(CtyNumber().validate(1), CtyValue.unknown(CtyNumber())).is_unknown

def test_modulo_with_null_and_unknown():
    assert modulo(CtyValue.null(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert modulo(CtyNumber().validate(1), CtyValue.null(CtyNumber())).is_unknown
    assert modulo(CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert modulo(CtyNumber().validate(1), CtyValue.unknown(CtyNumber())).is_unknown

def test_negate_with_null_and_unknown():
    assert negate(CtyValue.null(CtyNumber())).is_unknown
    assert negate(CtyValue.unknown(CtyNumber())).is_unknown

def test_log_fn_with_invalid_values():
    with pytest.raises(CtyFunctionError, match="log: number must be positive"):
        log_fn(CtyNumber().validate(0), CtyNumber().validate(10))
    with pytest.raises(CtyFunctionError, match="log: base must be positive"):
        log_fn(CtyNumber().validate(10), CtyNumber().validate(0))
    with pytest.raises(CtyFunctionError, match="log: base cannot be 1"):
        log_fn(CtyNumber().validate(10), CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError, match="log: math domain error"):
        log_fn(CtyNumber().validate(-1), CtyNumber().validate(10))

def test_pow_fn_with_invalid_values():
    with pytest.raises(CtyFunctionError, match="pow: invalid operation"):
        pow_fn(CtyNumber().validate(-1), CtyNumber().validate(0.5))

def test_parseint_fn_with_invalid_string():
    with pytest.raises(CtyFunctionError, match="parseint: invalid input string for parsing"):
        parseint_fn(CtyString().validate(None), CtyNumber().validate(10))
