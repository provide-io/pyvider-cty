# tests/tuple/test_cty_tuple_comparison.py

"""
Tests for CtyTuple type comparison (equal, usable_as) and CtyValue equality.
"""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyString,
    CtyTuple,
    CtyValue,
)


class TestCtyTupleComparison:
    """Tests CtyTuple type comparison and CtyValue instance equality."""

    # --- Type Comparison (equal, usable_as) ---

    @pytest.mark.asyncio
    async def test_type_equal_identical(self) -> None:
        """Test CtyTuple.equal for identical types."""
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t2 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        assert t1.equal(t2)
        assert t2.equal(t1)
        assert t1 == t2  # Test __eq__

    @pytest.mark.asyncio
    async def test_type_equal_different_length(self) -> None:
        """Test CtyTuple.equal for types with different lengths."""
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t2 = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))
        t3 = CtyTuple(element_types=(CtyString(),))
        assert not t1.equal(t2)
        assert not t2.equal(t1)
        assert not t1.equal(t3)
        assert not t3.equal(t1)
        assert t1 != t2  # Test __eq__

    @pytest.mark.asyncio
    async def test_type_equal_different_element_types(self) -> None:
        """Test CtyTuple.equal for types with different element types."""
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t2 = CtyTuple(element_types=(CtyString(), CtyString()))  # Second type differs
        t3 = CtyTuple(element_types=(CtyNumber(), CtyNumber()))  # First type differs
        assert not t1.equal(t2)
        assert not t2.equal(t1)
        assert not t1.equal(t3)
        assert not t3.equal(t1)
        assert t1 != t2

    @pytest.mark.asyncio
    async def test_type_equal_different_type_class(self) -> None:
        """Test CtyTuple.equal against other CtyType classes."""
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t_list = CtyList(element_type=CtyString())
        t_string = CtyString()
        assert not t1.equal(t_list)
        assert not t1.equal(t_string)
        assert t1 != t_list

    @pytest.mark.asyncio
    async def test_type_usable_as_identical(self) -> None:
        """Test CtyTuple.usable_as for identical types."""
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t2 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        assert t1.usable_as(t2)
        assert t2.usable_as(t1)

    @pytest.mark.asyncio
    async def test_type_usable_as_different_length(self) -> None:
        """Test CtyTuple.usable_as fails for different lengths."""
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t2 = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))
        assert not t1.usable_as(t2)
        assert not t2.usable_as(t1)

    @pytest.mark.asyncio
    async def test_type_usable_as_compatible_elements(self) -> None:
        """Test CtyTuple.usable_as with compatible element types (e.g., dynamic)."""
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t2_dynamic = CtyTuple(element_types=(CtyDynamic(), CtyDynamic()))
        t3_specific = CtyTuple(element_types=(CtyString(), CtyDynamic()))

        # A specific tuple can be used where dynamic is expected
        assert t1.usable_as(t2_dynamic)
        assert t1.usable_as(t3_specific)

        # A dynamic tuple cannot be used where a specific type is needed
        assert not t2_dynamic.usable_as(t1)
        assert not t3_specific.usable_as(t1)

    @pytest.mark.asyncio
    async def test_type_usable_as_incompatible_elements(self) -> None:
        """Test CtyTuple.usable_as fails with incompatible element types."""
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t2 = CtyTuple(
            element_types=(CtyString(), CtyBool())
        )  # Number not usable as Bool
        assert not t1.usable_as(t2)
        assert not t2.usable_as(t1)

    @pytest.mark.asyncio
    async def test_type_usable_as_different_type_class(self) -> None:
        """Test CtyTuple.usable_as against other CtyType classes."""
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t_list = CtyList(element_type=CtyString())
        assert not t1.usable_as(t_list)

    # --- CtyValue Instance Equality ---

    @pytest.mark.asyncio
    async def test_value_equality_equal_content(self) -> None:
        """Test equality of CtyValue tuples with the same content."""
        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber()))
        v1 = tuple_type.validate(("test", 10))
        v2 = tuple_type.validate(("test", 10))
        assert isinstance(v1, CtyValue)
        assert isinstance(v2, CtyValue)
        assert v1 == v2
        assert hash(v1) == hash(v2)  # Check hash consistency

    @pytest.mark.asyncio
    async def test_value_equality_different_content(self) -> None:
        """Test inequality of CtyValue tuples with different content."""
        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber()))
        v1 = tuple_type.validate(("test", 10))
        v2 = tuple_type.validate(("test", 20))  # Different number
        v3 = tuple_type.validate(("other", 10))  # Different string
        assert v1 != v2
        assert v1 != v3

    @pytest.mark.asyncio
    async def test_value_equality_different_types(self) -> None:
        """Test inequality of CtyValue tuples with different types."""
        tuple_type1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        tuple_type2 = CtyTuple(element_types=(CtyString(), CtyString()))
        v1 = tuple_type1.validate(("test", 10))
        v2 = tuple_type2.validate(("test", "10"))  # Same logical value, different type
        assert v1 != v2

    @pytest.mark.asyncio
    async def test_value_equality_special_values(self) -> None:
        """Test equality involving null and unknown values."""
        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber()))
        v_known = tuple_type.validate(("test", 10))
        v_null1 = CtyValue.null(tuple_type)
        v_null2 = CtyValue.null(tuple_type)
        v_unknown1 = CtyValue.unknown(tuple_type)
        v_unknown2 = CtyValue.unknown(tuple_type)

        assert v_null1 == v_null2
        assert v_unknown1 == v_unknown2
        assert v_known != v_null1
        assert v_known != v_unknown1
        assert v_null1 != v_unknown1

    @pytest.mark.asyncio
    async def test_value_equality_with_marks(self) -> None:
        """Test equality considers marks."""
        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber()))
        v1 = tuple_type.validate(("test", 10))
        v2 = tuple_type.validate(("test", 10))
        v1_marked = v1.mark("mark1")
        v2_marked = v2.mark("mark2")
        v2_marked_same = v2.mark("mark1")

        assert v1 == v2
        assert v1 != v1_marked  # Different marks
        assert v1_marked != v2_marked  # Different marks
        assert v1_marked == v2_marked_same  # Same marks
