from decimal import Decimal

import pytest

from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions.numeric_functions import (
    abs_fn,
    add,
    ceil_fn,
    divide,
    floor_fn,
    log_fn,
    modulo,
    multiply,
    negate,
    parseint_fn,
    pow_fn,
    signum_fn,
    subtract,
)


def test_add_numbers() -> None:
    assert add(CtyNumber().validate(1), CtyNumber().validate(2)).value == 3
    assert add(CtyNumber().validate(-1), CtyNumber().validate(2)).value == 1
    assert add(CtyNumber().validate(1.5), CtyNumber().validate(2.5)).value == 4.0


def test_add_null() -> None:
    assert add(CtyValue.null(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert add(CtyNumber().validate(1), CtyValue.null(CtyNumber())).is_unknown


def test_add_unknown() -> None:
    assert add(CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
    assert add(CtyNumber().validate(1), CtyValue.unknown(CtyNumber())).is_unknown


def test_add_type_error() -> None:
    with pytest.raises(CtyFunctionError):
        add(CtyString().validate("a"), CtyNumber().validate(1))


def test_subtract_numbers() -> None:
    assert subtract(CtyNumber().validate(3), CtyNumber().validate(2)).value == 1
    assert subtract(CtyNumber().validate(-1), CtyNumber().validate(2)).value == -3
    assert subtract(CtyNumber().validate(2.5), CtyNumber().validate(1.5)).value == 1.0


def test_multiply_numbers() -> None:
    assert multiply(CtyNumber().validate(3), CtyNumber().validate(2)).value == 6
    assert multiply(CtyNumber().validate(-1), CtyNumber().validate(2)).value == -2
    assert multiply(CtyNumber().validate(1.5), CtyNumber().validate(2)).value == 3.0


def test_divide_numbers() -> None:
    assert divide(CtyNumber().validate(6), CtyNumber().validate(2)).value == 3
    assert divide(CtyNumber().validate(-4), CtyNumber().validate(2)).value == -2
    assert divide(CtyNumber().validate(5), CtyNumber().validate(2)).value == 2.5


def test_divide_by_zero() -> None:
    with pytest.raises(CtyFunctionError, match="divide by zero"):
        divide(CtyNumber().validate(1), CtyNumber().validate(0))


def test_modulo_numbers() -> None:
    assert modulo(CtyNumber().validate(5), CtyNumber().validate(2)).value == 1
    assert modulo(CtyNumber().validate(-5), CtyNumber().validate(2)).value == -1
    assert modulo(CtyNumber().validate(5.5), CtyNumber().validate(2)).value == 1.5


def test_modulo_by_zero() -> None:
    with pytest.raises(CtyFunctionError, match="modulo by zero"):
        modulo(CtyNumber().validate(1), CtyNumber().validate(0))


def test_negate_number() -> None:
    assert negate(CtyNumber().validate(5)).value == -5
    assert negate(CtyNumber().validate(-5)).value == 5
    assert negate(CtyNumber().validate(0)).value == 0


def test_abs_fn() -> None:
    assert abs_fn(CtyNumber().validate(5)).value == 5
    assert abs_fn(CtyNumber().validate(-5)).value == 5
    assert abs_fn(CtyNumber().validate(0)).value == 0
    assert abs_fn(CtyNumber().validate(-5.5)).value == 5.5


def test_abs_fn_null_unknown() -> None:
    assert abs_fn(CtyValue.null(CtyNumber())).is_null
    assert abs_fn(CtyValue.unknown(CtyNumber())).is_unknown


def test_abs_fn_invalid_type() -> None:
    with pytest.raises(CtyFunctionError):
        abs_fn(CtyString().validate("not a number"))


def test_ceil_fn() -> None:
    assert ceil_fn(CtyNumber().validate(5.1)).value == Decimal("6")
    assert ceil_fn(CtyNumber().validate(5.9)).value == Decimal("6")
    assert ceil_fn(CtyNumber().validate(5.0)).value == Decimal("5")
    assert ceil_fn(CtyNumber().validate(-5.1)).value == Decimal("-5")


def test_ceil_fn_null_unknown() -> None:
    assert ceil_fn(CtyValue.null(CtyNumber())).is_null
    assert ceil_fn(CtyValue.unknown(CtyNumber())).is_unknown


def test_ceil_fn_invalid_type() -> None:
    with pytest.raises(CtyFunctionError):
        ceil_fn(CtyString().validate("not a number"))


def test_floor_fn() -> None:
    assert floor_fn(CtyNumber().validate(5.1)).value == Decimal("5")
    assert floor_fn(CtyNumber().validate(5.9)).value == Decimal("5")
    assert floor_fn(CtyNumber().validate(5.0)).value == Decimal("5")
    assert floor_fn(CtyNumber().validate(-5.1)).value == Decimal("-6")


def test_floor_fn_null_unknown() -> None:
    assert floor_fn(CtyValue.null(CtyNumber())).is_null
    assert floor_fn(CtyValue.unknown(CtyNumber())).is_unknown


def test_floor_fn_invalid_type() -> None:
    with pytest.raises(CtyFunctionError):
        floor_fn(CtyString().validate("not a number"))


def test_log_fn() -> None:
    assert log_fn(CtyNumber().validate(100), CtyNumber().validate(10)).value == Decimal(
        "2"
    )
    assert log_fn(CtyNumber().validate(8), CtyNumber().validate(2)).value == Decimal(
        "3"
    )


def test_log_fn_null_unknown() -> None:
    assert log_fn(CtyValue.null(CtyNumber()), CtyNumber().validate(10)).is_unknown
    assert log_fn(CtyNumber().validate(100), CtyValue.null(CtyNumber())).is_unknown
    assert log_fn(CtyValue.unknown(CtyNumber()), CtyNumber().validate(10)).is_unknown
    assert log_fn(CtyNumber().validate(100), CtyValue.unknown(CtyNumber())).is_unknown


def test_log_fn_invalid_type() -> None:
    with pytest.raises(CtyFunctionError):
        log_fn(CtyString().validate("a"), CtyNumber().validate(10))
    with pytest.raises(CtyFunctionError):
        log_fn(CtyNumber().validate(100), CtyString().validate("b"))


def test_log_fn_invalid_values() -> None:
    with pytest.raises(CtyFunctionError):
        log_fn(CtyNumber().validate(-1), CtyNumber().validate(10))
    with pytest.raises(CtyFunctionError):
        log_fn(CtyNumber().validate(100), CtyNumber().validate(-1))
    with pytest.raises(CtyFunctionError):
        log_fn(CtyNumber().validate(100), CtyNumber().validate(1))


def test_pow_fn() -> None:
    assert pow_fn(CtyNumber().validate(2), CtyNumber().validate(3)).value == 8
    assert pow_fn(CtyNumber().validate(4), CtyNumber().validate(0.5)).value == 2


def test_pow_fn_null_unknown() -> None:
    assert pow_fn(CtyValue.null(CtyNumber()), CtyNumber().validate(2)).is_unknown
    assert pow_fn(CtyNumber().validate(2), CtyValue.null(CtyNumber())).is_unknown
    assert pow_fn(CtyValue.unknown(CtyNumber()), CtyNumber().validate(2)).is_unknown
    assert pow_fn(CtyNumber().validate(2), CtyValue.unknown(CtyNumber())).is_unknown


def test_pow_fn_invalid_type() -> None:
    with pytest.raises(CtyFunctionError):
        pow_fn(CtyString().validate("a"), CtyNumber().validate(2))
    with pytest.raises(CtyFunctionError):
        pow_fn(CtyNumber().validate(2), CtyString().validate("b"))


def test_signum_fn() -> None:
    assert signum_fn(CtyNumber().validate(10)).value == 1
    assert signum_fn(CtyNumber().validate(-10)).value == -1
    assert signum_fn(CtyNumber().validate(0)).value == 0


def test_signum_fn_null_unknown() -> None:
    assert signum_fn(CtyValue.null(CtyNumber())).is_null
    assert signum_fn(CtyValue.unknown(CtyNumber())).is_unknown


def test_signum_fn_invalid_type() -> None:
    with pytest.raises(CtyFunctionError):
        signum_fn(CtyString().validate("a"))


def test_parseint_fn() -> None:
    assert parseint_fn(CtyString().validate("10"), CtyNumber().validate(10)).value == 10
    assert (
        parseint_fn(CtyString().validate("FF"), CtyNumber().validate(16)).value == 255
    )
    assert (
        parseint_fn(CtyString().validate("0xFF"), CtyNumber().validate(0)).value == 255
    )


def test_parseint_fn_null_result() -> None:
    assert parseint_fn(CtyString().validate("z"), CtyNumber().validate(10)).is_null


def test_parseint_fn_null_unknown() -> None:
    assert parseint_fn(CtyValue.null(CtyString()), CtyNumber().validate(10)).is_null
    assert parseint_fn(CtyString().validate("10"), CtyValue.null(CtyNumber())).is_null
    assert parseint_fn(
        CtyValue.unknown(CtyString()), CtyNumber().validate(10)
    ).is_unknown
    assert parseint_fn(
        CtyString().validate("10"), CtyValue.unknown(CtyNumber())
    ).is_unknown


def test_parseint_fn_invalid_type() -> None:
    with pytest.raises(CtyFunctionError):
        parseint_fn(CtyNumber().validate(10), CtyNumber().validate(10))
    with pytest.raises(CtyFunctionError):
        parseint_fn(CtyString().validate("10"), CtyString().validate("10"))


def test_parseint_fn_invalid_base() -> None:
    with pytest.raises(CtyFunctionError):
        parseint_fn(CtyString().validate("10"), CtyNumber().validate(1))
    with pytest.raises(CtyFunctionError):
        parseint_fn(CtyString().validate("10"), CtyNumber().validate(37))
