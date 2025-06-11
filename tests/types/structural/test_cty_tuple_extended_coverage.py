from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty.exceptions import CtyTupleValidationError, CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyBool, CtyNumber, CtyString
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.types.structural.tuple import CtyTuple
from pyvider.cty.values import CtyValue


# --- Fixtures ---
@pytest.fixture
def string_type() -> CtyString:
    return CtyString()


@pytest.fixture
def number_type() -> CtyNumber:
    return CtyNumber()


@pytest.fixture
def bool_type() -> CtyBool:
    return CtyBool()


@pytest.fixture
def simple_tuple_type(string_type: CtyString, number_type: CtyNumber) -> CtyTuple:
    return CtyTuple(element_types=(string_type, number_type))


# --- Tests ---


class TestCtyTupleInitValidation:  # For _validate_element_types
    def test_init_valid_element_types(
        self, string_type: CtyString, number_type: CtyNumber
    ) -> None:
        """Test CtyTuple instantiation with valid CtyType elements."""
        tuple_type = CtyTuple(element_types=(string_type, number_type))
        assert len(tuple_type.element_types) == 2

    def test_init_empty_element_types(self) -> None:
        """Test CtyTuple with an empty tuple of element types."""
        tuple_type = CtyTuple(element_types=())
        assert len(tuple_type.element_types) == 0

    def test_init_element_types_not_tuple(self) -> None:
        """Test __attrs_post_init__ raises error if element_types is not a tuple."""
        with pytest.raises(
            CtyTupleValidationError, match="element_types must be a tuple, got list"
        ):
            CtyTuple(element_types=[CtyString(), CtyNumber()])  # type: ignore

    def test_init_element_types_contains_non_ctytype(
        self, string_type: CtyString
    ) -> None:
        """Test __attrs_post_init__ raises error if an element_type is not a CtyType."""
        with pytest.raises(
            CtyTupleValidationError,
            match=r"Element type at index 1 must be a CtyType, got int",
        ):
            CtyTuple(element_types=(string_type, 123))  # type: ignore


class TestCtyTupleValidate:
    def test_validate_correct_value_tuple(self, simple_tuple_type: CtyTuple) -> None:
        """Test validate with a correct Python tuple of values."""
        val = simple_tuple_type.validate(("hello", 123))
        assert isinstance(val, CtyValue)
        assert val.type == simple_tuple_type
        assert isinstance(val.value, tuple)
        assert len(val.value) == 2
        assert val.value[0].value == "hello"
        assert val.value[1].value == Decimal("123")

    def test_validate_correct_value_list(self, simple_tuple_type: CtyTuple) -> None:
        """Test validate with a correct Python list of values."""
        val = simple_tuple_type.validate(["world", 45.67])
        assert isinstance(val, CtyValue)
        assert isinstance(
            val.value, tuple
        )  # Should be converted to tuple internally by CtyValue for tuples
        assert val.value[0].value == "world"
        assert val.value[1].value == Decimal("45.67")

    def test_validate_input_not_tuple_or_list(
        self, simple_tuple_type: CtyTuple
    ) -> None:
        """Test validate raises error for input that is not tuple or list."""
        with pytest.raises(CtyValidationError, match="Expected tuple or list, got str"):
            simple_tuple_type.validate("not a tuple")
        with pytest.raises(CtyValidationError, match="Expected tuple or list, got int"):
            simple_tuple_type.validate(123)

    def test_validate_incorrect_length(self, simple_tuple_type: CtyTuple) -> None:
        """Test validate raises error if input tuple/list has incorrect length."""
        # simple_tuple_type expects 2 elements
        with pytest.raises(CtyValidationError, match="Expected 2 elements, got 1"):
            simple_tuple_type.validate(("hello",))
        with pytest.raises(CtyValidationError, match="Expected 2 elements, got 3"):
            simple_tuple_type.validate(("hello", 123, True))

    def test_validate_element_type_mismatch_raw_value(
        self, simple_tuple_type: CtyTuple
    ) -> None:
        """Test validate raises error if an element's raw value doesn't match its CtyType."""
        # simple_tuple_type: (string, number)
        with pytest.raises(
            CtyValidationError,
            match=r"Invalid value for tuple element 1: Number validation error: Cannot convert string 'not-a-number' to number",
        ):
            simple_tuple_type.validate(("hello", "not-a-number"))

    def test_validate_element_is_ctyvalue_compatible(
        self, simple_tuple_type: CtyTuple, string_type: CtyString
    ) -> None:
        """Test validate with an element that is a CtyValue of a compatible type."""
        # simple_tuple_type: (string, number)
        # Pass CtyValue(CtyDynamic, "123") for the number part
        dynamic_num_val = CtyValue(vtype=CtyDynamic(), value="123")  # string "123"

        # Expect error because CtyDynamic is not usable_as CtyNumber directly at type level
        # The tuple validation doesn't unbox CtyDynamic to re-validate its inner value currently.
        with pytest.raises(
            CtyValidationError,
            match=r"Invalid value for tuple element 1: Value type mismatch for element 1: expected CtyNumber, got CtyDynamic",
        ):
            simple_tuple_type.validate(("test", dynamic_num_val))

    def test_validate_element_is_ctyvalue_incompatible(
        self, simple_tuple_type: CtyTuple, string_type: CtyString
    ) -> None:
        """Test validate raises error if an element is CtyValue of incompatible type."""
        # simple_tuple_type: (string, number)
        # Pass CtyValue(CtyString, "foo") for the number part
        string_val_for_num_pos = string_type.validate("foo")
        with pytest.raises(
            CtyValidationError,
            match=r"Value type mismatch for element 1: expected CtyNumber, got CtyString",
        ):
            simple_tuple_type.validate(("test", string_val_for_num_pos))

    def test_validate_element_is_ctyvalue_bool_for_number_pos(
        self, bool_type: CtyBool
    ) -> None:
        """Test specific CtyValue(CtyBool) for CtyNumber position error message."""
        # This tests the specific fix for error message formatting.
        tuple_type = CtyTuple(element_types=(CtyNumber(),))
        bool_val = bool_type.validate(True)  # CtyValue(CtyBool, True)
        with pytest.raises(CtyValidationError, match="Value must be a number"):
            tuple_type.validate((bool_val,))

    def test_validate_element_raw_decimal_conversion(self) -> None:
        """Test raw float/int in tuple get converted to Decimal by CtyNumber.validate."""
        tuple_type = CtyTuple(element_types=(CtyNumber(), CtyNumber()))
        val = tuple_type.validate((123, 45.67))
        assert val.value[0].value == Decimal("123")
        # Ensure float is precisely converted via string representation for CtyNumber
        assert val.value[1].value == Decimal(str(45.67))

    def test_validate_unexpected_error_during_element_validation(
        self, string_type: CtyString, mocker
    ) -> None:
        """Test handling of unexpected errors during an element's validate() call."""

        class ExplodingType(CtyType):
            def validate(self, value: Any) -> "CtyValue":
                raise RuntimeError("Boom!")

            def equal(self, other: CtyType) -> bool:
                return False

            def usable_as(self, other: CtyType) -> bool:
                return False

        tuple_type = CtyTuple(element_types=(string_type, ExplodingType()))
        with pytest.raises(
            CtyValidationError,
            match=r"Unexpected error validating tuple element 1: Boom!",
        ):
            tuple_type.validate(("hello", "anything"))


# Initial tests for validate and init. More to follow for other methods.


class TestCtyTupleElementAtAndSlice:
    def test_element_at_valid_index(self, simple_tuple_type: CtyTuple) -> None:
        # Note: element_at on CtyTuple type expects the *container* to be a CtyValue or raw tuple/list.
        # This is different from CtyList.element_at which was a method of the type definition.
        # CtyTuple.element_at is more like a static method helper if we interpret it strictly.
        # However, the method signature is `self, container: Any, index: int`.
        # This implies it's called on an instance of CtyTuple (a type definition).
        # Let's assume it's used to access elements from a raw tuple value that conforms to this type.
        raw_tuple_value = (CtyString().validate("hello"), CtyNumber().validate(123))

        # This test assumes element_at is meant to be called on the type instance,
        # and the 'container' is the raw data.
        el0 = simple_tuple_type.element_at(raw_tuple_value, 0)
        assert isinstance(el0, CtyValue) and el0.value == "hello"

        el1 = simple_tuple_type.element_at(raw_tuple_value, -1)  # Negative index
        assert isinstance(el1, CtyValue) and el1.value == Decimal(123)

    def test_element_at_ctyvalue_container(self, simple_tuple_type: CtyTuple) -> None:
        cty_tuple_value = simple_tuple_type.validate(("world", 42))
        el1 = simple_tuple_type.element_at(cty_tuple_value, 1)
        assert isinstance(el1, CtyValue) and el1.value == Decimal(42)

    def test_element_at_invalid_container_type(
        self, simple_tuple_type: CtyTuple
    ) -> None:
        with pytest.raises(
            CtyTupleValidationError, match="Expected tuple, list, or CtyValue, got int"
        ):
            simple_tuple_type.element_at(123, 0)  # type: ignore

    def test_element_at_null_or_unknown_container_raises(
        self, simple_tuple_type: CtyTuple
    ) -> None:
        null_tuple_val = CtyValue.null(simple_tuple_type)
        unknown_tuple_val = CtyValue.unknown(simple_tuple_type)
        with pytest.raises(
            CtyTupleValidationError,
            match="Cannot get element from null or unknown tuple value",
        ):
            simple_tuple_type.element_at(null_tuple_val, 0)
        with pytest.raises(
            CtyTupleValidationError,
            match="Cannot get element from null or unknown tuple value",
        ):
            simple_tuple_type.element_at(unknown_tuple_val, 0)

    def test_element_at_index_out_of_bounds(self, simple_tuple_type: CtyTuple) -> None:
        raw_tuple_value = (CtyString().validate("hello"), CtyNumber().validate(123))
        with pytest.raises(IndexError, match=r"Index 2 out of bounds \(0-1\)"):
            simple_tuple_type.element_at(raw_tuple_value, 2)
        with pytest.raises(
            IndexError, match=r"Index -1 out of bounds \(0-1\)"
        ):  # Corrected expected index
            simple_tuple_type.element_at(raw_tuple_value, -3)

    def test_slice_basic(
        self,
        simple_tuple_type: CtyTuple,
        string_type: CtyString,
        number_type: CtyNumber,
        bool_type: CtyBool,
    ) -> None:  # Added bool_type fixture
        # Similar to element_at, assuming 'container' is the data, 'self' is the type def.
        raw_tuple_value = (
            string_type.validate("a"),
            number_type.validate(1),
            bool_type.validate(True),
        )
        # Original type: (str, num, bool)
        original_tuple_type = CtyTuple(
            element_types=(string_type, number_type, bool_type)
        )  # Use fixture

        # Slice to get (str, num)
        sliced_cty_value = original_tuple_type.slice(raw_tuple_value, 0, 2)
        assert isinstance(sliced_cty_value, CtyValue)
        assert isinstance(sliced_cty_value.type, CtyTuple)
        assert len(sliced_cty_value.type.element_types) == 2
        assert sliced_cty_value.type.element_types[0] == string_type
        assert sliced_cty_value.type.element_types[1] == number_type
        assert sliced_cty_value.value[0].value == "a"
        assert sliced_cty_value.value[1].value == Decimal(1)

    def test_slice_to_end_and_negative_indices(
        self, string_type, number_type, bool_type
    ) -> None:
        original_tuple_type = CtyTuple(
            element_types=(string_type, number_type, bool_type)
        )
        raw_tuple_value = (
            string_type.validate("a"),
            number_type.validate(1),
            bool_type.validate(True),
        )

        cty_val_slice1 = original_tuple_type.slice(
            raw_tuple_value, 1
        )  # from index 1 to end
        assert len(cty_val_slice1.type.element_types) == 2
        assert cty_val_slice1.value[0].type == number_type
        assert cty_val_slice1.value[1].type == bool_type

        cty_val_slice2 = original_tuple_type.slice(raw_tuple_value, -2, -1)  # (num)
        assert len(cty_val_slice2.type.element_types) == 1
        assert cty_val_slice2.value[0].type == number_type

    def test_slice_out_of_bounds_clamps(self, string_type, number_type) -> None:
        original_tuple_type = CtyTuple(element_types=(string_type, number_type))
        raw_tuple_value = (string_type.validate("a"), number_type.validate(1))

        cty_val_slice_over = original_tuple_type.slice(
            raw_tuple_value, 0, 10
        )  # Clamps to (str, num)
        assert len(cty_val_slice_over.type.element_types) == 2

        cty_val_slice_empty = original_tuple_type.slice(
            raw_tuple_value, 5, 10
        )  # Clamps to empty
        assert len(cty_val_slice_empty.type.element_types) == 0
        assert cty_val_slice_empty.value == ()

    def test_slice_null_or_unknown_container_raises(
        self, simple_tuple_type: CtyTuple
    ) -> None:
        null_tuple_val = CtyValue.null(simple_tuple_type)
        unknown_tuple_val = CtyValue.unknown(simple_tuple_type)
        with pytest.raises(
            CtyTupleValidationError, match="Cannot slice null or unknown tuple value"
        ):
            simple_tuple_type.slice(null_tuple_val, 0, 1)
        with pytest.raises(
            CtyTupleValidationError, match="Cannot slice null or unknown tuple value"
        ):
            simple_tuple_type.slice(unknown_tuple_val, 0, 1)

    def test_slice_invalid_container_type(self, simple_tuple_type: CtyTuple) -> None:
        with pytest.raises(
            CtyTupleValidationError, match="Expected tuple, list, or CtyValue, got int"
        ):
            simple_tuple_type.slice(123, 0, 1)  # type: ignore


class TestCtyTupleEqualUsableAs:
    def test_equal_true_same_elements(self, string_type, number_type) -> None:
        t1 = CtyTuple(element_types=(string_type, number_type))
        t2 = CtyTuple(element_types=(string_type, number_type))
        assert t1.equal(t2)
        assert t1 == t2  # Test __eq__

    def test_equal_false_different_length(self, string_type, number_type) -> None:
        t1 = CtyTuple(element_types=(string_type, number_type))
        t2 = CtyTuple(element_types=(string_type,))
        assert not t1.equal(t2)

    def test_equal_false_different_element_types(
        self, string_type, number_type
    ) -> None:
        t1 = CtyTuple(element_types=(string_type, number_type))
        t2 = CtyTuple(element_types=(string_type, string_type))
        assert not t1.equal(t2)

    def test_equal_false_not_tuple_type(self, simple_tuple_type, string_type) -> None:
        assert not simple_tuple_type.equal(string_type)  # type: ignore

    def test_usable_as_true_identical(self, simple_tuple_type: CtyTuple) -> None:
        assert simple_tuple_type.usable_as(simple_tuple_type)

    def test_usable_as_true_element_types_compatible(
        self, string_type, number_type
    ) -> None:
        # (string, number) usable as (string, dynamic)
        t_concrete = CtyTuple(element_types=(string_type, number_type))
        t_dynamic_val = CtyTuple(element_types=(string_type, CtyDynamic()))
        assert t_concrete.usable_as(t_dynamic_val)

    def test_usable_as_false_element_types_incompatible(
        self, string_type, number_type
    ) -> None:
        # (string, string) not usable as (string, number)
        t_str_str = CtyTuple(element_types=(string_type, string_type))
        t_str_num = CtyTuple(element_types=(string_type, number_type))
        assert not t_str_str.usable_as(t_str_num)

    def test_usable_as_false_different_length(self, string_type, number_type) -> None:
        t1 = CtyTuple(element_types=(string_type, number_type))
        t2 = CtyTuple(element_types=(string_type,))
        assert not t1.usable_as(t2)
        assert not t2.usable_as(t1)

    def test_usable_as_true_to_dynamic(self, simple_tuple_type: CtyTuple) -> None:
        assert simple_tuple_type.usable_as(CtyDynamic())

    def test_usable_as_false_from_dynamic_to_concrete(
        self, simple_tuple_type: CtyTuple
    ) -> None:
        assert not CtyDynamic().usable_as(simple_tuple_type)  # type: ignore

    def test_usable_as_false_not_tuple_type(
        self, simple_tuple_type: CtyTuple, string_type
    ) -> None:
        assert not simple_tuple_type.usable_as(string_type)


class TestCtyTupleDunderMethodsAndFlags:
    def test_getitem_integer_index(
        self, simple_tuple_type: CtyTuple, string_type, number_type
    ) -> None:
        assert simple_tuple_type[0] == string_type
        assert simple_tuple_type[1] == number_type
        with pytest.raises(IndexError, match="tuple index out of range"):
            _ = simple_tuple_type[2]

    def test_getitem_slice(self, string_type, number_type, bool_type) -> None:
        original_type = CtyTuple(element_types=(string_type, number_type, bool_type))

        sliced_type = original_type[0:2]
        assert isinstance(sliced_type, CtyTuple)
        assert sliced_type.element_types == (string_type, number_type)

        sliced_with_step = original_type[0:3:2]
        assert isinstance(sliced_with_step, CtyTuple)
        assert sliced_with_step.element_types == (string_type, bool_type)

        empty_slice = original_type[1:1]
        assert isinstance(empty_slice, CtyTuple)
        assert empty_slice.element_types == ()

    def test_str_representation(
        self, simple_tuple_type: CtyTuple, string_type, number_type
    ) -> None:
        assert str(simple_tuple_type) == "tuple(string, number)"
        empty_tuple_type = CtyTuple(element_types=())
        assert str(empty_tuple_type) == "tuple()"
        nested_tuple = CtyTuple(
            element_types=(string_type, CtyTuple(element_types=(number_type,)))
        )
        assert str(nested_tuple) == "tuple(string, tuple(number))"

    def test_repr_representation(self, simple_tuple_type: CtyTuple) -> None:
        # Repr includes module info if types are not basic CtyString etc.
        # For basic ones, it should be clean.
        assert (
            "CtyTuple(element_types=(CtyString(value=''), CtyNumber(value=0)))"
            in repr(simple_tuple_type)
        )
        empty_tuple_type = CtyTuple(element_types=())
        assert repr(empty_tuple_type) == "CtyTuple(element_types=())"

    def test_type_flags(self, simple_tuple_type: CtyTuple) -> None:
        assert simple_tuple_type.is_structured_type()
        assert simple_tuple_type.is_tuple_type()
        assert not simple_tuple_type.is_primitive_type()
        assert not simple_tuple_type.is_collection_type()
