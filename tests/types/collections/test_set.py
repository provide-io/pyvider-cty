import pytest

from pyvider.cty.exceptions import CtySetValidationError
from pyvider.cty.types import (
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtySet,
    CtyString,
)
from pyvider.cty.values import CtyValue


class TestCtySetInstantiation:
    def test_instantiation_valid_element_type(self) -> None:
        """Test successful instantiation with a valid CtyType."""
        s = CtySet(element_type=CtyString())
        assert isinstance(s.element_type, CtyString)

    @pytest.mark.parametrize("invalid_type", ["foo", int, 123])
    def test_instantiation_invalid_element_type_raises_error(self, invalid_type) -> None:
        """Test CtySet raises CtySetValidationError for invalid element_type."""
        with pytest.raises(CtySetValidationError, match="Expected CtyType for element_type"):
            CtySet(element_type=invalid_type)

class TestCtySetValidate:
    def test_validate_exact_same_set_type_value(self) -> None:
        """Test validating a CtyValue of the exact same CtySet type."""
        set_type = CtySet(element_type=CtyString())
        initial_value = set_type.validate(frozenset({"a", "b"}))

        validated_value = set_type.validate(initial_value)
        assert validated_value == initial_value

    def test_validate_unknown_compatible_ctyvalue(self) -> None:
        """Test validating an unknown CtyValue of a compatible CtySet type."""
        set_type = CtySet(element_type=CtyString())
        compatible_unknown_value = CtyValue.unknown(CtySet(element_type=CtyString()))

        validated_value = set_type.validate(compatible_unknown_value)
        assert validated_value.is_unknown
        assert validated_value.type == set_type

    def test_validate_list_input_with_unhashable_elements_dynamic(self) -> None:
        """Test validating a list with unhashable items for CtySet(CtyDynamic)."""
        set_type = CtySet(element_type=CtyDynamic())
        unhashable_input = [1, "two", {"three": 3}]
        with pytest.raises(CtySetValidationError, match="Input list/tuple could not be converted to set"):
            set_type.validate(unhashable_input)

    def test_validate_set_with_mixed_validity_elements(self) -> None:
        """Test validating a set with some elements valid and some invalid."""
        set_type = CtySet(element_type=CtyNumber())
        mixed_validity_input = {10, "twenty"} # Valid number, invalid string for CtyNumber
        with pytest.raises(CtySetValidationError) as excinfo:
            set_type.validate(mixed_validity_input)

        assert "Set validation failed:" in str(excinfo.value)
        # Check if the specific error for "twenty" is present (order in set is not guaranteed for idx)
        assert "Number validation error: Cannot convert string 'twenty' to number" in str(excinfo.value)


class TestCtySetOperations:
    def test_add_invalid_element_raises_error(self) -> None:
        """Test add() raises CtySetValidationError if element_type.validate fails."""
        set_type = CtySet(element_type=CtyNumber())
        with pytest.raises(CtySetValidationError, match="Failed to add element: Number validation error: Cannot convert string 'not a number' to number"):
            set_type.add("not a number")

    def test_remove_invalid_item_raises_error(self) -> None:
        """Test remove() raises CtySetValidationError if item validation fails."""
        set_type = CtySet(element_type=CtyNumber())
        with pytest.raises(CtySetValidationError, match="Failed to remove item: Number validation error: Cannot convert string 'not a number' to number"):
            set_type.remove("not a number")

    # Removed tests for remove_item_not_in_set and remove_item_in_set
    # as CtySet.remove operates on the type's default value, not instance data held by CtyValue.
    # These tests would require CtyValue to have set manipulation methods.

class TestCtySetEqualityAndTypeChecks:
    def test_equal_with_non_set_type(self) -> None:
        """Test CtySet.equal() with a non-set type (e.g., CtyList)."""
        set_type = CtySet(element_type=CtyString())
        list_type = CtyList(element_type=CtyString())
        assert not set_type.equal(list_type)

    def test_equal_with_different_element_types(self) -> None:
        """Test CtySet.equal() with another CtySet of different element_type."""
        set_type_str = CtySet(element_type=CtyString())
        set_type_num = CtySet(element_type=CtyNumber())
        assert not set_type_str.equal(set_type_num)

    def test_equal_with_same_element_types(self) -> None:
        """Test CtySet.equal() with another CtySet of the same element_type."""
        set_type1 = CtySet(element_type=CtyString())
        set_type2 = CtySet(element_type=CtyString())
        assert set_type1.equal(set_type2)

    def test_is_collection_type(self) -> None:
        """Test is_collection_type() returns True."""
        set_type = CtySet(element_type=CtyString())
        assert set_type.is_collection_type()

    def test_is_set_type(self) -> None:
        """Test is_set_type() returns True."""
        set_type = CtySet(element_type=CtyString())
        assert set_type.is_set_type()

    def test_is_primitive_type(self) -> None:
        """Test is_primitive_type() returns False."""
        set_type = CtySet(element_type=CtyString())
        assert not set_type.is_primitive_type()
