#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD Test Suite for ergonomic helper methods on CtyValue.

These tests define the behavior for methods that allow for clean, immutable
updates to collection-based CtyValue objects, as seen in the project's examples."""

import pytest

from pyvider.cty import (
    CtyList,
    CtyMap,
    CtyNumber,
    CtyString,
    CtyValue,
)
from pyvider.cty.exceptions import CtyValidationError


class TestCtyValueMapOperations:
    """TDD for immutable map update helpers."""

    @pytest.fixture
    def map_val(self) -> CtyValue:
        map_type = CtyMap(element_type=CtyNumber())
        return map_type.validate({"max_connections": 100, "timeout": 30})

    def test_with_key_adds_and_updates(self, map_val: CtyValue) -> None:
        """TDD: .with_key() should add a new key or update an existing one."""
        new_val = map_val.with_key("batch_size", 500)
        assert new_val.raw_value == {
            "max_connections": 100,
            "timeout": 30,
            "batch_size": 500,
        }
        updated_val = new_val.with_key("timeout", 60)
        assert updated_val.raw_value == {
            "max_connections": 100,
            "timeout": 60,
            "batch_size": 500,
        }
        assert map_val.raw_value == {"max_connections": 100, "timeout": 30}

    def test_without_key_removes(self, map_val: CtyValue) -> None:
        """TDD: .without_key() should remove a key."""
        new_val = map_val.without_key("timeout")
        assert new_val.raw_value == {"max_connections": 100}
        same_val = new_val.without_key("non_existent")
        assert same_val.raw_value == {"max_connections": 100}
        assert map_val.raw_value == {"max_connections": 100, "timeout": 30}

    def test_with_key_on_non_map_fails(self) -> None:
        """TDD: Calling .with_key() on a non-map value should raise TypeError."""
        list_val = CtyList(element_type=CtyString()).validate(["a"])
        with pytest.raises(TypeError):
            list_val.with_key("foo", "bar")

    def test_map_with_key_with_wrong_element_type_raises_error(self, map_val: CtyValue) -> None:
        """Verifies that .with_key() validates the new value against the map's element type."""
        with pytest.raises(CtyValidationError):
            map_val.with_key("b", "not-a-number")
        with pytest.raises(CtyValidationError):
            map_val.with_key("a", "also-not-a-number")


class TestCtyValueListOperations:
    """TDD for immutable list update helpers."""

    @pytest.fixture
    def list_val(self) -> CtyValue:
        list_type = CtyList(element_type=CtyString())
        return list_type.validate(["a", "b", "c"])

    def test_append(self, list_val: CtyValue) -> None:
        """TDD: .append() should add an element to the end of the list."""
        new_val = list_val.append("d")
        assert new_val.raw_value == ["a", "b", "c", "d"]
        assert list_val.raw_value == ["a", "b", "c"]

    def test_append_invalid_type_fails(self, list_val: CtyValue) -> None:
        """TDD: .append() should raise a validation error for the wrong type."""
        with pytest.raises(CtyValidationError):
            list_val.append(123)

    def test_with_element_at(self, list_val: CtyValue) -> None:
        """TDD: .with_element_at() should replace an element at a given index."""
        new_val = list_val.with_element_at(1, "x")
        assert new_val.raw_value == ["a", "x", "c"]
        assert list_val.raw_value == ["a", "b", "c"]

    def test_with_element_at_out_of_bounds_fails(self, list_val: CtyValue) -> None:
        """TDD: .with_element_at() should fail for an out-of-bounds index."""
        with pytest.raises(IndexError):
            list_val.with_element_at(5, "z")

    def test_append_on_non_list_fails(self) -> None:
        """TDD: Calling .append() on a non-list value should raise TypeError."""
        map_val = CtyMap(element_type=CtyString()).validate({"a": "b"})
        with pytest.raises(TypeError):
            map_val.append("c")

    def test_list_with_element_at_with_wrong_element_type_raises_error(self, list_val: CtyValue) -> None:
        """Verifies that .with_element_at() validates the new element against the list's element type."""
        with pytest.raises(CtyValidationError):
            list_val.with_element_at(0, 456)


# 🌊🪢🔚
