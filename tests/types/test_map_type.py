#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty.exceptions import (
    CtyMapValidationError,
    CtyTypeMismatchError,
    CtyValidationError,
    InvalidTypeError,
)
from pyvider.cty.types import CtyDynamic, CtyMap, CtyNumber, CtyString, CtyType
from pyvider.cty.values import CtyValue


class TestCtyMap:
    def test_map_creation_and_type_equality(self) -> None:
        """Tests that a CtyMap can be created with an element_type."""
        map_type = CtyMap(element_type=CtyString())
        assert isinstance(map_type.element_type, CtyType)
        assert map_type.equal(CtyMap(element_type=CtyString()))
        assert not map_type.equal(CtyMap(element_type=CtyNumber()))

    def test_map_validation_success(self) -> None:
        map_type = CtyMap(element_type=CtyNumber())
        value = map_type.validate({"a": 1, "b": 100})
        assert isinstance(value, CtyValue)
        # CORRECTED: CtyValue.__eq__ is defined to compare the underlying values.
        # We compare the returned CtyValue with an expected CtyValue.
        assert value.value["a"] == CtyNumber().validate(1)

    def test_map_validation_with_cty_value(self) -> None:
        map_type = CtyMap(element_type=CtyNumber())
        cty_value = map_type.validate({"a": 1})
        validated = map_type.validate(cty_value)
        assert validated == cty_value

    def test_map_validation_non_dict_fails(self) -> None:
        map_type = CtyMap(element_type=CtyNumber())
        with pytest.raises(CtyMapValidationError):
            map_type.validate([1, 2, 3])

    def test_map_validation_non_string_keys_fails(self) -> None:
        map_type = CtyMap(element_type=CtyNumber())
        with pytest.raises(CtyMapValidationError):
            map_type.validate({1: 1, 2: 2})

    def test_map_get_method(self) -> None:
        map_type = CtyMap(element_type=CtyNumber())
        map_value = map_type.validate({"a": 1})
        assert map_type.get(map_value, "a") == CtyNumber().validate(1)
        assert map_type.get(map_value, "b").is_null
        assert map_type.get(map_value, "b", CtyNumber().validate(42)) == CtyNumber().validate(42)

    def test_map_get_on_non_map_value_fails(self) -> None:
        map_type = CtyMap(element_type=CtyNumber())
        with pytest.raises(CtyTypeMismatchError):
            map_type.get(CtyString().validate("not a map"), "a")

    def test_map_usable_as_dynamic(self) -> None:
        map_type = CtyMap(element_type=CtyNumber())
        assert map_type.usable_as(CtyDynamic())

    def test_map_validation_type_mismatch_fails(self) -> None:
        map_type = CtyMap(element_type=CtyNumber())
        with pytest.raises(CtyValidationError):
            map_type.validate({"a": 1, "b": "not-a-number"})

    def test_map_creation_with_invalid_type_fails(self) -> None:
        """Ensures the constructor raises an error for invalid element types."""
        with pytest.raises(InvalidTypeError):
            CtyMap(element_type="not a cty type")


# 🌊🪢🔚
