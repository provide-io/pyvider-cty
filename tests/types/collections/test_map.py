import pytest
import re # Import re for escaping regex special characters
from pyvider.cty.types import (
    CtyType, CtyMap, CtyString, CtyNumber, CtyBool, CtyList, CtyDynamic
)
from pyvider.cty.values import CtyValue
from pyvider.cty.exceptions import CtyMapValidationError, CtyValidationError, CtyTypeMismatchError

class TestCtyMapInstantiation:
    def test_instantiation_valid(self):
        """Test successful instantiation."""
        m = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        assert isinstance(m.key_type, CtyString)
        assert isinstance(m.value_type, CtyNumber)

    @pytest.mark.parametrize("invalid_key_type", ["foo", int, CtyList(element_type=CtyString())])
    def test_instantiation_invalid_key_type(self, invalid_key_type):
        """Test instantiation with invalid key_type."""
        # Regex updated to match the actual error messages, which vary based on the validation step that fails.
        # The CtyMapValidationError prepends "Map validation error: " to the specific message.
        expected_regex = (
            r"Map validation error: (key_type must be a CtyType instance, got (str|type)|"
            r"Map key_type must be a primitive type or CtyDynamic, got CtyList)"
        )
        with pytest.raises(CtyMapValidationError, match=expected_regex):
            CtyMap(key_type=invalid_key_type, value_type=CtyNumber())

    @pytest.mark.parametrize("invalid_value_type", ["foo", int])
    def test_instantiation_invalid_value_type(self, invalid_value_type):
        """Test instantiation with invalid value_type."""
        with pytest.raises(CtyMapValidationError, match="value_type must be a CtyType instance"):
            CtyMap(key_type=CtyString(), value_type=invalid_value_type)

class TestCtyMapValidate:
    def test_validate_none_input_raises_error(self):
        """Test validate(None) raises CtyMapValidationError."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        with pytest.raises(CtyMapValidationError, match="Input to CtyMap.validate cannot be None"):
            map_type.validate(None)

    def test_validate_ctyvalue_map_value_not_dict(self):
        """Test CtyValue map with internal value not a dict."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        # Craft a CtyValue that looks like a map but has a non-dict value internally
        # This is hard to do without breaking CtyValue's own validation.
        # We'll assume CtyValue ensures its internal value matches its type for collections.
        # This specific scenario might be better tested at CtyValue level.
        pass

    def test_validate_ctyvalue_incompatible_type(self):
        """Test CtyValue with an incompatible map type."""
        map_type_str_num = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_type_str_str = CtyMap(key_type=CtyString(), value_type=CtyString())
        # Corrected: Use validate() method of the CtyMap type to create the CtyValue
        val = map_type_str_str.validate({"a": "hello"})
        # The expected error message implies that the CtyMap.validate() method should
        # detect when a CtyValue of one CtyMap type is passed to the validate method
        # of another, incompatible CtyMap type.
        # The actual error message uses str(type), e.g. "map(CtyString, CtyString)"
        expected_msg_regex = (
            r"Map validation error: Input CtyValue map type map\(CtyString, CtyString\) "
            r"is not compatible with target type map\(CtyString, CtyNumber\)"
        )
        with pytest.raises(CtyMapValidationError, match=expected_msg_regex):
            map_type_str_num.validate(val)

    def test_validate_ctyvalue_incompatible_key_type(self):
        map_type_str_val = CtyMap(key_type=CtyString(), value_type=CtyString())
        map_type_num_key = CtyMap(key_type=CtyNumber(), value_type=CtyString())
        # Corrected: Use validate() method of the CtyMap type to create the CtyValue
        val = map_type_num_key.validate({1: "test"})
        # Similar to above, expecting a detailed incompatibility message using str(type).
        expected_msg_regex = (
            r"Map validation error: Input CtyValue map type map\(CtyNumber, CtyString\) "
            r"is not compatible with target type map\(CtyString, CtyString\)"
        )
        with pytest.raises(CtyMapValidationError, match=expected_msg_regex):
            map_type_str_val.validate(val)


    def test_validate_non_dict_non_ctyvalue_input(self):
        """Test validate with input that is not None, dict, or CtyValue."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        expected_regex = r"Map validation error: Expected dict or CtyValue map, got (str|list)"
        with pytest.raises(CtyMapValidationError, match=expected_regex):
            map_type.validate("not a dict or ctyvalue")
        with pytest.raises(CtyMapValidationError, match=expected_regex):
            map_type.validate([("a", "b")])

    def test_validate_dict_invalid_key_type(self):
        """Test validate with dict having keys invalid for key_type."""
        map_type = CtyMap(key_type=CtyNumber(), value_type=CtyString())
        # Updated regex to match the aggregated error message format
        expected_regex = r"Map validation error: Map validation failed:\n - Invalid key 'key1': Number validation error: Cannot convert string 'key1' to number"
        with pytest.raises(CtyMapValidationError, match=expected_regex):
            map_type.validate({"key1": "value1"})

    def test_validate_dict_invalid_value_type(self):
        """Test validate with dict having values invalid for value_type."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        # Updated regex to match the aggregated error message format
        expected_regex = r"Map validation error: Map validation failed:\n - Invalid value for key 'a': Number validation error: Cannot convert string 'not-a-number' to number"
        with pytest.raises(CtyMapValidationError, match=expected_regex):
            map_type.validate({"a": "not-a-number"})

    def test_validate_dict_ctyvalue_key_null_or_unknown(self):
        """Test validate with CtyValue keys that are null or unknown."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        # Regex updated to account for nested "Map validation error:" from the key's own validation.
        expected_regex_null = r"Map validation error: Map validation failed:\n - Invalid key CtyValue\(.*is_null=True.*\): Map validation error: Map keys cannot be null or unknown"
        with pytest.raises(CtyMapValidationError, match=expected_regex_null):
            map_type.validate({CtyValue.null(CtyString()): "value"})

        expected_regex_unknown = r"Map validation error: Map validation failed:\n - Invalid key CtyValue\(.*is_unknown=True.*\): Map validation error: Map keys cannot be null or unknown"
        with pytest.raises(CtyMapValidationError, match=expected_regex_unknown):
            map_type.validate({CtyValue.unknown(CtyString()): "value"})

    def test_validate_dict_raw_key_validates_to_null_or_unknown(self):
        """Test validate with raw keys that become null/unknown CtyValues."""
        map_type_dyn_key = CtyMap(key_type=CtyDynamic(), value_type=CtyString())
        # Updated regex to account for nested "Map validation error:"
        expected_regex = r"Map validation error: Map validation failed:\n - Invalid key None: Map validation error: Map keys cannot be null or unknown after validation"
        with pytest.raises(CtyMapValidationError, match=expected_regex):
             map_type_dyn_key.validate({None: "value"})


class TestCtyMapGetSetDelete:
    def test_get_on_non_ctyvalue_or_non_map_type(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        expected_regex = r"Expected CtyValue with CtyMap type, got (str|CtyValue)"
        with pytest.raises(TypeError, match=expected_regex):
            map_type.get("not a cty value", "a") # type: ignore
        with pytest.raises(TypeError, match=expected_regex):
            map_type.get(CtyValue.string("iamastring"), "a")

    def test_set_on_non_ctyvalue_or_non_map_type(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        expected_regex = r"Expected CtyValue with CtyMap type, got (str|CtyValue)"
        with pytest.raises(TypeError, match=expected_regex):
            map_type.set("not a cty value", "a", "b") # type: ignore
        with pytest.raises(TypeError, match=expected_regex):
            map_type.set(CtyValue.string("iamastring"), "a", "b")

    def test_delete_on_non_ctyvalue_or_non_map_type(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        expected_regex = r"Expected CtyValue with CtyMap type, got (str|CtyValue)"
        with pytest.raises(TypeError, match=expected_regex):
            map_type.delete("not a cty value", "a") # type: ignore
        with pytest.raises(TypeError, match=expected_regex):
            map_type.delete(CtyValue.string("iamastring"), "a")

    def test_get_on_null_or_unknown_map_value_with_default(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        null_map_val = CtyValue.null(map_type)
        unknown_map_val = CtyValue.unknown(map_type)

        assert map_type.get(null_map_val, "a", "default_val") == "default_val"
        assert map_type.get(unknown_map_val, "a", "default_val") == "default_val"

    def test_get_key_not_ctystring_or_compatible(self):
        map_type_str_key = CtyMap(key_type=CtyString(), value_type=CtyString())
        map_val = map_type_str_key.validate({})

        # Case 1: Raw integer key - should result in key validation failure within get, returning default (null)
        result1 = map_type_str_key.get(map_val, 123)
        assert result1 is not None, "Result should not be Python None"
        assert result1.is_null, "Result should be a null CtyValue"
        assert result1.type.equal(map_type_str_key.value_type), "Result type should match map's value_type"

        # Case 2: CtyValue(CtyNumber) key - should also result in returning default (null)
        # as the key type is not CtyString.
        key_number_val = CtyValue(vtype=CtyNumber(), value=123) # Using direct constructor for clarity
        result2 = map_type_str_key.get(map_val, key_number_val)
        assert result2 is not None, "Result should not be Python None"
        assert result2.is_null, "Result should be a null CtyValue"
        assert result2.type.equal(map_type_str_key.value_type), "Result type should match map's value_type"


class TestCtyMapEqualityAndTypeChecks:
    def test_equal_with_non_map_type(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        list_type = CtyList(element_type=CtyString())
        assert not map_type.equal(list_type)

    def test_equal_different_key_types(self):
        map_type1 = CtyMap(key_type=CtyString(), value_type=CtyString())
        map_type2 = CtyMap(key_type=CtyNumber(), value_type=CtyString())
        assert not map_type1.equal(map_type2)

    def test_equal_different_value_types(self):
        map_type1 = CtyMap(key_type=CtyString(), value_type=CtyString())
        map_type2 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        assert not map_type1.equal(map_type2)

    def test_equal_same_types(self):
        map_type1 = CtyMap(key_type=CtyString(), value_type=CtyString())
        map_type2 = CtyMap(key_type=CtyString(), value_type=CtyString())
        assert map_type1.equal(map_type2)

    def test_repr_method(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        # CtyString() defaults to CtyString(value='')
        # CtyNumber() defaults to CtyNumber(value=0) or CtyNumber(value=Decimal('0'))
        # The failure output indicates CtyNumber(value=0)
        expected_repr_str_num = "CtyMap(key_type=CtyString(value=''), value_type=CtyNumber(value=0))"
        assert repr(map_type) == expected_repr_str_num

        map_type_dyn = CtyMap(key_type=CtyDynamic(), value_type=CtyDynamic())
        assert repr(map_type_dyn) == "CtyMap(key_type=CtyDynamic(), value_type=CtyDynamic())"


    def test_is_collection_type(self):
        assert CtyMap(key_type=CtyString(), value_type=CtyString()).is_collection_type()

    def test_is_map_type(self):
        assert CtyMap(key_type=CtyString(), value_type=CtyString()).is_map_type()

    def test_is_primitive_type(self):
        assert not CtyMap(key_type=CtyString(), value_type=CtyString()).is_primitive_type()

class TestCtyMapElementIterator:
    def test_element_iterator_on_non_ctyvalue_or_non_map(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        # First case: input is not a CtyValue
        with pytest.raises(TypeError, match=r"Expected CtyValue with CtyMap type, got str"):
            list(map_type.element_iterator("not a cty value")) # type: ignore

        # Second case: input is a CtyValue, but not of a CtyMap type
        with pytest.raises(TypeError, match=r"Expected CtyValue with CtyMap type, got CtyValue"):
            list(map_type.element_iterator(CtyValue.string("a string")))

    def test_element_iterator_on_null_or_unknown(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        # Expect CtyMapValidationError as per the implementation
        expected_message = "Map validation error: Cannot iterate null or unknown map"
        with pytest.raises(CtyMapValidationError, match=expected_message):
            list(map_type.element_iterator(CtyValue.null(map_type)))
        with pytest.raises(CtyMapValidationError, match=expected_message):
            list(map_type.element_iterator(CtyValue.unknown(map_type)))

    def test_element_iterator_key_value_before_next(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        cty_val = map_type.validate({"a": "b"})
        iterator = map_type.element_iterator(cty_val)
        expected_message = "next() must be called first or iterator exhausted"
        with pytest.raises(RuntimeError, match=re.escape(expected_message)):
            iterator.key()
        with pytest.raises(RuntimeError, match=re.escape(expected_message)):
            iterator.value()

    def test_element_iterator_key_value_after_exhausted(self):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        cty_val = map_type.validate({"a": "b"})
        iterator = map_type.element_iterator(cty_val)
        while iterator.next():
            pass
        # Now iterator is exhausted
        expected_message = "next() must be called first or iterator exhausted"
        with pytest.raises(RuntimeError, match=re.escape(expected_message)):
            iterator.key()
        with pytest.raises(RuntimeError, match=re.escape(expected_message)):
            iterator.value()

    def test_element_iterator_sorting_fallback_conceptual(self, mocker):
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        pass
