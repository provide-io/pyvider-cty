#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Property-based tests for special value attack vectors.

Tests edge cases that could cause crashes or unexpected behavior:
- NaN/Infinity arithmetic and comparison operations
- Zero-width and confusable Unicode characters
- RTL override and other Unicode direction attacks"""

from decimal import Decimal, InvalidOperation

from hypothesis import given, settings, strategies as st
import pytest

from pyvider.cty import CtyMap, CtyNumber, CtyObject, CtyString
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack

# Aggressive settings for security testing
SECURITY_SETTINGS = settings(
    deadline=5000,
    max_examples=500,
)


@SECURITY_SETTINGS
@given(operation=st.sampled_from(["lt", "gt", "le", "ge", "eq", "ne"]))
def test_nan_comparisons_dont_crash(operation: str) -> None:  # noqa: C901
    """
    Security test: NaN comparisons should not crash the system.

    NaN values have special comparison semantics that can cause
    InvalidOperation exceptions in Decimal arithmetic.
    """
    num_type = CtyNumber()
    nan_val = num_type.validate(float("nan"))
    normal_val = num_type.validate(42)

    # These should not crash - either return a result or raise a handled exception
    try:
        if operation == "lt":
            result = nan_val.value < normal_val.value
        elif operation == "gt":
            result = nan_val.value > normal_val.value
        elif operation == "le":
            result = nan_val.value <= normal_val.value
        elif operation == "ge":
            result = nan_val.value >= normal_val.value
        elif operation == "eq":
            result = nan_val.value == normal_val.value
        elif operation == "ne":
            result = nan_val.value != normal_val.value

        # If it didn't crash, verify the result makes sense for NaN
        if operation in ["lt", "gt", "le", "ge"]:
            # Comparisons with NaN should be False or raise InvalidOperation
            assert isinstance(result, bool) or result is None
        elif operation == "eq":
            # NaN == anything should be False
            assert result is False
        elif operation == "ne":
            # NaN != anything should be True
            assert result is True

    except InvalidOperation:
        # This is acceptable - Decimal raises InvalidOperation for NaN comparisons
        pass
    except Exception as e:
        # Other exceptions indicate a problem
        pytest.fail(f"Unexpected exception for NaN comparison {operation}: {e}")


@SECURITY_SETTINGS
@given(special_value=st.sampled_from([float("nan"), float("inf"), float("-inf")]))
def test_special_float_serialization_roundtrip(special_value: float) -> None:
    """
    Security test: Special float values should serialize/deserialize safely.

    Tests NaN, Infinity, and -Infinity for safe round-trip behavior.
    """
    num_type = CtyNumber()

    # Validate
    cty_val = num_type.validate(special_value)

    # Serialize
    msgpack_bytes = cty_to_msgpack(cty_val, num_type)
    assert len(msgpack_bytes) > 0

    # Deserialize
    decoded = cty_from_msgpack(msgpack_bytes, num_type)

    # Verify round-trip
    # Note: NaN != NaN by definition, so we handle it specially
    if str(special_value) == "nan":
        assert str(decoded.value) == "NaN"
    else:
        assert decoded.value == cty_val.value


@SECURITY_SETTINGS
@given(
    zero_width_char=st.sampled_from(
        [
            "\u200b",  # Zero-width space
            "\u200c",  # Zero-width non-joiner
            "\u200d",  # Zero-width joiner
            "\ufeff",  # Zero-width no-break space
        ]
    )
)
def test_zero_width_characters_in_keys_are_preserved(zero_width_char: str) -> None:
    """
    Security test: Zero-width characters should be preserved but distinguishable.

    These characters are invisible but change the string, potentially causing
    confusion or bypassing validation. We preserve them but verify they make
    keys distinct.
    """
    map_type = CtyMap(element_type=CtyString())

    # Create keys that look identical but differ by zero-width char
    key1 = "key"
    key2 = f"k{zero_width_char}ey"

    test_map = {key1: "value1", key2: "value2"}

    # Validate
    validated = map_type.validate(test_map)

    # Both keys should be preserved as distinct
    assert len(validated.value) == 2
    assert key1 in validated.value
    assert key2 in validated.value


@SECURITY_SETTINGS
@given(
    direction_char=st.sampled_from(
        [
            "\u202a",  # Left-to-right embedding
            "\u202b",  # Right-to-left embedding
            "\u202c",  # Pop directional formatting
            "\u202d",  # Left-to-right override
            "\u202e",  # Right-to-left override
        ]
    )
)
def test_rtl_override_characters_in_keys_are_preserved(direction_char: str) -> None:
    """
    Security test: RTL override characters should be preserved.

    These can cause visual spoofing (text displays backwards), but we preserve
    them since they're valid Unicode. Consumers should be aware of this risk.
    """
    map_type = CtyMap(element_type=CtyString())

    # Create key with direction character
    sneaky_key = f"public_{direction_char}etavirp"

    test_map = {sneaky_key: "value"}

    # Validate
    validated = map_type.validate(test_map)

    # Key should be preserved exactly
    assert len(validated.value) == 1
    assert sneaky_key in validated.value


@SECURITY_SETTINGS
@given(
    confusable_pair=st.sampled_from(
        [
            ("a", "а"),  # Latin 'a' vs Cyrillic 'а'  # noqa: RUF001, RUF003
            ("o", "о"),  # Latin 'o' vs Cyrillic 'о'  # noqa: RUF001, RUF003
            ("p", "р"),  # Latin 'p' vs Cyrillic 'р'  # noqa: RUF001, RUF003
            ("c", "с"),  # Latin 'c' vs Cyrillic 'с'  # noqa: RUF001, RUF003
        ]
    )
)
def test_confusable_characters_are_distinct(confusable_pair: tuple[str, str]) -> None:
    """
    Security test: Visually similar characters should be treated as distinct.

    Homoglyphs (characters that look identical) can be used for spoofing.
    We preserve them as distinct but consumers should be aware.
    """
    char1, char2 = confusable_pair
    map_type = CtyMap(element_type=CtyString())

    # Create keys with confusable characters
    key1 = f"key_{char1}"
    key2 = f"key_{char2}"

    test_map = {key1: "value1", key2: "value2"}

    # Validate
    validated = map_type.validate(test_map)

    # Both keys should be preserved as distinct
    assert len(validated.value) == 2
    assert key1 in validated.value
    assert key2 in validated.value


def test_attribute_names_with_path_separators_are_documented_risk() -> None:
    """
    Security test: Path-like attribute names are a documented consumer risk.

    CTY itself doesn't use attribute names for file I/O, so path traversal
    patterns are accepted. This test documents the behavior and verifies CTY
    doesn't misuse them internally.
    """
    # These are accepted - consumers must sanitize if they use attr names for paths
    risky_names = ["../../../etc/passwd", "./config", "../../data", "key/with/slashes"]

    for risky_name in risky_names:
        # Should not crash or reject
        obj_type = CtyObject(attribute_types={risky_name: CtyString()})

        # Verify the attribute is stored correctly
        assert risky_name in obj_type.attribute_types

        # Validate with actual data
        obj_val = obj_type.validate({risky_name: "test_value"})
        assert risky_name in obj_val.value


def test_null_bytes_in_attribute_names_are_documented_risk() -> None:
    """
    Security test: Null bytes in attribute names are a documented consumer risk.

    Null bytes can break C string interop or cause truncation issues.
    CTY accepts them since Python strings can contain nulls, but consumers
    interfacing with C code should sanitize.
    """
    # Null bytes are accepted in Python strings
    null_name = "key\x00hidden"

    obj_type = CtyObject(attribute_types={null_name: CtyString()})

    # Verify stored correctly
    assert null_name in obj_type.attribute_types
    assert len(null_name) == 10  # Not truncated

    # Validate
    obj_val = obj_type.validate({null_name: "test_value"})
    assert null_name in obj_val.value


@SECURITY_SETTINGS
@given(large_decimal=st.integers(min_value=10**100, max_value=10**200))
def test_extremely_large_numbers_dont_crash(large_decimal: int) -> None:
    """
    Security test: Extremely large numbers should be handled gracefully.

    Tests numbers far beyond float64 range to verify no crashes.
    """
    num_type = CtyNumber()

    # Should not crash
    cty_val = num_type.validate(large_decimal)

    # Should be stored as Decimal with correct value
    assert isinstance(cty_val.value, Decimal)
    assert str(cty_val.value) == str(large_decimal)


# 🌊🪢🔚
