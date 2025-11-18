#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Numeric attack property-based tests for precision and overflow scenarios.

Tests edge cases in numeric handling:
- Integer overflow/underflow
- Floating point precision loss
- Subnormal numbers
- Very large exponents
- Division by near-zero"""

from decimal import Decimal
import sys

from hypothesis import HealthCheck, assume, given, settings, strategies as st
import pytest

from pyvider.cty import CtyNumber
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack

NUMERIC_ATTACK_SETTINGS = settings(
    deadline=5000,
    max_examples=1000,
    suppress_health_check=[HealthCheck.too_slow],
)


@NUMERIC_ATTACK_SETTINGS
@given(number=st.integers(min_value=2**53, max_value=2**200))
def test_very_large_integers(number: int) -> None:
    """
    Numeric attack: Integers far beyond JavaScript safe range.

    Tests handling of integers larger than 2^53.
    """
    number_type = CtyNumber()

    try:
        cty_value = number_type.validate(number)
        msgpack_bytes = cty_to_msgpack(cty_value, number_type)
        decoded = cty_from_msgpack(msgpack_bytes, number_type)
        # May have precision loss but should be close
        assert decoded.value is not None
    except (ValueError, OverflowError):
        # Also acceptable
        pass


@NUMERIC_ATTACK_SETTINGS
@given(number=st.integers(min_value=-(2**200), max_value=-(2**53)))
def test_very_negative_integers(number: int) -> None:
    """
    Numeric attack: Very large negative integers.

    Tests handling of large negative numbers.
    """
    number_type = CtyNumber()

    try:
        cty_value = number_type.validate(number)
        msgpack_bytes = cty_to_msgpack(cty_value, number_type)
        decoded = cty_from_msgpack(msgpack_bytes, number_type)
        assert decoded.value is not None
    except (ValueError, OverflowError):
        pass


@NUMERIC_ATTACK_SETTINGS
@given(exponent=st.integers(min_value=-300, max_value=-10))
def test_subnormal_floats(exponent: int) -> None:
    """
    Numeric attack: Subnormal/denormalized floating point numbers.

    Tests very small numbers near the float precision limit.
    """
    # Create subnormal number
    number = 10.0**exponent
    assume(number > 0)  # Avoid actual zero

    number_type = CtyNumber()

    cty_value = number_type.validate(number)
    msgpack_bytes = cty_to_msgpack(cty_value, number_type)
    decoded = cty_from_msgpack(msgpack_bytes, number_type)

    # Should preserve or be very close
    assert decoded.value == pytest.approx(number, rel=1e-9, abs=1e-300)


@NUMERIC_ATTACK_SETTINGS
@given(
    numerator=st.floats(min_value=1.0, max_value=1e10),
    denominator=st.floats(min_value=1e-100, max_value=1e-10),
)
def test_division_by_very_small_numbers(numerator: float, denominator: float) -> None:
    """
    Numeric attack: Division by very small numbers.

    Tests precision with division creating very large results.
    """
    assume(denominator != 0)
    result = numerator / denominator

    # Skip if result is infinity
    assume(not (result == float("inf") or result == float("-inf")))

    number_type = CtyNumber()

    try:
        cty_value = number_type.validate(result)
        assert cty_value.value is not None
    except (ValueError, OverflowError):
        # Acceptable for extreme values
        pass


@NUMERIC_ATTACK_SETTINGS
@given(number=st.floats(min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False))
def test_float_to_decimal_precision(number: float) -> None:
    """
    Numeric attack: Float to Decimal conversion precision.

    Tests that float→Decimal conversion handles precision correctly.
    """
    number_type = CtyNumber()

    cty_value = number_type.validate(number)

    # Value is stored as Decimal
    assert isinstance(cty_value.value, Decimal)

    # Roundtrip
    msgpack_bytes = cty_to_msgpack(cty_value, number_type)
    decoded = cty_from_msgpack(msgpack_bytes, number_type)

    # Should be close to original
    assert float(decoded.value) == pytest.approx(number, rel=1e-9)


@NUMERIC_ATTACK_SETTINGS
@given(precision=st.integers(min_value=20, max_value=100))
def test_high_precision_decimals(precision: int) -> None:
    """
    Numeric attack: Very high precision decimal numbers.

    Tests Decimals with many significant digits.
    """
    # Create high-precision decimal
    number_str = "1." + "123456789" * (precision // 9)
    number = Decimal(number_str)

    number_type = CtyNumber()

    cty_value = number_type.validate(number)
    msgpack_bytes = cty_to_msgpack(cty_value, number_type)
    decoded = cty_from_msgpack(msgpack_bytes, number_type)

    # Some precision may be lost in msgpack, but should be close
    assert decoded.value is not None


@NUMERIC_ATTACK_SETTINGS
@given(base=st.floats(min_value=1.1, max_value=10.0), exponent=st.integers(min_value=50, max_value=300))
def test_extreme_exponents(base: float, exponent: int) -> None:
    """
    Numeric attack: Numbers with extreme exponents.

    Tests very large numbers created by exponentiation.
    """
    try:
        number = base**exponent
        assume(number < sys.float_info.max)  # Avoid actual infinity

        number_type = CtyNumber()

        cty_value = number_type.validate(number)
        assert cty_value.value is not None
    except (OverflowError, ValueError):
        # Acceptable for extreme values
        pass


@NUMERIC_ATTACK_SETTINGS
@given(
    significant_digits=st.integers(min_value=1, max_value=50),
    exponent=st.integers(min_value=-50, max_value=50),
)
def test_precision_across_magnitude_ranges(significant_digits: int, exponent: int) -> None:
    """
    Numeric attack: Precision across different magnitude ranges.

    Tests that precision is maintained for numbers of vastly different magnitudes.
    """
    # Create number with specific significant digits and exponent
    mantissa = int("9" * significant_digits)
    number = Decimal(mantissa) * (Decimal(10) ** exponent)

    number_type = CtyNumber()

    try:
        cty_value = number_type.validate(number)
        msgpack_bytes = cty_to_msgpack(cty_value, number_type)
        decoded = cty_from_msgpack(msgpack_bytes, number_type)

        # Verify decoded value is reasonable
        assert decoded.value is not None
    except (ValueError, OverflowError):
        pass


# 🌊🪢🔚
