#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test module for CtySet implementation.

This module contains tests for the CtySet type, ensuring proper validation,
equality checking, and other operations."""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtySetValidationError


class TestCtySetType:
    """Test suite for CtySet type."""

    def setup_method(self) -> None:
        """set up test fixtures."""
        self.string_set = CtySet(element_type=CtyString())
        self.number_set = CtySet(element_type=CtyNumber())
        self.bool_set = CtySet(element_type=CtyBool())

    def test_attrs_post_init_invalid_element_type(self) -> None:
        """Test that __attrs_post_init__ raises an error for invalid element_type."""
        with pytest.raises(CtySetValidationError):
            CtySet(element_type="not a cty type")

    # -------------------- VALIDATION TESTS --------------------
    @pytest.mark.asyncio
    async def test_validate_valid_string_set(self) -> None:
        """Test validation of a valid string set."""
        valid = {"apple", "banana", "cherry"}
        validated = self.string_set.validate(valid)
        assert isinstance(validated, CtyValue)
        assert isinstance(validated.type, CtySet)
        assert validated == self.string_set.validate(list(valid))

    @pytest.mark.asyncio
    async def test_validate_valid_number_set(self) -> None:
        """Test validation of a valid number set."""
        valid = {1, 2, 3}
        validated = self.number_set.validate(valid)
        assert validated == self.number_set.validate(list(valid))

    @pytest.mark.asyncio
    async def test_validate_valid_bool_set(self) -> None:
        """Test validation of a valid boolean set."""
        valid = {True, False}
        validated = self.bool_set.validate(valid)
        assert validated == self.bool_set.validate(list(valid))

    @pytest.mark.asyncio
    async def test_validate_with_cty_value(self) -> None:
        """Test validation with a CtyValue as input."""
        cty_value = self.string_set.validate({"a", "b"})
        validated = self.string_set.validate(cty_value)
        assert validated == cty_value

    @pytest.mark.asyncio
    async def test_validate_with_list_or_tuple(self) -> None:
        """Test validation with a list or tuple as input."""
        expected = self.string_set.validate({"a", "b"})
        assert self.string_set.validate(["a", "b", "a"]) == expected
        assert self.string_set.validate(("a", "b", "a")) == expected

    @pytest.mark.asyncio
    async def test_validate_with_unhashable_elements_in_list(self) -> None:
        """Test validation with a list containing unhashable elements."""
        tuple_set_type = CtySet(element_type=CtyTuple((CtyString(),)))
        validated = tuple_set_type.validate([("a",), ("b",)])
        assert len(validated.value) == 2

    @pytest.mark.asyncio
    async def test_validate_invalid_element_type(self) -> None:
        mixed_types = {"apple", 2, True}
        with pytest.raises(CtySetValidationError) as exc_info:
            self.string_set.validate(mixed_types)
        assert "String validation error" in str(exc_info.value)
        assert "Cannot convert" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_empty_set(self) -> None:
        """Test validation of an empty set."""
        empty = set()
        validated = self.string_set.validate(empty)
        assert len(validated.value) == 0

    @pytest.mark.asyncio
    async def test_validate_none_value(self) -> None:
        """Test validation with None value."""
        validated = self.string_set.validate(None)
        assert validated.is_null is True

    @pytest.mark.asyncio
    async def test_validate_non_iterable(self) -> None:
        """Test validation with non-iterable value."""
        with pytest.raises(CtySetValidationError):
            self.string_set.validate(123)

    @pytest.mark.asyncio
    async def test_validate_nested_set(self) -> None:
        """Test validation with nested set of tuples (a valid, hashable construct)."""
        nested_set_type = CtySet(element_type=CtyTuple((CtyString(),)))
        validated = nested_set_type.validate([("a",), ("b",)])
        assert len(validated.value) == 2

    # -------------------- EQUALITY AND COMPARISON TESTS --------------------

    @pytest.mark.asyncio
    async def test_set_equality(self) -> None:
        """Test equality of sets with same element type."""
        set1 = CtySet(element_type=CtyString())
        set2 = CtySet(element_type=CtyString())
        assert set1.equal(set2)

    @pytest.mark.asyncio
    async def test_set_inequality(self) -> None:
        """Test inequality of sets with different element types."""
        assert not self.string_set.equal(self.number_set)

    @pytest.mark.asyncio
    async def test_usable_as_same_type(self) -> None:
        """Test usable_as with same type."""
        set1 = CtySet(element_type=CtyString())
        set2 = CtySet(element_type=CtyString())
        assert set1.usable_as(set2)

    @pytest.mark.asyncio
    async def test_usable_as_dynamic(self) -> None:
        """Test that any set is usable as dynamic."""
        assert self.string_set.usable_as(CtyDynamic())

    @pytest.mark.asyncio
    async def test_usable_as_different_type(self) -> None:
        """Test usable_as with different type."""
        assert not self.string_set.usable_as(self.number_set)

    @pytest.mark.asyncio
    async def test_usable_as_non_set_type(self) -> None:
        """Test usable_as with non-set type."""
        assert not self.string_set.usable_as(CtyString())

    # -------------------- EDGE CASES --------------------

    @pytest.mark.asyncio
    async def test_large_set(self) -> None:
        """Test validation of a large set."""
        large_set = {str(i) for i in range(1000)}
        validated = self.string_set.validate(large_set)
        assert len(validated.value) == 1000

    @pytest.mark.asyncio
    async def test_string_representation(self) -> None:
        """Test string representation of CtySet."""
        assert str(self.string_set) == "set(string)"

    @pytest.mark.asyncio
    async def test_iteration(self) -> None:
        """Test iteration over set values."""
        set_obj = self.string_set.validate({"apple", "banana", "cherry"})
        values = {item.value for item in set_obj.value}
        assert values == {"apple", "banana", "cherry"}


# 🌊🪢🔚
