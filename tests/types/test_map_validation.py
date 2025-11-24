#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for CtyMap validation edge cases.

This test suite focuses on achieving 100% coverage of map.py, particularly:
- Lines 46, 48, 52 (null/unknown handling in validate)
- Lines 94, 108, 116-118 (error paths in get and validation)
- Edge cases with non-dict inputs, non-string keys, value type mismatches"""

import pytest

from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import (
    CtyMapValidationError,
    CtyTypeMismatchError,
    InvalidTypeError,
)
from pyvider.cty.types.collections.map import CtyMap
from pyvider.cty.types.structural import CtyDynamic


class TestCtyMapValidation:
    """Test CtyMap validation edge cases."""

    def test_validate_ctyvalue_null(self) -> None:
        """Test: validate CtyValue.null() returns null (line 46)."""
        map_type = CtyMap(element_type=CtyString())
        null_value = CtyValue.null(map_type)
        result = map_type.validate(null_value)

        assert result.is_null
        assert result.type == map_type

    def test_validate_ctyvalue_unknown(self) -> None:
        """Test: validate CtyValue.unknown() returns unknown (line 48)."""
        map_type = CtyMap(element_type=CtyNumber())
        unknown_value = CtyValue.unknown(map_type)
        result = map_type.validate(unknown_value)

        assert result.is_unknown
        assert result.type == map_type

    def test_validate_none_returns_null(self) -> None:
        """Test: validate None returns null (line 52)."""
        map_type = CtyMap(element_type=CtyString())
        result = map_type.validate(None)

        assert result.is_null
        assert result.type == map_type

    def test_validate_non_dict_raises_error(self) -> None:
        """Test: validate non-dict input raises CtyMapValidationError (line 54-55)."""
        map_type = CtyMap(element_type=CtyString())

        with pytest.raises(CtyMapValidationError, match=r"Input must be a dictionary, got list\."):
            map_type.validate(["not", "a", "dict"])

    def test_validate_non_string_key_raises_error(self) -> None:
        """Test: validate dict with non-string key raises error (line 66-69)."""
        map_type = CtyMap(element_type=CtyString())

        with pytest.raises(CtyMapValidationError, match="Map keys must be strings, but got key of type int"):
            map_type.validate({123: "value"})

    def test_validate_value_type_mismatch_raises_error(self) -> None:
        """Test: validate value type mismatch raises error with path (line 75-77)."""
        map_type = CtyMap(element_type=CtyNumber())

        with pytest.raises(CtyMapValidationError) as exc_info:
            map_type.validate({"key1": 42, "key2": "not a number"})

        # Should include path information
        assert exc_info.value.path is not None

    def test_validate_unicode_normalization(self) -> None:
        """Test: keys are normalized using NFC (line 71)."""
        map_type = CtyMap(element_type=CtyString())
        # Use a key with combining characters
        result = map_type.validate({"café": "value"})

        assert not result.is_null
        assert not result.is_unknown
        # Key should be normalized
        assert "café" in result.value

    def test_validate_with_unknown_values_in_map(self) -> None:
        """Test: map with unknown values is marked as unknown (line 79)."""
        map_type = CtyMap(element_type=CtyNumber())
        result = map_type.validate(
            {
                "known": 42,
                "unknown": CtyValue.unknown(CtyNumber()),
            }
        )

        # Map itself should be marked as unknown because it contains unknown values
        assert result.is_unknown

    def test_validate_fast_path_same_type(self) -> None:
        """Test: fast path when CtyValue already has correct type (line 43-44)."""
        map_type = CtyMap(element_type=CtyString())
        original = map_type.validate({"key": "value"})
        # Re-validate the same value
        result = map_type.validate(original)

        assert result == original


class TestCtyMapGetOperation:
    """Test CtyMap.get() method edge cases."""

    def test_get_from_null_map_returns_null(self) -> None:
        """Test: get() on null map returns null (line 90-91)."""
        map_type = CtyMap(element_type=CtyString())
        null_map = CtyValue.null(map_type)
        result = map_type.get(null_map, "any_key")

        assert result.is_null

    def test_get_from_unknown_map_returns_null(self) -> None:
        """Test: get() on unknown map returns null (line 90-91)."""
        map_type = CtyMap(element_type=CtyNumber())
        unknown_map = CtyValue.unknown(map_type)
        result = map_type.get(unknown_map, "any_key")

        assert result.is_null

    def test_get_from_null_map_returns_default(self) -> None:
        """Test: get() on null map returns provided default (line 91)."""
        map_type = CtyMap(element_type=CtyString())
        null_map = CtyValue.null(map_type)
        default = CtyString().validate("default_value")
        result = map_type.get(null_map, "any_key", default=default)

        assert not result.is_null
        assert result.value == "default_value"

    def test_get_non_map_ctyvalue_raises_error(self) -> None:
        """Test: get() on non-map CtyValue raises CtyTypeMismatchError (line 88-89)."""
        map_type = CtyMap(element_type=CtyString())
        not_a_map = CtyString().validate("not a map")

        with pytest.raises(CtyTypeMismatchError, match="get operation called on non-map CtyValue"):
            map_type.get(not_a_map, "key")

    def test_get_malformed_internal_value_raises_error(self) -> None:
        """Test: get() with malformed internal value raises error (line 94-96)."""
        map_type = CtyMap(element_type=CtyString())
        # Create a malformed CtyValue (this is an internal error scenario)
        # We need to bypass normal validation to create this
        malformed = CtyValue(vtype=map_type, value="not a dict")

        with pytest.raises(
            CtyMapValidationError,
            match="Internal error: CtyValue of CtyMap type does not wrap a dict, got str",
        ):
            map_type.get(malformed, "key")

    def test_get_existing_key(self) -> None:
        """Test: get() returns value for existing key."""
        map_type = CtyMap(element_type=CtyNumber())
        map_value = map_type.validate({"key1": 42, "key2": 100})
        result = map_type.get(map_value, "key1")

        assert not result.is_null
        assert result.value == 42

    def test_get_missing_key_returns_null(self) -> None:
        """Test: get() returns null for missing key."""
        map_type = CtyMap(element_type=CtyNumber())
        map_value = map_type.validate({"key1": 42})
        result = map_type.get(map_value, "missing_key")

        assert result.is_null

    def test_get_missing_key_returns_default(self) -> None:
        """Test: get() returns default for missing key."""
        map_type = CtyMap(element_type=CtyNumber())
        map_value = map_type.validate({"key1": 42})
        default = CtyNumber().validate(999)
        result = map_type.get(map_value, "missing_key", default=default)

        assert not result.is_null
        assert result.value == 999


class TestCtyMapTypeOperations:
    """Test CtyMap type equality and usability."""

    def test_equal_same_element_type(self) -> None:
        """Test: maps with same element type are equal."""
        map1 = CtyMap(element_type=CtyString())
        map2 = CtyMap(element_type=CtyString())

        assert map1.equal(map2)

    def test_not_equal_different_element_type(self) -> None:
        """Test: maps with different element types are not equal (line 108)."""
        map1 = CtyMap(element_type=CtyString())
        map2 = CtyMap(element_type=CtyNumber())

        assert not map1.equal(map2)

    def test_not_equal_to_non_map_type(self) -> None:
        """Test: map not equal to non-map type (line 107-108)."""
        map_type = CtyMap(element_type=CtyString())
        string_type = CtyString()

        assert not map_type.equal(string_type)

    def test_usable_as_dynamic(self) -> None:
        """Test: map is usable as CtyDynamic (line 114-115)."""
        map_type = CtyMap(element_type=CtyString())
        dynamic = CtyDynamic()

        assert map_type.usable_as(dynamic)

    def test_not_usable_as_non_map(self) -> None:
        """Test: map not usable as non-map type (line 116-117)."""
        map_type = CtyMap(element_type=CtyString())
        string_type = CtyString()

        assert not map_type.usable_as(string_type)

    def test_usable_as_compatible_element_type(self) -> None:
        """Test: map usable as map with compatible element type (line 118)."""
        # For now, element types must be equal
        map1 = CtyMap(element_type=CtyString())
        map2 = CtyMap(element_type=CtyString())

        assert map1.usable_as(map2)

    def test_not_usable_as_incompatible_element_type(self) -> None:
        """Test: map not usable as map with incompatible element type."""
        map1 = CtyMap(element_type=CtyString())
        map2 = CtyMap(element_type=CtyNumber())

        assert not map1.usable_as(map2)


class TestCtyMapInitialization:
    """Test CtyMap initialization validation."""

    def test_init_with_invalid_element_type_raises_error(self) -> None:
        """Test: initializing CtyMap with non-CtyType element raises InvalidTypeError."""
        with pytest.raises(InvalidTypeError, match="element_type must be a CtyType instance, got str"):
            CtyMap(element_type="not a type")  # type: ignore[arg-type]

    def test_init_with_valid_element_type_succeeds(self) -> None:
        """Test: initializing CtyMap with valid CtyType succeeds."""
        map_type = CtyMap(element_type=CtyNumber())

        assert isinstance(map_type.element_type, CtyNumber)


# 🌊🪢🔚
