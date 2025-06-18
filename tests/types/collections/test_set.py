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
    def test_instantiation_invalid_element_type_raises_error(
        self, invalid_type
    ) -> None:
        """Test CtySet raises CtySetValidationError for invalid element_type."""
        with pytest.raises(
            CtySetValidationError, match="Expected CtyType for element_type"
        ):
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
        with pytest.raises(
            CtySetValidationError,
            match="Input list/tuple could not be converted to set",
        ):
            set_type.validate(unhashable_input)

    def test_validate_set_with_mixed_validity_elements(self) -> None:
        """Test validating a set with some elements valid and some invalid."""
        set_type = CtySet(element_type=CtyNumber())
        mixed_validity_input = {
            10,
            "twenty",
        }  # Valid number, invalid string for CtyNumber
        with pytest.raises(CtySetValidationError) as excinfo:
            set_type.validate(mixed_validity_input)

        assert "Set validation failed:" in str(excinfo.value)
        # Check if the specific error for "twenty" is present (order in set is not guaranteed for idx)
        assert (
            "Number validation error: Cannot convert string 'twenty' to number"
            in str(excinfo.value)
        )


class TestCtySetOperations:
    def test_add_invalid_element_raises_error(self) -> None:
        """Test add() raises CtySetValidationError if element_type.validate fails."""
        set_type = CtySet(element_type=CtyNumber())
        with pytest.raises(
            CtySetValidationError,
            match="Failed to add element: Number validation error: Cannot convert string 'not a number' to number",
        ):
            set_type.add("not a number")

    def test_remove_invalid_item_raises_error(self) -> None:
        """Test remove() raises CtySetValidationError if item validation fails."""
        set_type = CtySet(element_type=CtyNumber())
        with pytest.raises(
            CtySetValidationError,
            match="Failed to remove item: Number validation error: Cannot convert string 'not a number' to number",
        ):
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


class TestCtySetUnionOperation:
    def test_union_basic(self) -> None:
        """Test basic union operation."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1 = CtyValue.make_set(str_type, {"a", "b"})
        set_val2 = CtyValue.make_set(str_type, {"b", "c"})

        expected_result_val = CtyValue.make_set(str_type, {"a", "b", "c"})

        result_val = set_val1.union(set_val2)
        assert not result_val.is_unknown
        assert not result_val.is_null
        assert result_val.type.equal(set_type)
        # Ensure internal values are frozensets of CtyValues for comparison
        assert result_val.value == expected_result_val.value

    def test_union_with_empty_set(self) -> None:
        """Test union with an empty set."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1 = CtyValue.make_set(str_type, {"a", "b"})
        empty_set_val = CtyValue.make_set(str_type, set())

        result_val1 = set_val1.union(empty_set_val)
        assert result_val1.value == set_val1.value

        result_val2 = empty_set_val.union(set_val1)
        assert result_val2.value == set_val1.value

    def test_union_with_null_set(self) -> None:
        """Test union with a null set."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val = CtyValue.make_set(str_type, {"a", "b"})
        null_set_val = CtyValue.null(set_type)

        result_val1 = set_val.union(null_set_val)
        assert result_val1.value == set_val.value

        result_val2 = null_set_val.union(set_val)
        assert result_val2.value == set_val.value

        # Union of two null sets should be a null set
        null_set_val2 = CtyValue.null(set_type)
        result_val3 = null_set_val.union(null_set_val2)
        assert result_val3.is_null

    def test_union_with_unknown_set(self) -> None:
        """Test union with an unknown set."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val = CtyValue.make_set(str_type, {"a", "b"})
        unknown_set_val = CtyValue.unknown(set_type)

        result_val1 = set_val.union(unknown_set_val)
        assert result_val1.is_unknown

        result_val2 = unknown_set_val.union(set_val)
        assert result_val2.is_unknown

    def test_union_incompatible_element_types_raises_error(self) -> None:
        """Test union of sets with incompatible element types raises CtySetValidationError."""
        set_type_str = CtySet(element_type=CtyString())
        set_val_str = CtyValue(vtype=set_type_str, value=frozenset({CtyValue.string("a")}))

        set_type_num = CtySet(element_type=CtyNumber())
        set_val_num = CtyValue(vtype=set_type_num, value=frozenset({CtyValue.number(1)}))

        with pytest.raises(CtySetValidationError, match="Cannot perform union with incompatible set type"):
            set_val_str.union(set_val_num)

    def test_union_non_set_type_raises_type_error(self) -> None:
        """Test union with a non-set type raises TypeError."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)
        set_val = CtyValue.make_set(str_type, {"a"})

        list_type = CtyList(element_type=str_type)
        list_val = CtyValue.list(str_type, ["b"])

        with pytest.raises(TypeError, match="Other operand for union must also be a CtySet value."):
            set_val.union(list_val)

        # And the other way around
        with pytest.raises(TypeError, match="Union operation is only valid for CtySet values."):
            list_val.union(set_val)

    def test_union_preserves_marks_of_operands(self) -> None:
        """Test that union operation correctly handles marks (it should not merge/preserve them based on current CtySet.union)."""
        # The CtySet.union method as implemented returns a new CtyValue without specific mark handling.
        # The marks on the operands are not automatically transferred or combined.
        # The CtyValue.union method simply calls the CtySet's method.
        # If mark propagation is desired, it needs to be implemented in CtySet.union or CtyValue.union.

        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1_unmarked = CtyValue.make_set(str_type, {"a", "b"})
        set_val1_marked = set_val1_unmarked.mark("mark1")

        set_val2_unmarked = CtyValue.make_set(str_type, {"b", "c"})
        set_val2_marked = set_val2_unmarked.mark("mark2")

        # Union of two marked sets
        result_marked_marked = set_val1_marked.union(set_val2_marked)
        # According to current CtySet.union, the result is a new CtyValue based on the *type* of the first operand.
        # The CtyValue constructor itself doesn't inherit marks unless explicitly passed.
        # The CtySet.union creates a new CtyValue(vtype=self, value=unioned_items)
        # This means the resulting CtyValue will NOT have marks from set_val1_marked or set_val2_marked.
        assert not result_marked_marked._marks, "Resulting set should not have marks from operands by default"

        # Union of marked and unmarked
        result_marked_unmarked = set_val1_marked.union(set_val2_unmarked)
        assert not result_marked_unmarked._marks, "Resulting set should not have marks from operands by default"

        result_unmarked_marked = set_val1_unmarked.union(set_val2_marked)
        assert not result_unmarked_marked._marks, "Resulting set should not have marks from operands by default"


class TestCtySetIntersectionOperation:
    def test_intersection_basic(self) -> None:
        """Test basic intersection operation."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1 = CtyValue.make_set(str_type, {"a", "b", "c"})
        set_val2 = CtyValue.make_set(str_type, {"b", "c", "d"})

        expected_result_val = CtyValue.make_set(str_type, {"b", "c"})

        result_val = set_val1.intersection(set_val2)
        assert not result_val.is_unknown
        assert not result_val.is_null
        assert result_val.type.equal(set_type)
        assert result_val.value == expected_result_val.value

    def test_intersection_no_common_elements(self) -> None:
        """Test intersection when there are no common elements."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1 = CtyValue.make_set(str_type, {"a", "b"})
        set_val2 = CtyValue.make_set(str_type, {"c", "d"})

        expected_empty_set_val = CtyValue.make_set(str_type, set())

        result_val = set_val1.intersection(set_val2)
        assert not result_val.is_unknown
        assert not result_val.is_null # Should be an empty set, not null
        assert result_val.type.equal(set_type)
        assert result_val.value == expected_empty_set_val.value
        assert len(result_val.value) == 0


    def test_intersection_with_empty_set(self) -> None:
        """Test intersection with an empty set."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1 = CtyValue.make_set(str_type, {"a", "b"})
        empty_set_val = CtyValue.make_set(str_type, set())

        expected_empty_set_val = CtyValue.make_set(str_type, set())

        result_val1 = set_val1.intersection(empty_set_val)
        assert result_val1.value == expected_empty_set_val.value

        result_val2 = empty_set_val.intersection(set_val1)
        assert result_val2.value == expected_empty_set_val.value

    def test_intersection_with_null_set(self) -> None:
        """Test intersection with a null set."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val = CtyValue.make_set(str_type, {"a", "b"})
        null_set_val = CtyValue.null(set_type)

        expected_empty_set_val = CtyValue.make_set(str_type, set())

        # Intersection with null results in an empty set (not null)
        result_val1 = set_val.intersection(null_set_val)
        assert not result_val1.is_unknown
        assert not result_val1.is_null
        assert result_val1.type.equal(set_type)
        assert result_val1.value == expected_empty_set_val.value

        result_val2 = null_set_val.intersection(set_val)
        assert not result_val2.is_unknown
        assert not result_val2.is_null
        assert result_val2.type.equal(set_type)
        assert result_val2.value == expected_empty_set_val.value

        # Intersection of two null sets should be a null set
        null_set_val2 = CtyValue.null(set_type)
        result_val3 = null_set_val.intersection(null_set_val2)
        assert result_val3.is_null


    def test_intersection_with_unknown_set(self) -> None:
        """Test intersection with an unknown set."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val = CtyValue.make_set(str_type, {"a", "b"})
        unknown_set_val = CtyValue.unknown(set_type)

        result_val1 = set_val.intersection(unknown_set_val)
        assert result_val1.is_unknown

        result_val2 = unknown_set_val.intersection(set_val)
        assert result_val2.is_unknown

    def test_intersection_incompatible_element_types_raises_error(self) -> None:
        """Test intersection of sets with incompatible element types raises CtySetValidationError."""
        set_type_str = CtySet(element_type=CtyString())
        set_val_str = CtyValue(vtype=set_type_str, value=frozenset({CtyValue.string("a")}))

        set_type_num = CtySet(element_type=CtyNumber())
        set_val_num = CtyValue(vtype=set_type_num, value=frozenset({CtyValue.number(1)}))

        with pytest.raises(CtySetValidationError, match="Cannot perform intersection with incompatible set type"):
            set_val_str.intersection(set_val_num)

    def test_intersection_non_set_type_raises_type_error(self) -> None:
        """Test intersection with a non-set type raises TypeError."""
        str_type = CtyString()
        # set_type = CtySet(element_type=str_type) # Not used directly
        set_val = CtyValue.make_set(str_type, {"a"})

        list_type = CtyList(element_type=str_type)
        list_val = CtyValue.list(str_type, ["b"])

        with pytest.raises(TypeError, match="Other operand for intersection must also be a CtySet value."):
            set_val.intersection(list_val)

        with pytest.raises(TypeError, match="Intersection operation is only valid for CtySet values."):
            list_val.intersection(set_val)

    def test_intersection_marks_handling(self) -> None:
        """Test marks handling for intersection (should not be inherited)."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1_unmarked = CtyValue.make_set(str_type, {"a", "b"})
        set_val1_marked = set_val1_unmarked.mark("mark1")

        set_val2_unmarked = CtyValue.make_set(str_type, {"b", "c"})
        set_val2_marked = set_val2_unmarked.mark("mark2")

        result = set_val1_marked.intersection(set_val2_marked)
        assert not result._marks, "Resulting set from intersection should not have marks from operands by default"


class TestCtySetDifferenceOperation:
    def test_difference_basic(self) -> None:
        """Test basic difference operation (set1 - set2)."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1 = CtyValue.make_set(str_type, {"a", "b", "c"})
        set_val2 = CtyValue.make_set(str_type, {"b", "c", "d"})

        expected_result_val = CtyValue.make_set(str_type, {"a"})

        result_val = set_val1.difference(set_val2)
        assert not result_val.is_unknown
        assert not result_val.is_null
        assert result_val.type.equal(set_type)
        assert result_val.value == expected_result_val.value

    def test_difference_no_common_elements(self) -> None:
        """Test difference when there are no common elements (set1 - set2 = set1)."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1 = CtyValue.make_set(str_type, {"a", "b"})
        set_val2 = CtyValue.make_set(str_type, {"c", "d"})

        result_val = set_val1.difference(set_val2)
        assert not result_val.is_unknown
        assert not result_val.is_null
        assert result_val.type.equal(set_type)
        assert result_val.value == set_val1.value # Should be equal to set_val1

    def test_difference_all_common_elements(self) -> None:
        """Test difference when all elements are common (set1 - set2 = empty_set)."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1 = CtyValue.make_set(str_type, {"a", "b"})
        set_val2 = CtyValue.make_set(str_type, {"a", "b", "c"})

        expected_empty_set_val = CtyValue.make_set(str_type, set())

        result_val = set_val1.difference(set_val2)
        assert not result_val.is_unknown
        assert not result_val.is_null
        assert result_val.type.equal(set_type)
        assert result_val.value == expected_empty_set_val.value
        assert len(result_val.value) == 0

    def test_difference_with_empty_set(self) -> None:
        """Test difference with an empty set."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val1 = CtyValue.make_set(str_type, {"a", "b"})
        empty_set_val = CtyValue.make_set(str_type, set())

        # set1 - empty_set = set1
        result_val1 = set_val1.difference(empty_set_val)
        assert result_val1.value == set_val1.value

        # empty_set - set1 = empty_set
        expected_empty_set_val = CtyValue.make_set(str_type, set())
        result_val2 = empty_set_val.difference(set_val1)
        assert result_val2.value == expected_empty_set_val.value


    def test_difference_with_null_set(self) -> None:
        """Test difference with a null set."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val = CtyValue.make_set(str_type, {"a", "b"})
        null_set_val = CtyValue.null(set_type)

        # set_val - null_set_val = set_val
        result_val1 = set_val.difference(null_set_val)
        assert not result_val1.is_unknown
        assert not result_val1.is_null
        assert result_val1.type.equal(set_type)
        assert result_val1.value == set_val.value

        # null_set_val - set_val = null_set_val
        result_val2 = null_set_val.difference(set_val)
        assert result_val2.is_null # null - anything = null

        # null_set_val - null_set_val_other = null_set_val
        null_set_val_other = CtyValue.null(set_type)
        result_val3 = null_set_val.difference(null_set_val_other)
        assert result_val3.is_null


    def test_difference_with_unknown_set(self) -> None:
        """Test difference with an unknown set."""
        str_type = CtyString()
        set_type = CtySet(element_type=str_type)

        set_val = CtyValue.make_set(str_type, {"a", "b"})
        unknown_set_val = CtyValue.unknown(set_type)

        result_val1 = set_val.difference(unknown_set_val)
        assert result_val1.is_unknown

        result_val2 = unknown_set_val.difference(set_val)
        assert result_val2.is_unknown

    def test_difference_incompatible_element_types_raises_error(self) -> None:
        """Test difference of sets with incompatible element types raises CtySetValidationError."""
        set_type_str = CtySet(element_type=CtyString())
        set_val_str = CtyValue(vtype=set_type_str, value=frozenset({CtyValue.string("a")}))

        set_type_num = CtySet(element_type=CtyNumber())
        set_val_num = CtyValue(vtype=set_type_num, value=frozenset({CtyValue.number(1)}))

        with pytest.raises(CtySetValidationError, match="Cannot perform difference with incompatible set type"):
            set_val_str.difference(set_val_num)

    def test_difference_non_set_type_raises_type_error(self) -> None:
        """Test difference with a non-set type raises TypeError."""
        str_type = CtyString()
        set_val = CtyValue.make_set(str_type, {"a"})

        list_type = CtyList(element_type=str_type)
        list_val = CtyValue.list(str_type, ["b"])

        with pytest.raises(TypeError, match="Other operand for difference must also be a CtySet value."):
            set_val.difference(list_val)

        with pytest.raises(TypeError, match="Difference operation is only valid for CtySet values."):
            list_val.difference(set_val)

    def test_difference_marks_handling(self) -> None:
        """Test marks handling for difference (should not be inherited)."""
        str_type = CtyString()
        # set_type = CtySet(element_type=str_type) # Not used

        set_val1_unmarked = CtyValue.make_set(str_type, {"a", "b"})
        set_val1_marked = set_val1_unmarked.mark("mark1")

        set_val2_unmarked = CtyValue.make_set(str_type, {"b", "c"})
        set_val2_marked = set_val2_unmarked.mark("mark2")

        result = set_val1_marked.difference(set_val2_marked)
        assert not result._marks, "Resulting set from difference should not have marks from operands by default"
