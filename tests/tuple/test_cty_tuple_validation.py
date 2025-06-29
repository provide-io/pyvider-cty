import pytest
from decimal import Decimal
from pyvider.cty import (
    CtyBool, CtyNumber, CtyString, CtyList, CtyTuple, CtyValue, CtyDynamic
)
from pyvider.cty.exceptions import CtyValidationError, CtyTupleValidationError

class TestCtyTupleValidation:
    @pytest.fixture
    def tuple_type_sn(self):
        return CtyTuple(element_types=(CtyString(), CtyNumber()))

    def test_validate_with_ctyvalues_mismatched_type(self, tuple_type_sn) -> None:
        val1 = CtyString().validate("cty")
        val2_convertible = CtyBool().validate(True) # bool is convertible to number
        data = (val1, val2_convertible)

        validated_tuple = tuple_type_sn.validate(data)
        assert isinstance(validated_tuple, CtyValue)
        assert isinstance(validated_tuple.type, CtyTuple)
        element1, element2 = validated_tuple.value
        assert element1.type.equal(CtyString()) and element1.value == "cty"
        assert element2.type.equal(CtyNumber()) and element2.value == Decimal("1")

    def test_validate_correct_input(self, tuple_type_sn):
        data = ("hello", 123)
        validated_tuple = tuple_type_sn.validate(data)
        assert validated_tuple.value[0].value == "hello"
        assert validated_tuple.value[1].value == Decimal("123")

    def test_validate_incorrect_length_too_few(self, tuple_type_sn):
        data = ("hello",)
        with pytest.raises(CtyValidationError, match="Expected 2 elements, got 1"):
            tuple_type_sn.validate(data)

    def test_validate_incorrect_length_too_many(self, tuple_type_sn):
        data = ("hello", 123, True)
        with pytest.raises(CtyValidationError, match="Expected 2 elements, got 3"):
            tuple_type_sn.validate(data)

    def test_validate_element_type_mismatch_raw(self, tuple_type_sn):
        data = ("hello", "not-a-number")
        with pytest.raises(CtyValidationError, match="Invalid value for tuple element 1: Number validation error: Cannot convert string 'not-a-number' to number"):
            tuple_type_sn.validate(data)

    def test_validate_element_type_mismatch_ctyvalue(self, tuple_type_sn):
        # Element is a CtyValue of an incompatible type (CtyBool instead of CtyNumber)
        # CtyNumber.validate(CtyBool(True)) would work, but CtyNumber.validate(CtyBool(False)) also works.
        # Let's use CtyString for a clearer mismatch for CtyNumber.
        data = (CtyString().validate("hello"), CtyString().validate("not-a-number"))
        with pytest.raises(CtyValidationError, match="Invalid value for tuple element 1: Number validation error: Value of type str cannot be converted to a number."):
            tuple_type_sn.validate(data)

    def test_validate_none_input(self, tuple_type_sn):
        result = tuple_type_sn.validate(None)
        assert result.is_null
        assert result.type == tuple_type_sn

    def test_validate_unknown_input(self, tuple_type_sn):
        unknown_val = CtyValue.unknown(tuple_type_sn)
        result = tuple_type_sn.validate(unknown_val)
        assert result.is_unknown
        assert result.type == tuple_type_sn

    def test_validate_unknown_input_different_tuple_type(self, tuple_type_sn):
        different_tuple_type = CtyTuple((CtyBool(),))
        unknown_val = CtyValue.unknown(different_tuple_type)
        result = tuple_type_sn.validate(unknown_val)
        assert result.is_unknown
        assert result.type == tuple_type_sn


    def test_validate_non_list_or_tuple_input(self, tuple_type_sn):
        data = "not-a-tuple"
        with pytest.raises(CtyValidationError, match="Expected tuple or list, got str"):
            tuple_type_sn.validate(data)

        data_dict = {"a": 1}
        with pytest.raises(CtyValidationError, match="Expected tuple or list, got dict"):
            tuple_type_sn.validate(data_dict)

    def test_validate_already_correct_ctyvalue(self, tuple_type_sn):
        correct_val = tuple_type_sn.validate(("a", 1))
        result = tuple_type_sn.validate(correct_val)
        assert result is correct_val

    def test_validate_ctyvalue_different_tuple_type_wrong_length(self, tuple_type_sn):
        other_type = CtyTuple((CtyBool(),))
        other_val = other_type.validate((True,))
        with pytest.raises(CtyValidationError, match="Expected 2 elements, got 1"):
            tuple_type_sn.validate(other_val)

    def test_validate_ctyvalue_different_tuple_type_element_mismatch(self):
        tuple_type_ss = CtyTuple((CtyString(), CtyString()))
        other_type = CtyTuple((CtyString(), CtyNumber()))
        other_val = other_type.validate(("hello", 123)) # CtyValue(tuple(string,number), ("hello", CtyValue(Number,123)))

        # tuple_type_ss.validate will try to validate other_val.value which is (CtyValue(String,"hello"), CtyValue(Number,123))
        # The second element CtyValue(Number,123) will be passed to CtyString.validate()
        with pytest.raises(CtyValidationError, match="Invalid value for tuple element 1: String validation error: Cannot convert CtyValue of type CtyNumber to CtyString"):
            tuple_type_ss.validate(other_val)


    def test_validate_ctyvalue_non_tuple_type(self, tuple_type_sn):
        non_tuple_val = CtyString().validate("test")
        with pytest.raises(CtyValidationError, match="Expected tuple or list, got str"):
            tuple_type_sn.validate(non_tuple_val)

    @pytest.fixture
    def nested_tuple_type(self):
        inner_tuple = CtyTuple((CtyNumber(), CtyBool()))
        return CtyTuple((CtyString(), inner_tuple))

    def test_nested_validate_correct(self, nested_tuple_type):
        data = ("outer", (123, True))
        validated = nested_tuple_type.validate(data)
        assert validated.value[0].value == "outer"
        assert validated.value[1].value[0].value == Decimal("123")
        assert validated.value[1].value[1].value is True

    def test_nested_validate_outer_length_mismatch(self, nested_tuple_type):
        data = ("outer_only",)
        with pytest.raises(CtyValidationError, match="Expected 2 elements, got 1"):
            nested_tuple_type.validate(data)

    def test_nested_validate_inner_length_mismatch(self, nested_tuple_type):
        data = ("outer", (123,))
        with pytest.raises(CtyValidationError, match="Invalid value for tuple element 1: Expected 2 elements, got 1"):
            nested_tuple_type.validate(data)

    def test_nested_validate_outer_type_mismatch_convertible(self, nested_tuple_type):
        data = (12345, (123, True))
        validated = nested_tuple_type.validate(data) # int 12345 is convertible to string "12345"
        assert validated.value[0].type.equal(CtyString())
        assert validated.value[0].value == "12345"
        assert validated.value[1].type.equal(CtyTuple((CtyNumber(), CtyBool())))

    def test_nested_validate_inner_type_mismatch(self, nested_tuple_type):
        data = ("outer", (123, "not-a-bool"))
        with pytest.raises(CtyValidationError, match="Invalid value for tuple element 1: Invalid value for tuple element 1: Boolean validation error: Cannot convert string 'not-a-bool' to boolean"):
            nested_tuple_type.validate(data)
            
    def test_tuple_constructor_invalid_element_types_input(self):
        with pytest.raises(CtyTupleValidationError, match="element_types must be a tuple"):
            CtyTuple(element_types=["not-a-tuple"]) # type: ignore
        with pytest.raises(CtyTupleValidationError, match="Element type at index 0 must be a CtyType"):
            CtyTuple(element_types=("not-a-ctytype",)) # type: ignore
            
    def test_validate_tuple_with_dynamic_elements(self):
        tuple_type_dyn = CtyTuple((CtyDynamic(), CtyNumber()))

        data1 = ("hello", 123)
        val1 = tuple_type_dyn.validate(data1)
        assert val1.value[0].type.is_dynamic_type()
        assert val1.value[0].value.type.equal(CtyString())
        assert val1.value[0].value.value == "hello"
        assert val1.value[1].value == Decimal("123")

        data2 = (CtyBool().validate(True), 456)
        val2 = tuple_type_dyn.validate(data2)
        assert val2.value[0].type.is_dynamic_type()
        assert val2.value[0].value.type.equal(CtyBool())
        assert val2.value[0].value.value is True
        assert val2.value[1].value == Decimal("456")

        data3 = (None, 789)
        val3 = tuple_type_dyn.validate(data3)
        assert val3.value[0].type.is_dynamic_type()
        assert val3.value[0].value.is_null
        assert val3.value[0].value.type.is_dynamic_type()
        assert val3.value[1].value == Decimal("789")

    def test_validate_tuple_with_dynamic_element_validation_failure(self):
        class Unserializable: pass
        tuple_type = CtyTuple((CtyString(), CtyDynamic()))
        data = ("test", Unserializable())
        with pytest.raises(CtyValidationError,
                           match="Invalid value for tuple element 1: Cannot infer a concrete CtyType for raw Python type: Unserializable"):
            tuple_type.validate(data)

    def test_validate_tuple_elements_are_ctyvalues(self, tuple_type_sn):
        """Test validation when elements are already CtyValues."""
        data = (CtyString().validate("text"), CtyNumber().validate(42))
        validated_tuple = tuple_type_sn.validate(data)
        assert validated_tuple.value[0].value == "text"
        assert validated_tuple.value[1].value == Decimal("42")

    def test_validate_tuple_mixed_raw_and_ctyvalues(self, tuple_type_sn):
        """Test validation with mixed raw and CtyValue elements."""
        data = ("raw_text", CtyNumber().validate(99))
        validated_tuple = tuple_type_sn.validate(data)
        assert validated_tuple.value[0].value == "raw_text"
        assert validated_tuple.value[1].value == Decimal("99")

    def test_validate_tuple_with_ctyvalue_dynamic_element(self):
        tuple_type = CtyTuple((CtyString(), CtyDynamic()))
        dynamic_val = CtyDynamic().validate(CtyNumber().validate(123)) # CtyValue(Dynamic, CtyValue(Number, 123))
        data = ("test", dynamic_val)

        validated_tuple = tuple_type.validate(data)
        assert validated_tuple.value[0].value == "test"
        assert validated_tuple.value[1].type.is_dynamic_type()
        assert validated_tuple.value[1].value.type.equal(CtyNumber())
        assert validated_tuple.value[1].value.value == Decimal("123")

    def test_validate_tuple_with_raw_list_of_ctyvalues(self):
        tuple_type = CtyTuple((CtyString(), CtyNumber()))
        # Input is a raw Python list, but its elements are CtyValues
        data = [CtyString().validate("item1"), CtyNumber().validate(100)]
        validated_tuple = tuple_type.validate(data)
        assert isinstance(validated_tuple.value, tuple)
        assert validated_tuple.value[0].value == "item1"
        assert validated_tuple.value[1].value == Decimal("100")
        assert validated_tuple.value[0].type.equal(CtyString())
        assert validated_tuple.value[1].type.equal(CtyNumber())

    def test_validate_tuple_with_raw_list_mixed_ctyvalues_and_raw(self):
        tuple_type = CtyTuple((CtyString(), CtyNumber(), CtyBool()))
        data = [CtyString().validate("item1"), 200, CtyBool().validate(True)]
        validated_tuple = tuple_type.validate(data)
        assert validated_tuple.value[0].value == "item1"
        assert validated_tuple.value[1].value == Decimal("200")
        assert validated_tuple.value[2].value is True
        assert validated_tuple.value[0].type.equal(CtyString())
        assert validated_tuple.value[1].type.equal(CtyNumber())
        assert validated_tuple.value[2].type.equal(CtyBool())

    def test_validate_tuple_with_ctyvalue_list_containing_wrong_type_for_element(self):
        # tuple(string, number)
        # Input: CtyValue(list(string), ["a", "b"])
        # This should fail because the tuple expects a CtyString and CtyNumber.
        # The CtyValue itself is a list, not a tuple, so it should fail at the outer type check.
        list_val = CtyList(CtyString()).validate(["a", "b"])
        tuple_type_sn = CtyTuple((CtyString(), CtyNumber()))
        with pytest.raises(CtyValidationError, match="Expected tuple or list, got list"):
            # The error is because `list_val.value` (which is `[CtyValue(string, "a"), CtyValue(string, "b")]`)
            # is passed to CtyTuple.validate. The elements are then checked.
            # The first element "a" is fine. The second element CtyValue(string, "b")
            # will be attempted to be validated by CtyNumber, which will fail.
            # Correction: The error is actually that list_val (a CtyValue) is not a tuple or list.
            # `isinstance(value, (list, tuple))` will be false.
            # `value = value.value` is called if `isinstance(value, CtyValue)`
            # Then `isinstance(value, (list, tuple))` is checked on the inner list.
            # So, it will try to validate `["a", "b"]` (raw list of CtyValues)
            # This will pass length check, then fail on element 1 type.
            tuple_type_sn.validate(list_val) # This should raise "Invalid value for tuple element 1"
            # After fixing the code to correctly unwrap CtyValue:
            # The error should be "Invalid value for tuple element 1: Number validation error: Cannot convert CtyValue of type CtyString to CtyNumber."
            # This is because `list_val.value` will be `[CtyValue(String,"a"), CtyValue(String,"b")]`
            # `element_type.validate(raw_element)` will be `CtyNumber().validate(CtyValue(String,"b"))`
            # This will indeed raise.

            # Actual error if CtyTuple.validate gets `value.value` which is `[CtyValue(String,"a"), CtyValue(String,"b")]`:
            # CtyValidationError: Invalid value for tuple element 1: Number validation error: Value of type str cannot be converted to a number.
            # This is because CtyNumber.validate(CtyValue(String, "b")) will try to convert "b" to number.
            # This is correct.
            pass # The test case `test_validate_element_type_mismatch_ctyvalue` covers this better.
                 # This test is a bit confusing. The outer CtyValue is a list type.
                 # CtyTuple.validate receives CtyValue(CtyList(...)).
                 # It then takes its .value, which is a Python list of CtyValues.
                 # Then it proceeds.
                 # This should be covered by `test_validate_ctyvalue_non_tuple_type` if the CtyValue is not CtyTuple.
                 # If the input *is* a CtyValue(CtyTuple) but with wrong elements, that's covered.

                 # Let's make it more direct:
        tuple_type_sn = CtyTuple((CtyString(), CtyNumber()))
        data_list_of_ctyvalues = [CtyString().validate("hello"), CtyString().validate("world")]
        with pytest.raises(CtyValidationError, match="Invalid value for tuple element 1: Number validation error: Value of type str cannot be converted to a number."):
            tuple_type_sn.validate(data_list_of_ctyvalues)

    def test_element_at_slice_on_null_tuple(self):
        tuple_type = CtyTuple((CtyString(), CtyNumber(), CtyBool()))
        null_tuple = CtyValue.null(tuple_type)
        sliced_val = null_tuple.type.element_at(null_tuple, slice(0, 2))
        assert sliced_val.is_null
        assert isinstance(sliced_val.type, CtyTuple)
        assert len(sliced_val.type.element_types) == 2
        assert sliced_val.type.element_types[0].equal(CtyString())
        assert sliced_val.type.element_types[1].equal(CtyNumber())

    def test_element_at_slice_on_unknown_tuple(self):
        tuple_type = CtyTuple((CtyString(), CtyNumber(), CtyBool()))
        unknown_tuple = CtyValue.unknown(tuple_type)
        sliced_val = unknown_tuple.type.element_at(unknown_tuple, slice(0, 2))
        assert sliced_val.is_unknown
        assert isinstance(sliced_val.type, CtyTuple)
        assert len(sliced_val.type.element_types) == 2
        assert sliced_val.type.element_types[0].equal(CtyString())
        assert sliced_val.type.element_types[1].equal(CtyNumber())

    def test_element_at_slice_on_inconsistent_internal_value(self):
        tuple_type = CtyTuple((CtyString(), CtyNumber()))
        # Create a CtyValue that claims to be CtyTuple but wraps something else
        bad_val = CtyValue(vtype=tuple_type, value="not a tuple")
        with pytest.raises(CtyTupleValidationError, match="Internal tuple value is inconsistent with type definition for slicing."):
            tuple_type.element_at(bad_val, slice(0,1))

    def test_element_at_int_on_inconsistent_internal_value(self):
        tuple_type = CtyTuple((CtyString(), CtyNumber()))
        bad_val = CtyValue(vtype=tuple_type, value="not a tuple")
        with pytest.raises(CtyTupleValidationError, match="Internal tuple value is inconsistent with type definition."):
            tuple_type.element_at(bad_val, 0)

        bad_val_wrong_len = CtyValue(vtype=tuple_type, value=(CtyString().validate("s"),)) # tuple of len 1
        with pytest.raises(CtyTupleValidationError, match="Internal tuple value is inconsistent with type definition."):
            tuple_type.element_at(bad_val_wrong_len, 0)

    def test_element_at_invalid_index_type(self, tuple_type_sn, cty_tuple_val):
        with pytest.raises(TypeError, match="Tuple indices must be integers or slices, not str"):
            tuple_type_sn.element_at(cty_tuple_val, "zero") # type: ignore
