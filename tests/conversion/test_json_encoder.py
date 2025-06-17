from decimal import Decimal
import json

import pytest

from pyvider.cty.conversion.formats.json import JsonEncoder
from pyvider.cty.exceptions import EncodingError
from pyvider.cty.types import (
    CtyBool,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
)
from pyvider.cty.values import CtyValue


# Helper to encode and parse JSON
def encode_and_parse(cty_value, **options):
    json_bytes = JsonEncoder.encode(cty_value, **options)
    return json.loads(json_bytes.decode('utf-8'))

def test_encode_map_of_strings() -> None:
    """Test encoding a CtyMap with CtyString values."""
    cty_map_val = CtyValue.map(
        CtyString(),
        CtyString(),
        {"key1": "value1", "key2": "value2"}
    )
    parsed_json = encode_and_parse(cty_map_val)

    assert parsed_json["type_name"] == "CtyMap"
    assert parsed_json["key_type"] == "CtyString"
    assert parsed_json["value_type"] == "CtyString"
    assert parsed_json["value"] == {"key1": "value1", "key2": "value2"}
    assert parsed_json.get("is_unknown", False) is False
    assert parsed_json.get("is_null", False) is False

def test_encode_list_of_strings() -> None:
    """Test encoding a CtyList with CtyString values."""
    cty_list_val = CtyValue.list(
        CtyString(),
        ["apple", "banana"]
    )
    parsed_json = encode_and_parse(cty_list_val)

    assert parsed_json["type_name"] == "CtyList"
    assert parsed_json["element_type"] == "CtyString"
    assert parsed_json["value"] == ["apple", "banana"]
    assert parsed_json.get("is_unknown", False) is False
    assert parsed_json.get("is_null", False) is False

def test_encode_map_of_numbers() -> None:
    """Test encoding a CtyMap with CtyNumber values."""
    cty_map_val = CtyValue.map(
        CtyString(),
        CtyNumber(),
        {"count": 10, "total": Decimal("123.45")}
    )
    parsed_json = encode_and_parse(cty_map_val)

    assert parsed_json["type_name"] == "CtyMap"
    assert parsed_json["key_type"] == "CtyString"
    assert parsed_json["value_type"] == "CtyNumber"
    assert parsed_json["value"] == {"count": "10", "total": "123.45"}
    assert parsed_json.get("is_unknown", False) is False
    assert parsed_json.get("is_null", False) is False


def test_encode_list_of_numbers() -> None:
    """Test encoding a CtyList with CtyNumber values."""
    cty_list_val = CtyValue.list(
        CtyNumber(),
        [1, 20, Decimal("3.14")]
    )
    parsed_json = encode_and_parse(cty_list_val)

    assert parsed_json["type_name"] == "CtyList"
    assert parsed_json["element_type"] == "CtyNumber"
    assert parsed_json["value"] == ["1", "20", "3.14"]
    assert parsed_json.get("is_unknown", False) is False
    assert parsed_json.get("is_null", False) is False


def test_encode_map_of_bools() -> None:
    """Test encoding a CtyMap with CtyBool values."""
    cty_map_val = CtyValue.map(
        CtyString(),
        CtyBool(),
        {"active": True, "admin": False}
    )
    parsed_json = encode_and_parse(cty_map_val)

    assert parsed_json["type_name"] == "CtyMap"
    assert parsed_json["key_type"] == "CtyString"
    assert parsed_json["value_type"] == "CtyBool"
    assert parsed_json["value"] == {"active": True, "admin": False}
    assert parsed_json.get("is_unknown", False) is False
    assert parsed_json.get("is_null", False) is False

def test_encode_list_of_bools() -> None:
    """Test encoding a CtyList with CtyBool values."""
    cty_list_val = CtyValue.list(
        CtyBool(),
        [True, False, True]
    )
    parsed_json = encode_and_parse(cty_list_val)

    assert parsed_json["type_name"] == "CtyList"
    assert parsed_json["element_type"] == "CtyBool"
    assert parsed_json["value"] == [True, False, True]
    assert parsed_json.get("is_unknown", False) is False
    assert parsed_json.get("is_null", False) is False

def test_encode_nested_map_primitive_values() -> None:
    """Test encoding a nested CtyMap where inner map values are primitive."""
    inner_map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
    outer_map_type = CtyMap(key_type=CtyString(), value_type=inner_map_type)

    cty_val = CtyValue.map(
        outer_map_type.key_type,
        outer_map_type.value_type,
        {"outer_key": CtyValue.map(
            inner_map_type.key_type,
            inner_map_type.value_type,
            {"inner_key": "inner_value"}
        )}
    )
    parsed_json = encode_and_parse(cty_val)

    assert parsed_json["type_name"] == "CtyMap"
    assert parsed_json["key_type"] == "CtyString"
    assert parsed_json["value_type"] == "CtyMap" # Outer map holds CtyMap instances

    inner_map_json = parsed_json["value"]["outer_key"]
    assert inner_map_json["type_name"] == "CtyMap"
    assert inner_map_json["key_type"] == "CtyString"
    assert inner_map_json["value_type"] == "CtyString"
    assert inner_map_json["value"] == {"inner_key": "inner_value"}

def test_encode_map_with_object_values_having_primitives() -> None:
    """Test encoding a CtyMap with CtyObject values, where object attributes are primitives."""
    obj_type = CtyObject({"name": CtyString(), "active": CtyBool()})
    map_type = CtyMap(key_type=CtyString(), value_type=obj_type)

    cty_val = CtyValue.map(
        map_type.key_type,
        map_type.value_type,
        {"user1": CtyValue.object(obj_type.attribute_types, {"name": "Alice", "active": True})}
    )
    parsed_json = encode_and_parse(cty_val)

    assert parsed_json["type_name"] == "CtyMap"
    assert parsed_json["key_type"] == "CtyString"
    assert parsed_json["value_type"] == "CtyObject"

    user1_data = parsed_json["value"]["user1"]
    assert user1_data["type_name"] == "CtyObject"
    assert user1_data["value"] == {
        "name": {"type_name": "CtyString", "value": "Alice"},
        "active": {"type_name": "CtyBool", "value": True}
    }

def test_encode_top_level_primitive_string() -> None:
    """Test encoding a top-level CtyString value."""
    cty_string_val = CtyValue.string("hello")
    parsed_json = encode_and_parse(cty_string_val)

    assert parsed_json == {"type_name": "CtyString", "value": "hello"}

def test_encode_top_level_primitive_number() -> None:
    """Test encoding a top-level CtyNumber value."""
    cty_num_val = CtyValue.number(Decimal("123.45"))
    parsed_json = encode_and_parse(cty_num_val)

    assert parsed_json == {"type_name": "CtyNumber", "value": "123.45"}


def test_encode_top_level_primitive_bool() -> None:
    """Test encoding a top-level CtyBool value."""
    cty_bool_val = CtyValue.bool(True)
    parsed_json = encode_and_parse(cty_bool_val)

    assert parsed_json == {"type_name": "CtyBool", "value": True}

def test_encode_empty_map() -> None:
    """Test encoding an empty CtyMap."""
    empty_map = CtyValue.map(CtyString(), CtyString(), {})
    parsed_json = encode_and_parse(empty_map)

    assert parsed_json["type_name"] == "CtyMap"
    assert parsed_json["key_type"] == "CtyString"
    assert parsed_json["value_type"] == "CtyString"
    assert parsed_json["value"] == {}
    assert parsed_json.get("is_null") is not True

def test_encode_empty_list() -> None:
    """Test encoding an empty CtyList."""
    empty_list = CtyValue.list(CtyString(), [])
    parsed_json = encode_and_parse(empty_list)

    assert parsed_json["type_name"] == "CtyList"
    assert parsed_json["element_type"] == "CtyString"
    assert parsed_json["value"] == []
    assert parsed_json.get("is_null") is not True

def test_encode_collection_with_null_value() -> None:
    """Test encoding a CtyMap with a null CtyString value."""
    cty_map_val = CtyValue.map(
        CtyString(),
        CtyString(),
        {"key1": "value1", "key2": CtyValue.null(CtyString())}
    )
    parsed_json = encode_and_parse(cty_map_val)

    assert parsed_json["type_name"] == "CtyMap"
    assert parsed_json["value"]["key1"] == "value1"
    assert parsed_json["value"]["key2"] == {"type_name": "CtyString", "is_null": True}

def test_encode_collection_with_unknown_value() -> None:
    """Test encoding a CtyMap with an unknown CtyString value."""
    cty_map_val = CtyValue.map(
        CtyString(),
        CtyString(),
        {"key1": "value1", "key2": CtyValue.unknown(CtyString())}
    )
    parsed_json = encode_and_parse(cty_map_val)

    assert parsed_json["type_name"] == "CtyMap"
    assert parsed_json["value"]["key1"] == "value1"
    assert parsed_json["value"]["key2"] == {"type_name": "CtyString", "is_unknown": True}

def test_encode_list_with_mixed_primitives_and_complex() -> None:
    """Test a list containing mixed primitive CtyValues and a CtyMap."""
    dynamic_list_val = CtyValue.list_of_dynamic([
        CtyValue.string("text_element"),
        CtyValue.map(key_type=CtyString(), value_type=CtyString(), items={"map_key": "map_value"}),
        CtyValue.number(123),
        CtyValue.bool(True)
    ])

    parsed_json = encode_and_parse(dynamic_list_val)

    assert parsed_json["type_name"] == "CtyList"
    assert parsed_json["element_type"] == "CtyDynamic"

    assert parsed_json["value"][0] == "text_element"
    assert parsed_json["value"][1] == {
        "type_name": "CtyMap", "key_type": "CtyString", "value_type": "CtyString",
        "value": {"map_key": "map_value"}
    }
    assert parsed_json["value"][2] == "123"
    assert parsed_json["value"][3] is True

def test_encode_map_with_mixed_primitives_and_complex_values() -> None:
    """Test a map containing mixed primitive CtyValues and a CtyList as a value."""
    dynamic_map_val = CtyValue.map_of_dynamic(
        CtyString(), # Key type
        {
            "primitive_str": CtyValue.string("hello"),
            "complex_list": CtyValue.list(element_type=CtyString(), elements=["a", "b"]),
            "primitive_num": CtyValue.number(42)
        }
    )
    parsed_json = encode_and_parse(dynamic_map_val)

    assert parsed_json["type_name"] == "CtyMap"
    assert parsed_json["key_type"] == "CtyString"
    assert parsed_json["value_type"] == "CtyDynamic"

    assert parsed_json["value"]["primitive_str"] == "hello"
    assert parsed_json["value"]["complex_list"] == {
        "type_name": "CtyList", "element_type": "CtyString",
        "value": ["a", "b"]
    }
    assert parsed_json["value"]["primitive_num"] == "42"

def test_encode_object_with_primitive_attributes() -> None:
    """Test encoding a CtyObject where attributes are primitives."""
    obj_type = CtyObject({"name": CtyString(), "age": CtyNumber(), "active": CtyBool()})
    cty_obj_val = CtyValue.object(
        obj_type.attribute_types,
        {"name": "Bob", "age": 30, "active": False}
    )
    parsed_json = encode_and_parse(cty_obj_val)

    assert parsed_json["type_name"] == "CtyObject"
    assert parsed_json["value"] == {
        "name": {"type_name": "CtyString", "value": "Bob"},
        "age": {"type_name": "CtyNumber", "value": "30"},
        "active": {"type_name": "CtyBool", "value": False}
    }

def test_encode_object_inside_list_with_primitive_attributes() -> None:
    """Test CtyObject with primitive attributes when the object is inside a CtyList."""
    obj_type = CtyObject({"id": CtyString()})
    list_of_objects = CtyValue.list(obj_type, [
        CtyValue.object(obj_type.attribute_types, {"id": "obj1"})
    ])
    parsed_json = encode_and_parse(list_of_objects)

    assert parsed_json["type_name"] == "CtyList"
    assert parsed_json["element_type"] == "CtyObject"

    object_in_list = parsed_json["value"][0]
    assert object_in_list["type_name"] == "CtyObject"
    assert object_in_list["value"] == {
        "id": {"type_name": "CtyString", "value": "obj1"}
    }

def test_decimal_serialization_in_list() -> None:
    """Ensure Decimals are serialized as strings in lists."""
    cty_list_val = CtyValue.list(CtyNumber(), [Decimal("1.23"), Decimal("4.56")])
    parsed_json = encode_and_parse(cty_list_val)
    assert parsed_json["value"] == ["1.23", "4.56"]

def test_decimal_serialization_in_map() -> None:
    """Ensure Decimals are serialized as strings in map values."""
    cty_map_val = CtyValue.map(CtyString(), CtyNumber(), {"a": Decimal("7.89")})
    parsed_json = encode_and_parse(cty_map_val)
    assert parsed_json["value"] == {"a": "7.89"}

def test_decimal_serialization_top_level() -> None:
    """Ensure Decimals are serialized as strings at the top level."""
    cty_val = CtyValue.number(Decimal("10.11"))
    parsed_json = encode_and_parse(cty_val)
    assert parsed_json["value"] == "10.11"

# Test cases for preserve_type=False
def test_encode_map_of_strings_no_preserve_type() -> None:
    cty_map_val = CtyValue.map(CtyString(), CtyString(), {"key1": "value1"})
    parsed_json = encode_and_parse(cty_map_val, preserve_type=False)
    assert parsed_json == {"value": {"key1": "value1"}}


def test_encode_list_of_strings_no_preserve_type() -> None:
    cty_list_val = CtyValue.list(CtyString(), ["apple"])
    parsed_json = encode_and_parse(cty_list_val, preserve_type=False)
    assert parsed_json == {"value": ["apple"]}

def test_encode_top_level_string_no_preserve_type() -> None:
    cty_string_val = CtyValue.string("hello")
    parsed_json = encode_and_parse(cty_string_val, preserve_type=False)
    assert parsed_json == {"value": "hello"}

def test_encode_object_no_preserve_type() -> None:
    obj_type = CtyObject({"name": CtyString()})
    cty_obj_val = CtyValue.object(obj_type.attribute_types, {"name": "Bob"})
    parsed_json = encode_and_parse(cty_obj_val, preserve_type=False)
    assert parsed_json == {"value": {"name": {"value": "Bob"}}}

def test_encode_null_string_no_preserve_type() -> None:
    cty_null_str_val = CtyValue.null(CtyString())
    parsed_json = encode_and_parse(cty_null_str_val, preserve_type=False)
    assert parsed_json == {"is_null": True}

def test_encode_unknown_string_no_preserve_type() -> None:
    cty_unknown_str_val = CtyValue.unknown(CtyString())
    parsed_json = encode_and_parse(cty_unknown_str_val, preserve_type=False)
    assert parsed_json == {"is_unknown": True}


# Tests for _create_type_from_name fallbacks and error handling via JsonEncoder.decode
def test_decode_malformed_object_type_string_fallback() -> None:
    """Test decoding JSON with a malformed object type string."""
    malformed_json_bytes = b'{"type_name": "object({name=string", "value": {}}'
    decoded_value = JsonEncoder.decode(malformed_json_bytes)
    # Log assertion removed
    assert decoded_value.type.__class__.__name__ == "CtyMap"

def test_decode_malformed_tuple_type_string_fallback() -> None:
    """Test decoding JSON with a malformed tuple type string."""
    malformed_json_bytes = b'{"type_name": "tuple([string,number", "value": []}'
    decoded_value = JsonEncoder.decode(malformed_json_bytes)
    # Log assertion removed
    assert decoded_value.type.__class__.__name__ == "CtyList"

def test_decode_unknown_type_string_fallback() -> None:
    """Test decoding JSON with an entirely unknown type string."""
    unknown_type_json_bytes = b'{"type_name": "completely_unknown_type", "value": "test"}'
    decoded_value = JsonEncoder.decode(unknown_type_json_bytes)
    # Log assertion removed
    assert decoded_value.type.__class__.__name__ == "CtyString"

def test_decode_object_type_string_with_unparseable_attribute_fallback() -> None:
    """Test object type string with an attribute that itself is unparseable."""
    json_bytes = b'{"type_name": "object({data=list(broken", "value": {"data": []}}'
    decoded_value = JsonEncoder.decode(json_bytes)
    # Log assertion removed
    assert decoded_value.type.__class__.__name__ == "CtyMap"


def test_decode_empty_object_attributes_string() -> None:
    """Test decoding an object type string with empty attributes."""
    json_bytes = b'{"type_name": "object({})", "value": {}}'
    decoded_value = JsonEncoder.decode(json_bytes)
    assert decoded_value.type.__class__.__name__ == "CtyObject"
    assert not decoded_value.type.attribute_types # No attributes

def test_decode_empty_tuple_elements_string() -> None:
    """Test decoding a tuple type string with empty elements."""
    json_bytes = b'{"type_name": "tuple([])", "value": []}'
    decoded_value = JsonEncoder.decode(json_bytes)
    assert decoded_value.type.__class__.__name__ == "CtyTuple"
    assert not decoded_value.type.element_types # No elements


# Test for _json_default
def test_json_default_decimal() -> None:
    """Test _json_default handles Decimal correctly."""
    assert JsonEncoder._json_default(Decimal("123.45")) == "123.45"

def test_json_default_unserializable() -> None:
    """Test _json_default raises TypeError for unserializable objects."""
    class Unserializable:
        pass
    with pytest.raises(TypeError, match="Object of type Unserializable is not JSON serializable"):
        JsonEncoder._json_default(Unserializable())

# Tests for JsonEncoder.decode error paths
def test_decode_invalid_json_syntax() -> None:
    """Test decoding a string that is not valid JSON."""
    invalid_json_bytes = b'{"type_name": "CtyString", value: "test"}' # Missing quotes around value key
    with pytest.raises(EncodingError, match="Invalid JSON: Expecting property name enclosed in double quotes"):
        JsonEncoder.decode(invalid_json_bytes)

def test_decode_cannot_infer_type_for_untyped_value() -> None:
    """Test decoding data where 'value' is of a type that cannot be inferred without a type_name."""
    # If 'type_name' is missing, _create_untyped_value is called.
    # It infers type based on Python type of 'value'.
    # For an empty dict, it should infer CtyMap.
    json_bytes = b'{"value": {}}'
    decoded_value = JsonEncoder.decode(json_bytes)
    assert isinstance(decoded_value, CtyValue)
    assert decoded_value.type.__class__.__name__ == "CtyMap"
    assert decoded_value.value == {}

def test_decode_typed_value_validation_error_propagates_as_encoding_error() -> None:
    """Test that a CtyValidationError during typed value creation propagates as EncodingError."""
    # CtyNumber expects a number, but we provide a string that's not a valid number representation in the value.
    json_bytes = b'{"type_name": "CtyNumber", "value": "not-a-number"}'
    # The specific error message from CtyNumberValidationError might be part of the EncodingError message.
    # We make the regex more general to accommodate this.
    with pytest.raises(EncodingError, match="Failed to convert dictionary to CtyValue.*Cannot convert string"):
        JsonEncoder.decode(json_bytes)

def test_decode_value_missing_entirely() -> None:
    """Test decoding data where the 'value' key is missing, but type_name is present."""
    # CtyNumber.validate(None) results in CtyValue.number(0)
    json_bytes = b'{"type_name": "CtyNumber"}' # No "value" key
    decoded_value = JsonEncoder.decode(json_bytes)
    assert isinstance(decoded_value, CtyValue)
    assert decoded_value.type.__class__.__name__ == "CtyNumber"
    # Value should be null if missing, not default to 0, as per CtyNumber.validate(None) behavior
    assert decoded_value.is_null
    assert isinstance(decoded_value.type, CtyNumber)

def test_decode_type_key_present_but_value_is_unsupported_for_type() -> None:
    """'type_name' suggests a CtyList, but 'value' is not a list. This should cause validation to fail."""
    json_bytes = b'{"type_name": "CtyList", "element_type": "CtyString", "value": "not-a-list"}'
    with pytest.raises(EncodingError, match="Failed to convert dictionary to CtyValue: List validation error: Expected list, tuple, or CtyValue list, got str"):
        JsonEncoder.decode(json_bytes)


# Tests for JsonEncoder.encode error paths
def test_encode_non_cty_value_raises_type_error() -> None:
    """Test encoding an object that is not a CtyValue instance."""
    # The TypeError is wrapped in an EncodingError by the encode method's try-except block
    with pytest.raises(EncodingError, match="Failed to encode to JSON: Expected CtyValue, got str"):
        JsonEncoder.encode("not a cty value")

def test_encode_internal_json_default_failure_propagates_as_encoding_error(mocker) -> None:
    """Test if json.dumps fails internally (e.g., _json_default bypassed or fails)."""
    # This is tricky to test perfectly as _json_default is robust for Decimals.
    # We can mock _value_to_dict to return something that json.dumps will fail on
    # after _json_default has been tried (if applicable).
    # Let's assume _value_to_dict produces a dict with an unserializable object.
    class UnserializableForEncode:
        pass

    mocker.patch.object(JsonEncoder, '_value_to_dict', return_value={"value": UnserializableForEncode()})
    cty_val = CtyValue.string("test") # Actual value doesn't matter due to mock

    with pytest.raises(EncodingError, match="Failed to encode to JSON: Object of type UnserializableForEncode is not JSON serializable"):
        JsonEncoder.encode(cty_val)
