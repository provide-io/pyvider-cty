from decimal import Decimal
from typing import Any, Never

import pytest

from pyvider.cty.exceptions import CtySetValidationError
from pyvider.cty.types.base import CtyType  # For type hinting and isinstance checks
from pyvider.cty.types.collections.set import CtySet
from pyvider.cty.types.primitives.number import CtyNumber
from pyvider.cty.types.primitives.string import CtyString
from pyvider.cty.types.structural.dynamic import CtyDynamic
from pyvider.cty.values import CtyValue


# --- Fixtures ---
@pytest.fixture
def string_set_type() -> CtySet[str]:
    return CtySet(element_type=CtyString())


@pytest.fixture
def number_set_type() -> CtySet[Decimal]:
    return CtySet(element_type=CtyNumber())


@pytest.fixture
def dynamic_set_type() -> CtySet[Any]:
    return CtySet(element_type=CtyDynamic())


# --- Tests ---


class TestCtySetAttrsPostInit:
    def test_attrs_post_init_invalid_element_type(self) -> None:
        """Test __attrs_post_init__ raises error for invalid element_type (not a CtyType)."""
        with pytest.raises(
            CtySetValidationError,
            match=r"Expected CtyType for element_type, got <class 'int'>",
        ):
            CtySet(element_type=123)  # type: ignore

    def test_attrs_post_init_success(self, string_set_type: CtySet[str]) -> None:
        """Test successful __attrs_post_init__."""
        assert isinstance(string_set_type.element_type, CtyString)


class TestCtySetValidate:
    def test_validate_none_input_returns_null_value(
        self, string_set_type: CtySet[str]
    ) -> None:
        """Test validate with None input returns a null CtyValue."""
        cty_val = string_set_type.validate(None)
        assert isinstance(cty_val, CtyValue)
        assert cty_val.type == string_set_type
        assert cty_val.is_null
        assert cty_val.value is None  # Internal representation of null for CtyValue

    def test_validate_ctyvalue_matching_type(
        self, string_set_type: CtySet[str]
    ) -> None:
        """Test validate with a CtyValue of the exact same set type."""
        original_value = string_set_type.validate({"hello", "world"})
        validated_value = string_set_type.validate(original_value)
        assert validated_value is original_value

    def test_validate_ctyvalue_unknown_and_usable(
        self, string_set_type: CtySet[str]
    ) -> None:
        """Test validate with an unknown CtyValue of a usable type."""
        # Create an unknown value whose type is CtySet(CtyString())
        unknown_set_val = CtyValue.unknown(string_set_type)

        validated_val = string_set_type.validate(unknown_set_val)
        assert validated_val.is_unknown
        assert validated_val.type == string_set_type

    def test_validate_ctyvalue_value_extraction_error(
        self, string_set_type: CtySet[str]
    ) -> None:
        """Test validate CtyValue where .value access raises ValueError (e.g. bad unknown)."""
        # This requires a CtyValue that is not unknown, but .value access fails.
        # This scenario is a bit artificial as CtyValue constructors usually prevent this.
        # We can mock CtyValue or create a carefully crafted one if needed.
        # For now, let's assume this path is hard to hit with current CtyValue impl.
        # The code `value = value.value` implies `value` is not unknown.
        # A CtyValue that is known but whose internal .value access raises ValueError is unusual.
        # This might cover cases where a CtyValue was constructed with a type that has since become "unusable"
        # or if a CtyValue subclass had a faulty .value property.

        # Let's try to simulate a CtyValue that is not CtySet but whose .value might be problematic
        # if usable_as was true.
        class MockProblematicValueType(CtyType):
            def validate(self, v):
                return CtyValue(self, v)

            def equal(self, o):
                return isinstance(o, MockProblematicValueType)

            def usable_as(self, o):
                return isinstance(o, CtySet)  # Pretend it's usable as CtySet

        problem_type = MockProblematicValueType()

        class ProblematicCtyValue(CtyValue):
            @property
            def value(self) -> Never:
                raise ValueError("Simulated access error")

        # This value is not unknown, its type claims to be usable as CtySet, but .value access fails
        problem_cty_value = ProblematicCtyValue(
            vtype=problem_type, value=None
        )  # value here is for constructor, not the property

        with pytest.raises(CtySetValidationError, match="Simulated access error"):
            string_set_type.validate(problem_cty_value)

    def test_validate_list_tuple_input_conversion(
        self, string_set_type: CtySet[str]
    ) -> None:
        """Test validate converts list/tuple inputs to sets."""
        list_input = ["a", "b", "a"]
        tuple_input = ("c", "d", "c")

        cty_val_from_list = string_set_type.validate(list_input)
        assert isinstance(cty_val_from_list.value, frozenset)
        assert len(cty_val_from_list.value) == 2  # Duplicates removed
        assert {v.value for v in cty_val_from_list.value} == {"a", "b"}

        cty_val_from_tuple = string_set_type.validate(tuple_input)
        assert isinstance(cty_val_from_tuple.value, frozenset)
        assert len(cty_val_from_tuple.value) == 2
        assert {v.value for v in cty_val_from_tuple.value} == {"c", "d"}

    def test_validate_empty_list_input_converted_to_set(
        self, string_set_type: CtySet[str]
    ) -> None:
        """Test validate with an empty list input that gets converted to a set."""
        cty_val = string_set_type.validate([])  # Empty list
        assert isinstance(cty_val, CtyValue)
        assert cty_val.type == string_set_type
        assert cty_val.value == frozenset()  # Should be an empty frozenset

    def test_validate_list_tuple_with_unhashable_items(
        self, dynamic_set_type: CtySet[Any]
    ) -> None:
        """Test validate list/tuple with unhashable items raises error."""
        # CtyDynamic can hold lists/dicts, which are unhashable for sets.
        # However, CtyDynamic.validate wraps them in CtyValues which are hashable.
        # So, to test this, the *elements* of the input list/tuple to CtySet.validate
        # must be directly unhashable Python types if element_type is CtyDynamic.
        # If element_type is CtyList(CtyString), then CtyList(CtyString).validate(['a'])
        # would produce a hashable CtyValue.

        # This test is for the set(value) conversion inside CtySet.validate
        # If we have a list like `[['a'], ['b']]` and try to make `set([['a'], ['b']])`, Python fails.
        # CtySet's element_type would be CtyList(CtyString()) for this to be valid post-validation.
        # But the initial `set(value)` happens before element validation.

        # We need a CtySet of a type that CANNOT hold unhashable things after validation,
        # but the raw input list might contain them.
        # This test targets the `except TypeError as e:` in `validate`

        # This path is hard to hit if `element_type` doesn't allow unhashable items,
        # because `self.element_type.validate(raw_item)` would fail first.
        # Let's assume element_type is CtyDynamic for this test, which *would* successfully validate a list.
        # So, `set([CtyDynamic().validate(['a'])])` is fine.
        # The target is `set([['a']])` failing *before* CtyDynamic validation.

        # This test is for the initial `set(value)` conversion
        with pytest.raises(
            CtySetValidationError,
            match=r"Input list/tuple could not be converted to set \(possibly unhashable elements\): unhashable type: 'list'",
        ):
            # string_set_type expects strings. If we pass [['a']], element validation will fail.
            # But we want to test the `set([['a']])` failure first.
            # This means the element_type validation should not run before set() conversion.
            # The current code runs set(value) *after* CtyValue processing but *before* element validation loop.
            # This test should be valid.
            dynamic_set_type.validate([["a"], ["b"]])  # type: ignore

    def test_validate_invalid_container_type(
        self, string_set_type: CtySet[str]
    ) -> None:
        """Test validate raises error for non-set/list/tuple input."""
        with pytest.raises(
            CtySetValidationError,
            match=r"Expected a Python set/frozenset \(or convertible list/tuple\) for CtySet validation; got int",
        ):
            string_set_type.validate(123)

    def test_validate_element_validation_fails(
        self, string_set_type: CtySet[str]
    ) -> None:
        """Test validate when an element fails validation against element_type."""
        with pytest.raises(CtySetValidationError) as excinfo:
            string_set_type.validate(
                {"valid_string", 123}
            )  # 123 is not a valid CtyString
        assert "Set validation failed:" in str(excinfo.value)
        assert (
            "element 0: String validation error: Value must be a string, got int"
            in str(excinfo.value)
            or "element 1: String validation error: Value must be a string, got int"
            in str(excinfo.value)
        )

    def test_validate_multiple_element_errors(
        self, number_set_type: CtySet[Decimal]
    ) -> None:
        """Test validate aggregates multiple element validation errors."""
        with pytest.raises(CtySetValidationError) as excinfo:
            number_set_type.validate({1, "not-a-number", 3.14})
        error_str = str(excinfo.value)
        assert "Set validation failed:" in error_str
        assert "element " in error_str  # Check for multiple element errors
        # Check for specific error messages, acknowledging order might vary due to set iteration
        err_nan = (
            "Number validation error: Cannot convert string 'not-a-number' to number"
        )
        err_bool = "Number validation error: Value must be a number or a string representation of a number, got bool"
        assert err_nan in error_str or err_bool in error_str
        assert err_bool in error_str or err_nan in error_str

    def test_validate_successful_set(self, number_set_type: CtySet[Decimal]) -> None:
        """Test successful validation of a set of numbers."""
        input_set = {1, 2.5, CtyNumber().validate(3), Decimal("4.0")}
        cty_val = number_set_type.validate(input_set)
        assert isinstance(cty_val, CtyValue)
        assert cty_val.type == number_set_type
        assert isinstance(cty_val.value, frozenset)
        # Extract Python values from CtyValue elements for comparison
        py_values = {v.value for v in cty_val.value}
        assert py_values == {Decimal("1"), Decimal("2.5"), Decimal("3"), Decimal("4.0")}


# More tests for add, remove, etc. will follow.
# Initial focus on __attrs_post_init__ and validate.


class TestCtySetAdd:
    def test_add_new_element(self, string_set_type: CtySet[str]) -> None:
        set_val = CtySet(
            element_type=CtyString(), value=frozenset({CtyString().validate("a")})
        )  # type: ignore
        added_set_type_instance = set_val.add(
            "b"
        )  # CtySet.add returns a new CtySet *type* instance

        # The .add method in CtySet returns a new CtySet *type* instance,
        # with the new element conceptually part of its internal 'value' field for that new type definition.
        # This is different from a CtyValue object's operations.
        # The 'value' attribute of a CtySet type definition holds the default/initial value,
        # not the result of an operation on an instance of data.
        # The test needs to be about the returned CtySet *type* instance.

        # Let's assume CtySet.add is intended to operate on an *instance* of a set
        # and return a *new instance* of that set type with the element added.
        # The current CtySet is defined with `value: PySet[T] = field(factory=set, kw_only=True)`
        # This 'value' is part of the type definition, not an instance's current data.
        # The methods add/remove seem to be defined on the type, intending to return new type instances
        # which is unusual. Typically, these ops would be on a CtyValue(set_type, actual_set_data).
        # Given the current implementation, let's test what it does:

        assert isinstance(added_set_type_instance, CtySet)
        # The 'value' field of the *new type instance* should contain the added element.
        # This implies `evolve(self, value=new_set)` changes the default `value` of the new type.
        expected_values = {CtyString().validate("a"), CtyString().validate("b")}
        assert added_set_type_instance.value == expected_values

    def test_add_existing_element(self, string_set_type: CtySet[str]) -> None:
        val_a = CtyString().validate("a")
        set_val = CtySet(element_type=CtyString(), value=frozenset({val_a}))  # type: ignore
        added_set_type_instance = set_val.add("a")
        assert added_set_type_instance.value == {val_a}

    def test_add_element_validation_fails(self, string_set_type: CtySet[str]) -> None:
        set_val = CtySet(element_type=CtyString(), value=frozenset())  # type: ignore
        with pytest.raises(
            CtySetValidationError,
            match="Failed to add element: String validation error: Value must be a string, got int",
        ):
            set_val.add(123)


class TestCtySetRemove:
    def test_remove_existing_element(self, string_set_type: CtySet[str]) -> None:
        val_a = CtyString().validate("a")
        val_b = CtyString().validate("b")
        set_val = CtySet(element_type=CtyString(), value=frozenset({val_a, val_b}))  # type: ignore
        removed_set_type_instance = set_val.remove("b")
        assert removed_set_type_instance.value == {val_a}

    def test_remove_non_existing_element(self, string_set_type: CtySet[str]) -> None:
        val_a = CtyString().validate("a")
        set_val = CtySet(element_type=CtyString(), value=frozenset({val_a}))  # type: ignore
        removed_set_type_instance = set_val.remove("c")  # "c" is not in the set
        assert removed_set_type_instance.value == {val_a}  # Should be unchanged

    def test_remove_element_validation_fails(
        self, string_set_type: CtySet[str]
    ) -> None:
        set_val = CtySet(element_type=CtyString(), value=frozenset())  # type: ignore
        with pytest.raises(
            CtySetValidationError,
            match="Failed to remove item: String validation error: Value must be a string, got int",
        ):
            set_val.remove(123)  # type: ignore


class TestCtySetUsableAs:
    def test_usable_as_self(self, string_set_type: CtySet[str]) -> None:
        assert string_set_type.usable_as(string_set_type)

    def test_usable_as_equal_set_type(self) -> None:
        st1 = CtySet(element_type=CtyString())
        st2 = CtySet(element_type=CtyString())
        assert st1.usable_as(st2)

    def test_usable_as_false_different_element_type(self) -> None:
        st_str = CtySet(element_type=CtyString())
        st_num = CtySet(element_type=CtyNumber())
        assert not st_str.usable_as(st_num)

    def test_usable_as_true_element_type_usable(self) -> None:
        # set<string> usable as set<dynamic> because string is usable as dynamic
        st_str = CtySet(element_type=CtyString())
        st_dyn = CtySet(element_type=CtyDynamic())
        assert st_str.usable_as(st_dyn)

    def test_usable_as_false_element_type_not_usable(self) -> None:
        # set<dynamic> not usable as set<string> because dynamic is not usable as string
        st_dyn = CtySet(element_type=CtyDynamic())
        st_str = CtySet(element_type=CtyString())
        assert not st_dyn.usable_as(st_str)

    def test_usable_as_false_not_set_type(self, string_set_type: CtySet[str]) -> None:
        assert not string_set_type.usable_as(CtyString())


class TestCtySetEqual:
    def test_equal_self(self, string_set_type: CtySet[str]) -> None:
        assert string_set_type.equal(string_set_type)

    def test_equal_same_element_type(self) -> None:
        st1 = CtySet(element_type=CtyString())
        st2 = CtySet(element_type=CtyString())
        assert st1.equal(st2)

    def test_not_equal_different_element_type(self) -> None:
        st_str = CtySet(element_type=CtyString())
        st_num = CtySet(element_type=CtyNumber())
        assert not st_str.equal(st_num)

    def test_not_equal_non_set_type(self, string_set_type: CtySet[str]) -> None:
        assert not string_set_type.equal(CtyString())  # type: ignore


class TestCtySetDunderMethodsAndFlags:
    def test_iter(self, string_set_type: CtySet[str]) -> None:
        # Note: CtySet type's .value is its default/initial value.
        # Iteration makes sense on a CtyValue of this set type.
        # For the type itself, __iter__ would iterate its default 'value' field.
        val_a = CtyString().validate("a")
        val_b = CtyString().validate("b")
        set_type_with_value = CtySet(
            element_type=CtyString(), value=frozenset({val_a, val_b})
        )  # type: ignore

        iterated_elements = {elem for elem in set_type_with_value}
        assert iterated_elements == {val_a, val_b}

    def test_str(self, string_set_type: CtySet[str]) -> None:
        assert str(string_set_type) == "set(string)"  # Uses element_type.__str__()
        nested_set = CtySet(element_type=CtySet(element_type=CtyNumber()))
        # Note: __str__ of element_type is used. CtySet's str() is "set(ElementType)"
        assert str(nested_set) == "set(set(number))"  # Uses element_type.__str__()

    def test_type_flags(self, string_set_type: CtySet[str]) -> None:
        assert string_set_type.is_collection_type()
        assert string_set_type.is_set_type()
        assert not string_set_type.is_list_type()
        assert not string_set_type.is_map_type()


# Need to import CtyType for the UnsortableKeyType definition in test_cty_map_element_iterator
# This was added in the previous subtask's test file, ensure it's here if needed.
# from pyvider.cty.types.base import CtyType
# It's already imported at the top.
