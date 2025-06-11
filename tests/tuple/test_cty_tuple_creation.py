# tests/tuple/test_cty_tuple_creation.py

"""
Tests for CtyTuple type creation and initialization.
"""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
)
from pyvider.cty.exceptions import CtyTupleValidationError


class TestCtyTupleCreation:
    """Tests initialization of CtyTuple types."""

    @pytest.mark.asyncio
    async def test_tuple_type_initialization_simple(self) -> None:
        """Test basic initialization with primitive types."""
        str_num_bool = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))
        assert isinstance(str_num_bool, CtyTuple)
        assert len(str_num_bool.element_types) == 3
        assert isinstance(str_num_bool.element_types[0], CtyString)
        assert isinstance(str_num_bool.element_types[1], CtyNumber)
        assert isinstance(str_num_bool.element_types[2], CtyBool)

    @pytest.mark.asyncio
    async def test_tuple_type_initialization_empty(self) -> None:
        """Test initialization of an empty tuple type."""
        empty_tuple = CtyTuple(element_types=())
        assert isinstance(empty_tuple, CtyTuple)
        assert len(empty_tuple.element_types) == 0

    @pytest.mark.asyncio
    async def test_tuple_type_initialization_complex(self) -> None:
        """Test initialization with nested collection and structural types."""
        list_type = CtyList(element_type=CtyString())
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        obj_type = CtyObject(attribute_types={"attr": CtyBool()})
        nested_tuple = CtyTuple(element_types=(CtyString(), list_type))

        complex_tuple = CtyTuple(
            element_types=(list_type, map_type, obj_type, nested_tuple, CtyDynamic())
        )

        assert isinstance(complex_tuple, CtyTuple)
        assert len(complex_tuple.element_types) == 5
        assert complex_tuple.element_types[0] is list_type
        assert complex_tuple.element_types[1] is map_type
        assert complex_tuple.element_types[2] is obj_type
        assert isinstance(complex_tuple.element_types[3], CtyTuple)
        assert isinstance(complex_tuple.element_types[4], CtyDynamic)

    @pytest.mark.asyncio
    async def test_tuple_type_init_invalid_element_types_type(self) -> None:
        """Test initialization fails if element_types is not a tuple."""
        with pytest.raises(CtyTupleValidationError) as exc_info:
            CtyTuple(
                element_types=[CtyString(), CtyNumber()]
            )  # Pass list instead of tuple
        assert "element_types must be a tuple" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_tuple_type_init_invalid_element_type_item(self) -> None:
        """Test initialization fails if an element type is not a CtyType."""
        with pytest.raises(
            CtyTupleValidationError,
            match=r"Element type at index 1 must be a CtyType, got type",
        ):
            CtyTuple(element_types=(CtyString(), int, CtyBool()))  # Pass 'int' type
        # No need to assert exc_info.value outside the block if match is used.

        with pytest.raises(
            CtyTupleValidationError,
            match=r"Element type at index 1 must be a CtyType, got str",
        ):
            CtyTuple(element_types=(CtyString(), "not a type"))  # Pass string
        # If we need to assert specific parts beyond regex, keep it inside or use the caught exception:
        # assert "Element type at index 1 must be a CtyType, got str" in str(exc_info_str.value)
        # For now, the match argument should suffice.

    @pytest.mark.asyncio
    async def test_tuple_type_string_representation(self) -> None:
        """Test __str__ and __repr__ methods."""
        simple_tuple = CtyTuple(element_types=(CtyString(), CtyNumber()))
        empty_tuple = CtyTuple(element_types=())

        # __str__
        assert (
            str(simple_tuple) == "tuple(string, number)"
        )  # Expecting simplified primitive type names
        assert str(empty_tuple) == "tuple()"

        # __repr__
        # Default value for CtyString is '', for CtyNumber is 0.
        assert (
            repr(simple_tuple)
            == "CtyTuple(element_types=(CtyString(value=''), CtyNumber(value=0)))"
        )
        assert repr(empty_tuple) == "CtyTuple(element_types=())"
