# tests/tuple/test_cty_tuple_validation.py

"""
Tests for CtyTuple type validation logic.
"""

import pytest
from decimal import Decimal
from pyvider.cty import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtyObject, CtyTuple,
    CtyDynamic, CtyType, CtyValue
)
from pyvider.cty.exceptions import CtyValidationError


class TestCtyTupleValidation:
    """Tests the CtyTuple.validate() method."""

    @pytest.fixture
    def tuple_type_sn(self):
        """Fixture for a simple (String, Number) tuple type."""
        return CtyTuple(element_types=(CtyString(), CtyNumber()))

    @pytest.fixture
    def tuple_type_complex(self):
        """Fixture for a complex tuple type."""
        return CtyTuple(element_types=(
            CtyString(),
            CtyList(element_type=CtyBool()),
            CtyNumber()
        ))

    @pytest.mark.asyncio
    async def test_validate_valid_tuple(self, tuple_type_sn):
        """Test validating a conforming tuple."""
        data = ("hello", 42)
        result_val = tuple_type_sn.validate(data)

        assert isinstance(result_val, CtyValue)
        assert isinstance(result_val.type, CtyTuple)
        assert result_val.type.equal(tuple_type_sn) # Check type equality
        assert not result_val.is_null
        assert not result_val.is_unknown

        # Check internal structure
        assert isinstance(result_val.value, tuple)
        assert len(result_val.value) == 2

        # Check elements
        assert isinstance(result_val.value[0], CtyValue)
        assert isinstance(result_val.value[0].type, CtyString)
        assert result_val.value[0].value == "hello"

        assert isinstance(result_val.value[1], CtyValue)
        assert isinstance(result_val.value[1].type, CtyNumber)
        assert result_val.value[1].value == Decimal("42") # Numbers stored as Decimal

    @pytest.mark.asyncio
    async def test_validate_valid_list(self, tuple_type_sn):
        """Test validating a conforming list (should be accepted)."""
        data = ["world", 123.45]
        result_val = tuple_type_sn.validate(data) # Pass a list

        assert isinstance(result_val, CtyValue)
        assert isinstance(result_val.type, CtyTuple)
        assert isinstance(result_val.value, tuple) # Internal value should be tuple
        assert len(result_val.value) == 2
        assert result_val.value[0].value == "world"
        assert result_val.value[1].value == Decimal("123.45")

    @pytest.mark.asyncio
    async def test_validate_empty_tuple(self):
        """Test validating an empty tuple against an empty tuple type."""
        empty_type = CtyTuple(element_types=())
        result_val = empty_type.validate(())
        assert isinstance(result_val, CtyValue)
        assert isinstance(result_val.type, CtyTuple)
        assert result_val.type.equal(empty_type)
        assert isinstance(result_val.value, tuple)
        assert len(result_val.value) == 0

        result_val_list = empty_type.validate([])
        assert len(result_val_list.value) == 0

    @pytest.mark.asyncio
    async def test_validate_invalid_length_too_short(self, tuple_type_sn):
        """Test validation fails if tuple is too short."""
        data = ("hello",)
        with pytest.raises(CtyValidationError) as exc_info:
            tuple_type_sn.validate(data)
        assert "Expected 2 elements, got 1" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_invalid_length_too_long(self, tuple_type_sn):
        """Test validation fails if tuple is too long."""
        data = ("hello", 42, True)
        with pytest.raises(CtyValidationError) as exc_info:
            tuple_type_sn.validate(data)
        assert "Expected 2 elements, got 3" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_invalid_element_type(self, tuple_type_sn):
        """Test validation fails if an element has the wrong type."""
        data = ("hello", "not a number") # Second element is wrong type
        with pytest.raises(CtyValidationError) as exc_info:
            tuple_type_sn.validate(data)
        assert "Invalid value for tuple element 1" in str(exc_info.value)
        # Check for nested error message from CtyNumber validation
        assert "Cannot convert string 'not a number' to number" in str(exc_info.value)

        data_2 = (123, 42) # First element is wrong type
        with pytest.raises(CtyValidationError) as exc_info_2:
            tuple_type_sn.validate(data_2)
        assert "Invalid value for tuple element 0" in str(exc_info_2.value)
        assert "Value must be a string, got int" in str(exc_info_2.value)

    @pytest.mark.asyncio
    async def test_validate_invalid_input_type(self, tuple_type_sn):
        """Test validation fails for non-list/tuple inputs."""
        invalid_inputs = [
            None,
            123,
            "a string",
            {"a": 1},
            {"a", "b"},
            CtyValue.string("test") # Should pass dict or list/tuple, not other CtyValues
        ]
        for invalid_input in invalid_inputs:
            with pytest.raises(CtyValidationError) as exc_info:
                tuple_type_sn.validate(invalid_input)
            assert "Expected tuple or list" in str(exc_info.value)
            assert type(invalid_input).__name__ in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_with_ctyvalues_input(self, tuple_type_sn):
        """Test validating a tuple containing CtyValue instances."""
        val1 = CtyValue.string("cty")
        val2 = CtyValue.number(99)
        data = (val1, val2)
        result_val = tuple_type_sn.validate(data)

        assert isinstance(result_val, CtyValue)
        assert len(result_val.value) == 2
        # Should preserve the original CtyValue instances if types match
        assert result_val.value[0] is val1
        assert result_val.value[1] is val2

    @pytest.mark.asyncio
    async def test_validate_with_ctyvalues_mismatched_type(self, tuple_type_sn):
        """Test validation fails if input CtyValue has wrong type."""
        val1 = CtyValue.string("cty")
        val2_wrong = CtyValue.bool(True) # Should be number
        data = (val1, val2_wrong)
        with pytest.raises(CtyValidationError) as exc_info:
            tuple_type_sn.validate(data)
        assert "Invalid value for tuple element 1" in str(exc_info.value)
        # Check for the error from CtyNumber validation trying bool
        assert "Value must be a number" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_complex_tuple(self, tuple_type_complex):
        """Test validation with nested collections."""
        data = ("config", [True, False, True], 10.5)
        result_val = tuple_type_complex.validate(data)

        assert isinstance(result_val, CtyValue)
        assert len(result_val.value) == 3

        # Check types and values
        assert result_val.value[0].value == "config"
        assert isinstance(result_val.value[1], CtyValue)
        assert isinstance(result_val.value[1].type, CtyList)
        assert [v.value for v in result_val.value[1].value] == [True, False, True]
        assert result_val.value[2].value == Decimal("10.5")
