from typing import Any

import pytest

from pyvider.cty.exceptions import CtyListValidationError  # Removed CtyDatatypeError
from pyvider.cty.types.collections.list import CtyList
from pyvider.cty.types.primitives.number import CtyNumber
from pyvider.cty.types.primitives.string import CtyString
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.values import CtyValue  # Actual import


# Fixtures
@pytest.fixture
def string_list_type() -> CtyList[str]:
    return CtyList(element_type=CtyString())


@pytest.fixture
def number_list_type() -> CtyList[float]:  # Assuming float for CtyNumber underlying
    return CtyList(element_type=CtyNumber())


@pytest.fixture
def dynamic_list_type() -> CtyList[Any]:
    return CtyList(element_type=CtyDynamic())


class TestCtyListAttrsPostInit:
    def test_attrs_post_init_invalid_element_type(self) -> None:
        """Test __attrs_post_init__ raises error for invalid element_type."""
        with pytest.raises(
            CtyListValidationError, match="Expected CtyType for element_type, got int"
        ):
            CtyList(element_type=123)  # type: ignore


class TestCtyListValidate:
    def test_validate_none_input(self, string_list_type: CtyList[str]) -> None:
        """Test validate raises error for None input."""
        with pytest.raises(
            CtyListValidationError, match="Expected list or tuple, got NoneType"
        ):
            string_list_type.validate(None)

    def test_validate_invalid_container_type(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test validate raises error for non-list/tuple input."""
        with pytest.raises(
            CtyListValidationError, match="Expected list or tuple, got int"
        ):
            string_list_type.validate(123)

    def test_validate_empty_list_input(self, string_list_type: CtyList[str]) -> None:
        """Test validate with an empty list input."""
        cty_val = string_list_type.validate([])
        assert isinstance(cty_val, CtyValue)
        assert cty_val.type == string_list_type
        assert cty_val.value == []

    def test_validate_list_with_none_element(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test validate raises error for list containing None."""
        # The error message includes the nested CtyListValidationError message.
        # We need to match the overall structure.
        with pytest.raises(
            CtyListValidationError,
            match=r"Item 0: None -> .*None is not a valid list element",
        ):
            string_list_type.validate([None])  # type: ignore

    def test_validate_list_with_pre_validated_correct_type_elements(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test validate with list of CtyValue elements of the correct type."""
        pre_validated_element = CtyString().validate("hello")
        cty_val = string_list_type.validate([pre_validated_element, "world"])
        assert isinstance(cty_val, CtyValue)
        assert len(cty_val.value) == 2
        assert cty_val.value[0] == pre_validated_element
        assert cty_val.value[1].value == "world"
        assert cty_val.value[1].type == CtyString()

    def test_validate_list_with_mixed_elements_validation_failure(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test validate with mixed elements where one fails validation."""
        with pytest.raises(CtyListValidationError) as excinfo:
            string_list_type.validate(["valid", 123, "another_valid"])
        # Check that the error message contains info about the failed item
        # The exact message from CtyString().validate(123) might be like "Not a valid CtyString: 123"
        # or "Value 123 is not a valid string."
        # For now, let's be a bit general for the nested error part.
        assert "Item 1: 123 ->" in str(excinfo.value)
        assert "String validation error: Value must be a string" in str(excinfo.value)

    def test_validate_successful_list(self, number_list_type: CtyList[float]) -> None:
        """Test successful validation of a list of numbers."""
        cty_val = number_list_type.validate([1, 2.5, CtyNumber().validate(3)])
        assert isinstance(cty_val, CtyValue)
        assert len(cty_val.value) == 3
        assert cty_val.value[0].value == 1
        assert cty_val.value[1].value == 2.5
        assert cty_val.value[2].value == 3


class TestCtyListElementAt:
    def test_element_at_ctyvalue_container_invalid_type(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test element_at with CtyValue container of wrong CtyType."""
        # Create a CtyValue holding a CtyNumber, not a CtyList
        number_value = CtyNumber().validate(123)
        with pytest.raises(
            CtyListValidationError,
            match="Expected CtyValue with CtyList type, got CtyValue with CtyNumber",
        ):
            string_list_type.element_at(number_value, 0)

    def test_element_at_ctyvalue_container_valid_type(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test element_at with CtyValue container of correct CtyList type."""
        list_val = string_list_type.validate(["a", "b"])
        element = string_list_type.element_at(list_val, 1)
        assert element.value == "b"

    def test_element_at_ctylist_container(self, string_list_type: CtyList[str]) -> None:
        """Test element_at with CtyList instance as container."""
        # Note: CtyList instances usually don't hold CtyValues directly in their .value
        # This test relies on the internal structure or might need adjustment
        # For now, let's assume CtyList can be constructed with CtyValues for this test path
        val_a = CtyString().validate("a")
        val_b = CtyString().validate("b")
        list_instance_with_values = CtyList(
            element_type=CtyString(), value=[val_a, val_b]
        )  # type: ignore

        element = list_instance_with_values.element_at(list_instance_with_values, 0)
        assert element == val_a  # Direct CtyValue comparison

    def test_element_at_raw_list_container(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test element_at with raw list as container (elements are CtyValues)."""
        raw_list = [CtyString().validate("x"), CtyString().validate("y")]
        element = string_list_type.element_at(raw_list, 1)
        assert element.value == "y"

    def test_element_at_invalid_container(self, string_list_type: CtyList[str]) -> None:
        """Test element_at with an invalid container type (e.g., int)."""
        with pytest.raises(
            CtyListValidationError,
            match="Expected list, tuple, CtyList, or CtyValue with CtyList type, got int",
        ):
            string_list_type.element_at(123, 0)

    def test_element_at_index_out_of_bounds_positive(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test element_at with positive index out of bounds."""
        list_val = string_list_type.validate(["a"])
        with pytest.raises(IndexError, match=r"List index 1 out of bounds \(size 1\)"):
            string_list_type.element_at(list_val, 1)

    def test_element_at_index_out_of_bounds_negative(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test element_at with negative index out of bounds."""
        list_val = string_list_type.validate(["a"])
        with pytest.raises(IndexError, match=r"List index -2 out of bounds \(size 1\)"):
            string_list_type.element_at(list_val, -2)

    def test_element_at_successful_negative_index(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test element_at with a successful negative index."""
        list_val = string_list_type.validate(["a", "b", "c"])
        element = string_list_type.element_at(list_val, -1)
        assert element.value == "c"
        element_first = string_list_type.element_at(list_val, -3)
        assert element_first.value == "a"


# Placeholder for CtyValue and CtyDatatypeError if not already available globally
# from pyvider.cty.values import CtyValue
# class CtyDatatypeError(Exception): pass


# More tests for append, slice, concat, contains, usable_as, equal, __getitem__, __str__, __repr__ will follow.
# Focusing on the first few methods for now.


class TestCtyListAppend:
    def test_append_successful(self, string_list_type: CtyList[str]) -> None:
        """Test successful append operation."""
        string_list_type.validate(["a", "b"])
        # To use append, we need a CtyList instance that holds the CtyValue elements,
        # not just the type definition.
        # The CtyList type itself is a blueprint. Operations like append are on instances
        # that represent actual lists.
        # Let's create a CtyList *instance* from the validated value.
        # The `validate` method returns a CtyValue, not a CtyList instance directly.
        # This highlights a potential confusion in how these types vs. values are handled.
        # CtyList.append is a method of the CtyList *type* definition, not a CtyValue.
        # This suggests CtyList might need to be instantiated with its value to use append.

        # The current CtyList structure:
        # CtyList(element_type=X, value=[...]) where value contains CtyValues.
        # Let's assume we have an instance of CtyList representing an actual list.
        val_a = CtyString().validate("a")
        val_b = CtyString().validate("b")
        list_instance = CtyList(element_type=CtyString(), value=[val_a, val_b])  # type: ignore

        appended_list = list_instance.append("c")
        assert len(appended_list.value) == 3
        assert appended_list.value[2].value == "c"
        assert appended_list.element_type == string_list_type.element_type
        # Ensure original is unchanged
        assert len(list_instance.value) == 2

    def test_append_validation_failure(self, string_list_type: CtyList[str]) -> None:
        """Test append raises error if item validation fails."""
        val_a = CtyString().validate("a")
        list_instance = CtyList(element_type=CtyString(), value=[val_a])  # type: ignore

        with pytest.raises(
            CtyListValidationError,
            match="Failed to append item: String validation error: Value must be a string, got int",
        ):
            list_instance.append(123)  # type: ignore


class TestCtyListSlice:
    def test_slice_basic(self, number_list_type: CtyList[float]) -> None:
        """Test basic slice operation."""
        val1, val2, val3, val4 = (
            CtyNumber().validate(1),
            CtyNumber().validate(2),
            CtyNumber().validate(3),
            CtyNumber().validate(4),
        )
        list_instance = CtyList(
            element_type=CtyNumber(), value=[val1, val2, val3, val4]
        )  # type: ignore

        sliced = list_instance.slice(1, 3)
        assert len(sliced.value) == 2
        assert sliced.value[0].value == 2
        assert sliced.value[1].value == 3
        assert sliced.element_type == number_list_type.element_type

    def test_slice_negative_indices(self, string_list_type: CtyList[str]) -> None:
        """Test slice with negative indices."""

        def s_val(s):
            return CtyString().validate(s)

        list_instance = CtyList(
            element_type=CtyString(),
            value=[s_val("a"), s_val("b"), s_val("c"), s_val("d")],
        )  # type: ignore

        sliced = list_instance.slice(-3, -1)
        assert len(sliced.value) == 2
        assert sliced.value[0].value == "b"
        assert sliced.value[1].value == "c"

    def test_slice_to_end(self, string_list_type: CtyList[str]) -> None:
        """Test slice with no end index."""

        def s_val(s):
            return CtyString().validate(s)

        list_instance = CtyList(
            element_type=CtyString(), value=[s_val("a"), s_val("b"), s_val("c")]
        )  # type: ignore
        sliced = list_instance.slice(1)
        assert len(sliced.value) == 2
        assert sliced.value[0].value == "b"
        assert sliced.value[1].value == "c"

    def test_slice_from_beginning(self, string_list_type: CtyList[str]) -> None:
        """Test slice with no start index (though API requires start)."""

        # Current API `slice(self, start: int, end: Optional[int] = None)` requires start.
        # To test slicing from beginning, start=0 is used.
        def s_val(s):
            return CtyString().validate(s)

        list_instance = CtyList(
            element_type=CtyString(), value=[s_val("a"), s_val("b"), s_val("c")]
        )  # type: ignore
        sliced = list_instance.slice(0, 2)
        assert len(sliced.value) == 2
        assert sliced.value[0].value == "a"
        assert sliced.value[1].value == "b"

    def test_slice_out_of_bounds_clamps(self, string_list_type: CtyList[str]) -> None:
        """Test slice clamps out-of-bounds indices."""

        def s_val(s):
            return CtyString().validate(s)

        list_instance = CtyList(
            element_type=CtyString(), value=[s_val("a"), s_val("b")]
        )  # type: ignore

        sliced_over_end = list_instance.slice(1, 10)
        assert len(sliced_over_end.value) == 1
        assert sliced_over_end.value[0].value == "b"

        sliced_before_start = list_instance.slice(-5, 1)
        assert len(sliced_before_start.value) == 1
        assert sliced_before_start.value[0].value == "a"

        sliced_empty_due_to_bounds = list_instance.slice(5, 10)
        assert len(sliced_empty_due_to_bounds.value) == 0

        sliced_empty_negative = list_instance.slice(-1, -5)  # start effectively > end
        assert len(sliced_empty_negative.value) == 0


class TestCtyListConcat:
    def test_concat_successful(self, string_list_type: CtyList[str]) -> None:
        """Test successful concatenation of two lists."""

        def s_val(s):
            return CtyString().validate(s)

        list1 = CtyList(element_type=CtyString(), value=[s_val("a"), s_val("b")])  # type: ignore
        list2 = CtyList(element_type=CtyString(), value=[s_val("c"), s_val("d")])  # type: ignore

        concatenated = list1.concat(list2)
        assert len(concatenated.value) == 4
        assert [v.value for v in concatenated.value] == ["a", "b", "c", "d"]
        assert concatenated.element_type == string_list_type.element_type

    def test_concat_with_empty_list(self, string_list_type: CtyList[str]) -> None:
        """Test concatenation with an empty list."""

        def s_val(s):
            return CtyString().validate(s)

        list1 = CtyList(element_type=CtyString(), value=[s_val("a")])  # type: ignore
        empty_list = CtyList(element_type=CtyString(), value=[])  # type: ignore

        concatenated1 = list1.concat(empty_list)
        assert [v.value for v in concatenated1.value] == ["a"]

        concatenated2 = empty_list.concat(list1)
        assert [v.value for v in concatenated2.value] == ["a"]

    def test_concat_different_ctylist_instance_same_type(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test concat with a different CtyList instance but compatible type."""
        # string_list_type is CtyList(element_type=CtyString())
        # Create another CtyList type that is equal
        another_string_list_type = CtyList(element_type=CtyString())

        def s_val(s):
            return CtyString().validate(s)

        list1 = CtyList(element_type=string_list_type.element_type, value=[s_val("a")])  # type: ignore
        list2 = CtyList(
            element_type=another_string_list_type.element_type, value=[s_val("b")]
        )  # type: ignore

        concatenated = list1.concat(list2)
        assert [v.value for v in concatenated.value] == ["a", "b"]

    def test_concat_invalid_other_type(self, string_list_type: CtyList[str]) -> None:
        """Test concat raises error if other is not CtyList."""

        def s_val(s):
            return CtyString().validate(s)

        list1 = CtyList(element_type=CtyString(), value=[s_val("a")])  # type: ignore
        with pytest.raises(CtyListValidationError, match="Expected CtyList, got int"):
            list1.concat(123)  # type: ignore

    def test_concat_incompatible_element_type(
        self, string_list_type: CtyList[str], number_list_type: CtyList[float]
    ) -> None:
        """Test concat raises error for incompatible element types."""

        def s_val(s):
            return CtyString().validate(s)

        def n_val(n):
            return CtyNumber().validate(n)

        list_str = CtyList(element_type=CtyString(), value=[s_val("a")])  # type: ignore
        list_num = CtyList(element_type=CtyNumber(), value=[n_val(1)])  # type: ignore

        with pytest.raises(
            CtyListValidationError,
            match="Cannot concatenate lists with different element types",
        ):
            list_str.concat(list_num)  # type: ignore


class TestCtyListContains:
    def test_contains_item_present(self, string_list_type: CtyList[str]) -> None:
        def s_val(s):
            return CtyString().validate(s)

        list_instance = CtyList(
            element_type=CtyString(), value=[s_val("a"), s_val("b")]
        )  # type: ignore
        assert list_instance.contains("b")
        assert list_instance.contains(s_val("a"))  # Containing a CtyValue

    def test_contains_item_not_present(self, string_list_type: CtyList[str]) -> None:
        def s_val(s):
            return CtyString().validate(s)

        list_instance = CtyList(
            element_type=CtyString(), value=[s_val("a"), s_val("b")]
        )  # type: ignore
        assert not list_instance.contains("c")

    def test_contains_item_validation_fails(
        self, string_list_type: CtyList[str]
    ) -> None:
        """Test contains returns False if item validation fails."""

        def s_val(s):
            return CtyString().validate(s)

        list_instance = CtyList(element_type=CtyString(), value=[s_val("a")])  # type: ignore
        # CtyString().validate(123) would raise CtyStringValidationError
        assert not list_instance.contains(123)

    def test_contains_on_empty_list(self, string_list_type: CtyList[str]) -> None:
        empty_list = CtyList(element_type=CtyString(), value=[])  # type: ignore
        assert not empty_list.contains("a")


class TestCtyListUsableAs:
    def test_usable_as_self(self, string_list_type: CtyList[str]) -> None:
        assert string_list_type.usable_as(string_list_type)

    def test_usable_as_equal_list_type(self) -> None:
        lt1 = CtyList(element_type=CtyString())
        lt2 = CtyList(element_type=CtyString())
        assert lt1.usable_as(lt2)

    def test_usable_as_different_element_type(self) -> None:
        lt_str = CtyList(element_type=CtyString())
        lt_num = CtyList(element_type=CtyNumber())
        assert not lt_str.usable_as(lt_num)

    def test_usable_as_dynamic_element_type(self) -> None:
        lt_str = CtyList(element_type=CtyString())
        lt_dyn = CtyList(element_type=CtyDynamic())
        # CtyString is usable as CtyDynamic
        assert lt_str.usable_as(lt_dyn)
        # CtyDynamic is generally not usable as a more concrete type,
        # only as another CtyDynamic.
        assert not lt_dyn.usable_as(lt_str)

    def test_usable_as_non_list_type(self, string_list_type: CtyList[str]) -> None:
        assert not string_list_type.usable_as(CtyString())


class TestCtyListEqual:
    def test_equal_self(self, string_list_type: CtyList[str]) -> None:
        assert string_list_type.equal(string_list_type)
        assert string_list_type == string_list_type

    def test_equal_same_element_type(self) -> None:
        lt1 = CtyList(element_type=CtyString())
        lt2 = CtyList(element_type=CtyString())
        assert lt1.equal(lt2)
        assert lt1 == lt2

    def test_not_equal_different_element_type(self) -> None:
        lt_str = CtyList(element_type=CtyString())
        lt_num = CtyList(element_type=CtyNumber())
        assert not lt_str.equal(lt_num)
        assert lt_str != lt_num

    def test_not_equal_non_list_type(self, string_list_type: CtyList[str]) -> None:
        assert not string_list_type.equal(CtyString())  # type: ignore
        assert string_list_type != CtyString()  # type: ignore

    def test_equal_value_not_considered(self) -> None:
        """Equality of CtyList types should not depend on their .value attribute."""

        def s_val(s):
            return CtyString().validate(s)

        list_type1 = CtyList(element_type=CtyString(), value=[s_val("a")])  # type: ignore
        list_type2 = CtyList(element_type=CtyString(), value=[s_val("b")])  # type: ignore
        assert list_type1.equal(list_type2)  # Types are equal
        assert list_type1 == list_type2


class TestCtyListDunderMethods:
    def test_len(self) -> None:
        def s_val(s):
            return CtyString().validate(s)

        list_instance = CtyList(
            element_type=CtyString(), value=[s_val("a"), s_val("b")]
        )  # type: ignore
        assert len(list_instance) == 2

        empty_list = CtyList(element_type=CtyString(), value=[])  # type: ignore
        assert len(empty_list) == 0

    def test_iter(self) -> None:
        def s_val(s):
            return CtyString().validate(s)

        val_a, val_b = s_val("a"), s_val("b")
        list_instance = CtyList(element_type=CtyString(), value=[val_a, val_b])  # type: ignore

        elements = []
        for elem in list_instance:
            elements.append(elem)
        assert elements == [val_a, val_b]

    def test_getitem_integer_index(self) -> None:
        def s_val(s):
            return CtyString().validate(s)

        val_a, val_b = s_val("a"), s_val("b")
        list_instance = CtyList(element_type=CtyString(), value=[val_a, val_b])  # type: ignore
        assert list_instance[0] == val_a
        assert list_instance[1] == val_b
        with pytest.raises(IndexError, match="list index out of range"):
            _ = list_instance[2]

    def test_getitem_slice_no_step(self) -> None:
        def s_val(s):
            return CtyString().validate(s)

        val_a, val_b, val_c = s_val("a"), s_val("b"), s_val("c")
        list_instance = CtyList(element_type=CtyString(), value=[val_a, val_b, val_c])  # type: ignore

        sliced = list_instance[0:2]
        assert isinstance(sliced, CtyList)
        assert len(sliced.value) == 2
        assert sliced.value[0] == val_a
        assert sliced.value[1] == val_b

    def test_getitem_slice_with_step(self) -> None:
        def s_val(s):
            return CtyString().validate(s)

        vals = [s_val(c) for c in "abcde"]
        list_instance = CtyList(element_type=CtyString(), value=vals)  # type: ignore

        sliced = list_instance[0:5:2]
        assert isinstance(sliced, CtyList)
        assert len(sliced.value) == 3
        assert sliced.value[0].value == "a"
        assert sliced.value[1].value == "c"
        assert sliced.value[2].value == "e"

    def test_getitem_slice_with_step_empty_result(self) -> None:
        def s_val(s):
            return CtyString().validate(s)

        vals = [s_val(c) for c in "abcde"]
        list_instance = CtyList(element_type=CtyString(), value=vals)  # type: ignore

        sliced = list_instance[0:5:5]  # Step larger than range
        assert isinstance(sliced, CtyList)
        assert len(sliced.value) == 1
        assert sliced.value[0].value == "a"

        sliced_negative_step = list_instance[4:0:-1]  # Test negative step
        assert len(sliced_negative_step.value) == 4
        assert [v.value for v in sliced_negative_step.value] == ["e", "d", "c", "b"]

    def test_str_simple_type(self) -> None:
        lt_str = CtyList(element_type=CtyString())
        assert str(lt_str) == "list(CtyString)"

    def test_str_nested_list_type(self) -> None:
        nested_list = CtyList(element_type=CtyList(element_type=CtyNumber()))
        assert str(nested_list) == "list(list(CtyNumber))"

        double_nested_list = CtyList(
            element_type=CtyList(element_type=CtyList(element_type=CtyString()))
        )
        assert str(double_nested_list) == "list(list(list(CtyString)))"

    def test_repr(self) -> None:
        lt_str = CtyList(element_type=CtyString())
        # CtyString() repr is CtyString(value=None) or similar, so check for presence
        assert "CtyList(element_type=CtyString" in repr(lt_str)


# Test the is_collection_type and is_list_type methods (should be always True)
def test_type_flags(string_list_type: CtyList[str]) -> None:
    assert string_list_type.is_collection_type()
    assert string_list_type.is_list_type()
    assert not string_list_type.is_map_type()  # Sanity check
    assert not string_list_type.is_set_type()  # Sanity check
    assert not string_list_type.is_primitive_type()  # Sanity check
    assert not string_list_type.is_structured_type()  # Sanity check
