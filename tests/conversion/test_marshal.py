import pytest
from unittest import mock

from pyvider.cty.conversion.marshal import marshal_type, unmarshal_type, TypeCategory
from pyvider.cty.types import (
    CtyString, CtyNumber, CtyBool, CtyDynamic, CtyList, CtyMap, CtySet, CtyObject, CtyTuple
)
from pyvider.cty.exceptions import CtyConversionError, CtyTypeConversionError


# Tests for unmarshal_type
class TestUnmarshalType:

    def test_unmarshal_type_unicode_decode_error(self):
        """Test UnicodeDecodeError when type_bytes is not valid UTF-8."""
        with pytest.raises(CtyTypeConversionError, match="Type bytes are not valid UTF-8"):
            unmarshal_type(b"\xff\xfe\x00\x00s\x00t\x00r\x00i\x00n\x00g\x00")

    @mock.patch("pyvider.cty.conversion.marshal._standardize_type_string", side_effect=Exception("Mocked standardization error"))
    def test_unmarshal_type_standardize_exception(self, mock_standardize_private):
        """Test generic Exception during _standardize_type_string."""
        with pytest.raises(CtyTypeConversionError, match="Unexpected error standardizing type string: Mocked standardization error"):
            unmarshal_type(b'"string"')

    @mock.patch("pyvider.cty.conversion.marshal._classify_type", side_effect=Exception("Mocked classification error"))
    def test_unmarshal_type_classify_exception(self, mock_classify_private):
        """Test generic Exception during _classify_type."""
        with pytest.raises(CtyTypeConversionError, match="Unexpected error classifying type string: Mocked classification error"):
            unmarshal_type(b'"string"')

    def test_unmarshal_type_empty_bytes(self):
        """Test unmarshal_type with empty type_bytes returns CtyDynamic."""
        assert isinstance(unmarshal_type(b''), CtyDynamic)
        assert isinstance(unmarshal_type(b'""'), CtyDynamic)

    def test_unmarshal_type_unknown_primitive(self):
        """Test unknown primitive type raises CtyTypeConversionError."""
        with pytest.raises(CtyTypeConversionError, match="Unknown or malformed CTY type string format: unknown_primitive"):
            unmarshal_type(b'"unknown_primitive"')

    def test_unmarshal_type_unsupported_collection_format(self):
        """Test unsupported collection type format (e.g., 'foo(string)')."""
        with pytest.raises(CtyTypeConversionError, match="Unknown or malformed CTY type string format: foo\\(string\\)"):
            unmarshal_type(b'"foo(string)"')

    @mock.patch("pyvider.cty.conversion.marshal._classify_type", return_value=TypeCategory.UNKNOWN)
    def test_unmarshal_type_unknown_type_category(self, mock_classify_private):
        """Test unknown type format (TypeCategory.UNKNOWN)."""
        with pytest.raises(CtyTypeConversionError, match="Unknown or malformed CTY type string format: unknown_type_str"):
            unmarshal_type(b'"unknown_type_str"')

    def test_unmarshal_type_parse_collection_value_error_empty_inner(self):
        """Test 'list()' is normalized to 'list(dynamic)'."""
        result = unmarshal_type(b'"list()"')
        assert isinstance(result, CtyList)
        assert isinstance(result.element_type, CtyDynamic)

    def test_unmarshal_type_parse_collection_value_error_unclosed(self):
        """Test 'list(string' (unclosed) is treated as malformed."""
        with pytest.raises(CtyTypeConversionError, match="Unknown or malformed CTY type string format: list\\(string"):
            unmarshal_type(b'"list(string"')

    def test_unmarshal_type_parse_collection_malformed_inner(self):
        """Test 'list(map())' is normalized to 'list(map(dynamic))'."""
        result = unmarshal_type(b'"list(map())"')
        assert isinstance(result, CtyList)
        assert isinstance(result.element_type, CtyMap)
        assert isinstance(result.element_type.key_type, CtyString)
        assert isinstance(result.element_type.value_type, CtyDynamic)


    # Successful unmarshalling of primitives
    @pytest.mark.parametrize("type_bytes, expected_type", [
        (b'"string"', CtyString),
        (b'"number"', CtyNumber),
        (b'"bool"', CtyBool),
        (b'"dynamic"', CtyDynamic),
        (b'"null"', CtyDynamic),
        (b'', CtyDynamic),
    ])
    def test_unmarshal_primitive_types_success(self, type_bytes, expected_type):
        assert isinstance(unmarshal_type(type_bytes), expected_type)

    # Successful unmarshalling of collections
    @pytest.mark.parametrize("type_bytes, expected_outer_type, expected_inner_type_str", [
        (b'"list(string)"', CtyList, "CtyString"),
        (b'"map(number)"', CtyMap, "CtyNumber"),
        (b'"set(bool)"', CtySet, "CtyBool"),
        (b'"list(dynamic)"', CtyList, "CtyDynamic"),
        (b'"map(dynamic)"', CtyMap, "CtyDynamic"),
        (b'"set(dynamic)"', CtySet, "CtyDynamic"),
    ])
    def test_unmarshal_collection_types_success(self, type_bytes, expected_outer_type, expected_inner_type_str):
        unmarshalled = unmarshal_type(type_bytes)
        assert isinstance(unmarshalled, expected_outer_type)
        if isinstance(unmarshalled, (CtyList, CtySet)):
            assert unmarshalled.element_type.__class__.__name__ == expected_inner_type_str
        elif isinstance(unmarshalled, CtyMap):
            assert unmarshalled.value_type.__class__.__name__ == expected_inner_type_str
            assert isinstance(unmarshalled.key_type, CtyString)

    def test_unmarshal_nested_collection_success(self):
        """Test successful unmarshalling of nested collection types."""
        unmarshalled = unmarshal_type(b'"list(map(string))"')
        assert isinstance(unmarshalled, CtyList)
        assert isinstance(unmarshalled.element_type, CtyMap)
        assert isinstance(unmarshalled.element_type.key_type, CtyString)
        assert isinstance(unmarshalled.element_type.value_type, CtyString)

        unmarshalled_set = unmarshal_type(b'"set(list(number))"')
        assert isinstance(unmarshalled_set, CtySet)
        assert isinstance(unmarshalled_set.element_type, CtyList)
        assert isinstance(unmarshalled_set.element_type.element_type, CtyNumber)


# Tests for marshal_type
class TestMarshalType:

    @mock.patch("pyvider.cty.conversion.marshal._normalize_type_object", side_effect=Exception("Mocked normalization error"))
    def test_marshal_type_normalize_exception(self, mock_normalize_private):
        """Test generic Exception during _normalize_type_object."""
        with pytest.raises(CtyTypeConversionError, match="Unexpected error marshalling type: Mocked normalization error"):
            marshal_type(CtyString())

    # Successful marshalling of CtyType instances
    @pytest.mark.parametrize("cty_type_instance, expected_bytes", [
        (CtyString(), b'"string"'),
        (CtyNumber(), b'"number"'),
        (CtyBool(), b'"bool"'),
        (CtyDynamic(), b'"dynamic"'),
        (CtyList(element_type=CtyString()), b'"list(string)"'),
        (CtyMap(key_type=CtyString(), value_type=CtyNumber()), b'"map(number)"'),
        (CtySet(element_type=CtyBool()), b'"set(bool)"'),
        (CtyList(element_type=CtyMap(key_type=CtyString(), value_type=CtyDynamic())), b'"list(map(dynamic))"'),
    ])
    def test_marshal_cty_type_instances_success(self, cty_type_instance, expected_bytes):
        assert marshal_type(cty_type_instance) == expected_bytes

    # Successful marshalling of string representations
    @pytest.mark.parametrize("type_string, expected_bytes", [
        ("string", b'"string"'),
        ("list(number)", b'"list(number)"'),
        ("map(bool)", b'"map(bool)"'),
        ("set(dynamic)", b'"set(dynamic)"'),
        ("  string  ", b'"string"'),
        ("list( map( string ) )", b'"list(map(string))"'),
    ])
    def test_marshal_type_strings_success(self, type_string, expected_bytes):
        assert marshal_type(type_string) == expected_bytes

    def test_marshal_type_invalid_input_type(self):
        """Test marshal_type with an invalid input type (not CtyType or str)."""
        with pytest.raises(CtyConversionError, match="Unhandled CTY type class: int"):
             marshal_type(123) # type: ignore

    def test_marshal_type_object_and_tuple(self):
        """Test marshalling of CtyObject and CtyTuple."""
        assert marshal_type(CtyObject({"a": CtyString()})) == b'"object({a=string})"'
        assert marshal_type(CtyTuple((CtyString(), CtyNumber()))) == b'"tuple([string, number])"' # Added space here
