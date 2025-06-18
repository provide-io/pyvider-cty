# tests/tuple/test_cty_tuple_operations.py

"""
Tests for CtyTuple operations (indexing, slicing) and related CtyValue operations.
"""

from decimal import Decimal

import pytest

from pyvider.cty import (
    CtyBool,
    CtyNumber,
    CtyString,
    CtyTuple,
    CtyValue,
)


class TestCtyTupleOperations:
    """Tests operations on CtyTuple types and CtyValue tuple instances."""

    @pytest.fixture
    def tuple_type(self):
        """Fixture for a (String, Number, Bool) tuple type."""
        return CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))

    @pytest.fixture
    def tuple_value(self, tuple_type):
        """Fixture for a CtyValue instance of the tuple type."""
        # Use the type's validate method to create the value correctly
        return tuple_type.validate(("data", 123, False))

    # --- Tests for CtyTuple methods (element_at, slice) ---

    @pytest.mark.asyncio
    async def test_element_at_valid_indices(self, tuple_type, tuple_value) -> None:
        """Test element_at with valid positive and negative indices."""
        # Note: element_at operates on the *internal* tuple of CtyValues
        internal_tuple = tuple_value.value

        # Positive indices
        el0 = tuple_type.element_at(internal_tuple, 0)
        el1 = tuple_type.element_at(internal_tuple, 1)
        el2 = tuple_type.element_at(internal_tuple, 2)
        assert isinstance(el0, CtyValue) and el0.value == "data"
        assert isinstance(el1, CtyValue) and el1.value == Decimal("123")
        assert isinstance(el2, CtyValue) and el2.value is False

        # Negative indices
        el_neg1 = tuple_type.element_at(internal_tuple, -1)  # Last element
        el_neg3 = tuple_type.element_at(internal_tuple, -3)  # First element
        assert el_neg1 is el2
        assert el_neg3 is el0

    @pytest.mark.asyncio
    async def test_element_at_out_of_bounds(self, tuple_type, tuple_value) -> None:
        """Test element_at raises Exception for out-of-bounds indices."""
        internal_tuple = tuple_value.value
        with pytest.raises(Exception):
            tuple_type.element_at(internal_tuple, 3)
        with pytest.raises(Exception):
            tuple_type.element_at(internal_tuple, -4)

    @pytest.mark.asyncio
    async def test_slice_valid(self, tuple_type, tuple_value) -> None:
        """Test slice method with various valid ranges."""
        internal_tuple = tuple_value.value

        # Slice [0:2] -> (String, Number)
        slice02_val = tuple_type.slice(internal_tuple, 0, 2)
        assert isinstance(slice02_val, CtyValue)
        assert isinstance(slice02_val.type, CtyTuple)
        assert len(slice02_val.type.element_types) == 2
        assert isinstance(slice02_val.type.element_types[0], CtyString)
        assert isinstance(slice02_val.type.element_types[1], CtyNumber)
        assert len(slice02_val.value) == 2
        assert slice02_val.value[0].value == "data"
        assert slice02_val.value[1].value == Decimal("123")

        # Slice [1:] -> (Number, Bool)
        slice1_val = tuple_type.slice(
            internal_tuple, 1, 3
        )  # Explicit end needed for tuple.slice
        assert isinstance(slice1_val.type, CtyTuple)
        assert len(slice1_val.type.element_types) == 2
        assert isinstance(slice1_val.type.element_types[0], CtyNumber)
        assert isinstance(slice1_val.type.element_types[1], CtyBool)
        assert len(slice1_val.value) == 2
        assert slice1_val.value[0].value == Decimal("123")
        assert slice1_val.value[1].value is False

        # Slice [:-1] -> (String, Number)
        slice_neg1_val = tuple_type.slice(internal_tuple, 0, -1)
        assert len(slice_neg1_val.value) == 2
        assert slice_neg1_val.value[0].value == "data"
        assert slice_neg1_val.value[1].value == Decimal("123")

        # Empty slice
        slice_empty = tuple_type.slice(internal_tuple, 1, 1)
        assert isinstance(slice_empty.type, CtyTuple)
        assert len(slice_empty.type.element_types) == 0
        assert len(slice_empty.value) == 0

    @pytest.mark.asyncio
    async def test_slice_out_of_bounds(self, tuple_type, tuple_value) -> None:
        """Test slice method handles out-of-bounds indices gracefully (clamps)."""
        internal_tuple = tuple_value.value
        # Slice indices are typically clamped in Python slicing
        slice_oob_end = tuple_type.slice(internal_tuple, 1, 10)  # End clamped to 3
        assert len(slice_oob_end.value) == 2
        assert slice_oob_end.value[0].value == Decimal("123")
        assert slice_oob_end.value[1].value is False

        slice_oob_start = tuple_type.slice(internal_tuple, 5, 10)  # Start clamped to 3
        assert len(slice_oob_start.value) == 0

    # --- Tests for CtyValue operations (__getitem__, __len__, __iter__) ---

    @pytest.mark.asyncio
    async def test_value_getitem_index(self, tuple_value) -> None:
        """Test CtyValue.__getitem__ for integer indexing."""
        el0 = tuple_value[0]
        el1 = tuple_value[1]
        el2 = tuple_value[2]
        assert isinstance(el0, CtyValue) and el0.value == "data"
        assert isinstance(el1, CtyValue) and el1.value == Decimal("123")
        assert isinstance(el2, CtyValue) and el2.value is False

        # Negative index
        assert tuple_value[-1].value is False

        # Out of bounds
        with pytest.raises(Exception):
            _ = tuple_value[3]
        with pytest.raises(Exception):
            _ = tuple_value[-4]

    @pytest.mark.asyncio
    async def test_value_getitem_slice(self, tuple_value) -> None:
        """Test CtyValue.__getitem__ for slicing."""
        slice02 = tuple_value[0:2]
        assert isinstance(slice02, CtyValue)
        assert isinstance(slice02.type, CtyTuple)
        assert len(slice02.type.element_types) == 2
        assert isinstance(slice02.type.element_types[0], CtyString)
        assert isinstance(slice02.type.element_types[1], CtyNumber)
        assert len(slice02.value) == 2
        assert slice02.value[0].value == "data"
        assert slice02.value[1].value == Decimal("123")

        slice_neg = tuple_value[1:-1]  # -> index 1 only
        assert len(slice_neg.value) == 1
        assert slice_neg.value[0].value == Decimal("123")

    @pytest.mark.asyncio
    async def test_value_length(self, tuple_value) -> None:
        """Test len() on a CtyValue tuple."""
        assert len(tuple_value) == 3

        empty_type = CtyTuple(element_types=())
        empty_value = empty_type.validate(())
        assert len(empty_value) == 0

    @pytest.mark.asyncio
    async def test_value_iteration(self, tuple_value) -> None:
        """Test iterating over a CtyValue tuple."""
        elements = []
        for element in tuple_value:
            assert isinstance(element, CtyValue)
            elements.append(element.value)

        assert elements == ["data", Decimal("123"), False]

    @pytest.mark.asyncio
    async def test_operations_on_null_unknown(self, tuple_type) -> None:
        """Test operations on null and unknown tuple values."""
        null_tuple = CtyValue.null(tuple_type)
        unknown_tuple = CtyValue.unknown(tuple_type)

        # len()
        assert len(null_tuple) == 0  # Length of null tuple is 0
        with pytest.raises(
            TypeError
        ):  # Length of unknown tuple raises TypeError (as per CtyValue base behavior)
            len(unknown_tuple)

        # __getitem__ (index)
        with pytest.raises(TypeError):  # Indexing null tuple raises TypeError
            _ = null_tuple[0]
        with pytest.raises(TypeError):  # Indexing unknown tuple raises TypeError
            _ = unknown_tuple[0]

        # __getitem__ (slice)
        with pytest.raises(TypeError):  # Slicing null tuple raises TypeError
            _ = null_tuple[0:1]
        with pytest.raises(TypeError):  # Slicing unknown tuple raises TypeError
            _ = unknown_tuple[0:1]

        # __iter__
        assert list(null_tuple) == []  # Iterating null tuple yields empty list
        with pytest.raises(TypeError):  # Iterating unknown tuple raises TypeError
            list(unknown_tuple)
