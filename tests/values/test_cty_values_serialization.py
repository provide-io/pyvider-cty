# tests/values/test_cty_values_serialization.py
# 🐍🧪🔒

from decimal import Decimal
import json  # Added for test_deserialization_corrupted_data

import msgpack  # Added for test_deserialization_corrupted_data
import pytest

# CtyValue and CtyType imports
from pyvider.cty import CtyValue
from pyvider.cty.marks import CtyMark
from pyvider.cty.types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyType,  # Base type, useful for isinstance checks if needed
)


# Helper to make test cases more concise
def check_serialization_deserialization(
    original_value: CtyValue, target_type: CtyType
) -> None:
    """
    Checks JSON and Msgpack serialization and deserialization for a CtyValue.
    """
    # JSON Serialization/Deserialization
    json_str = original_value.to_json_string()
    deserialized_json = CtyValue.from_json_string(json_str, target_type)

    assert original_value.type.equal(deserialized_json.type), (
        f"JSON: Type mismatch after deserialization. Expected {original_value.type}, got {deserialized_json.type}"
    )
    assert original_value == deserialized_json, (
        f"JSON: Value mismatch. Original: {original_value!r}, Deserialized: {deserialized_json!r}"
    )
    assert original_value.is_null == deserialized_json.is_null, (
        "JSON: Null status mismatch"
    )
    assert original_value.is_unknown == deserialized_json.is_unknown, (
        "JSON: Unknown status mismatch"
    )
    # is_known is implicitly covered by is_null and is_unknown
    assert original_value._marks == deserialized_json._marks, "JSON: Marks mismatch"

    # Msgpack Serialization/Deserialization
    msgpack_bytes = original_value.to_msgpack_bytes()
    deserialized_msgpack = CtyValue.from_msgpack_bytes(msgpack_bytes, target_type)

    assert original_value.type.equal(deserialized_msgpack.type), (
        f"Msgpack: Type mismatch. Expected {original_value.type}, got {deserialized_msgpack.type}"
    )
    assert original_value == deserialized_msgpack, (
        f"Msgpack: Value mismatch. Original: {original_value!r}, Deserialized: {deserialized_msgpack!r}"
    )
    assert original_value.is_null == deserialized_msgpack.is_null, (
        "Msgpack: Null status mismatch"
    )
    assert original_value.is_unknown == deserialized_msgpack.is_unknown, (
        "Msgpack: Unknown status mismatch"
    )
    # is_known is implicitly covered by is_null and is_unknown
    assert original_value._marks == deserialized_msgpack._marks, (
        "Msgpack: Marks mismatch"
    )


# --- Test Cases ---


def test_string_serialization() -> None:
    original_value = CtyString().validate("hello world")
    check_serialization_deserialization(original_value, CtyString())

    original_value_empty = CtyString().validate("")
    check_serialization_deserialization(original_value_empty, CtyString())


def test_number_serialization() -> None:
    original_value_int = CtyNumber().validate(Decimal("123"))
    check_serialization_deserialization(original_value_int, CtyNumber())

    original_value_float = CtyNumber().validate(Decimal("123.456"))
    check_serialization_deserialization(original_value_float, CtyNumber())

    original_value_zero = CtyNumber().validate(Decimal("0"))
    check_serialization_deserialization(original_value_zero, CtyNumber())


def test_bool_serialization() -> None:
    original_value_true = CtyBool().validate(True)
    check_serialization_deserialization(original_value_true, CtyBool())

    original_value_false = CtyBool().validate(False)
    check_serialization_deserialization(original_value_false, CtyBool())


def test_list_serialization_simple() -> None:
    list_type = CtyList(element_type=CtyString())
    original_value = list_type.validate(["a", "b", "c"])
    check_serialization_deserialization(original_value, list_type)

    list_type_empty = CtyList(element_type=CtyNumber())
    original_value_empty = list_type_empty.validate([])
    check_serialization_deserialization(original_value_empty, list_type_empty)


def test_list_serialization_nested() -> None:
    nested_list_type = CtyList(element_type=CtyList(element_type=CtyNumber()))
    data = [[Decimal("1"), Decimal("2")], [Decimal("3")]]
    # Need to create CtyValues for inner lists if validate expects that
    # Assuming validate can handle raw python lists of appropriate types for now
    # If not, this would be:
    # data = [CtyList(element_type=CtyNumber()).validate([Decimal("1"), Decimal("2")]), CtyList(element_type=CtyNumber()).validate([Decimal("3")])]
    # However, the current CtyValue structure stores raw python values internally after validation.
    original_value = nested_list_type.validate(data)
    check_serialization_deserialization(original_value, nested_list_type)


def test_map_serialization_simple() -> None:
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    original_value = map_type.validate({"a": Decimal("1"), "b": Decimal("2")})
    check_serialization_deserialization(original_value, map_type)

    map_type_empty = CtyMap(key_type=CtyString(), value_type=CtyString())
    original_value_empty = map_type_empty.validate({})
    check_serialization_deserialization(original_value_empty, map_type_empty)


def test_map_serialization_nested() -> None:
    # map of lists of strings
    map_type_nested = CtyMap(
        key_type=CtyString(), value_type=CtyList(element_type=CtyString())
    )
    data = {"list1": ["x", "y"], "list2": ["z"]}
    original_value = map_type_nested.validate(data)
    check_serialization_deserialization(original_value, map_type_nested)


def test_object_serialization_simple() -> None:
    object_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
    data = {"name": "Alice", "age": Decimal("30")}
    original_value = object_type.validate(data)
    check_serialization_deserialization(original_value, object_type)

    object_type_empty_schema = CtyObject({})
    original_value_empty_obj = object_type_empty_schema.validate({})
    check_serialization_deserialization(
        original_value_empty_obj, object_type_empty_schema
    )


def test_object_serialization_nested() -> None:
    nested_object_type = CtyObject(
        {
            "id": CtyString(),
            "data": CtyObject(
                {"value": CtyNumber(), "tags": CtyList(element_type=CtyString())}
            ),
        }
    )
    data = {
        "id": "item123",
        "data": {"value": Decimal("101.5"), "tags": ["tagA", "tagB"]},
    }
    original_value = nested_object_type.validate(data)
    check_serialization_deserialization(original_value, nested_object_type)


def test_tuple_serialization_simple() -> None:
    tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))
    data = ("hello", Decimal("42"), True)
    original_value = tuple_type.validate(data)
    check_serialization_deserialization(original_value, tuple_type)

    tuple_type_empty = CtyTuple(element_types=())
    original_value_empty = tuple_type_empty.validate(())
    check_serialization_deserialization(original_value_empty, tuple_type_empty)


def test_tuple_serialization_nested() -> None:
    tuple_type_nested = CtyTuple(
        element_types=(
            CtyString(),
            CtyList(element_type=CtyNumber()),
            CtyObject({"name": CtyString()}),
        )
    )
    data = (
        "tuple_id",
        [Decimal("1"), Decimal("2"), Decimal("3")],
        {"name": "NestedObjInTuple"},
    )
    original_value = tuple_type_nested.validate(data)
    check_serialization_deserialization(original_value, tuple_type_nested)


# Tests for special states: null, unknown


def test_null_value_serialization() -> None:
    null_string = CtyValue.null(CtyString())
    check_serialization_deserialization(null_string, CtyString())

    null_list_of_numbers = CtyValue.null(CtyList(element_type=CtyNumber()))
    check_serialization_deserialization(
        null_list_of_numbers, CtyList(element_type=CtyNumber())
    )

    complex_object_type = CtyObject(
        {"a": CtyString(), "b": CtyList(element_type=CtyNumber())}
    )
    null_object = CtyValue.null(complex_object_type)
    check_serialization_deserialization(null_object, complex_object_type)


def test_unknown_value_serialization() -> None:
    unknown_number = CtyValue.unknown(CtyNumber())
    check_serialization_deserialization(unknown_number, CtyNumber())

    unknown_map_of_bools = CtyValue.unknown(
        CtyMap(key_type=CtyString(), value_type=CtyBool())
    )
    check_serialization_deserialization(
        unknown_map_of_bools, CtyMap(key_type=CtyString(), value_type=CtyBool())
    )

    complex_tuple_type = CtyTuple(
        element_types=(CtyString(), CtyObject({"id": CtyNumber()}))
    )
    unknown_tuple = CtyValue.unknown(complex_tuple_type)
    check_serialization_deserialization(unknown_tuple, complex_tuple_type)


# Tests for values with marks


def test_marked_value_serialization() -> None:
    mark1 = CtyMark("sensitive")
    mark2 = CtyMark(
        "source", "user_input"
    )  # Assuming CtyMark can take value or details

    # Marked string
    string_val = CtyString().validate("secret data").mark(mark1).mark(mark2)
    check_serialization_deserialization(string_val, CtyString())

    # Marked list (mark on the list itself, not elements)
    list_type = CtyList(element_type=CtyNumber())
    marked_list = list_type.validate([Decimal("10"), Decimal("20")]).mark(mark1)
    check_serialization_deserialization(marked_list, list_type)

    # Marked object
    obj_type = CtyObject({"key": CtyString()})
    marked_obj = obj_type.validate({"key": "value"}).mark(mark2)
    check_serialization_deserialization(marked_obj, obj_type)


# Test with CtyDynamic (value should resolve before serialization ideally)
# Serialization of CtyDynamic itself is tricky as its type is not fixed.
# The current codec is designed around target_type for deserialization.
# If a CtyValue is CtyDynamic().validate(CtyString().validate("foo")),
# it becomes CtyValue(CtyString, "foo"). So serialization uses the concrete type.


def test_dynamic_value_resolved_serialization() -> None:
    # When a dynamic value resolves to a concrete type
    concrete_string = CtyString().validate("dynamic turned string")
    dynamic_val_holding_string = CtyDynamic().validate(concrete_string)

    # The type of dynamic_val_holding_string should be CtyDynamic, wrapping the CtyString
    assert isinstance(dynamic_val_holding_string.type, CtyDynamic)
    assert isinstance(dynamic_val_holding_string.value, CtyValue)
    assert dynamic_val_holding_string.value.type.equal(CtyString())
    # Now check serialization for the dynamic_val_holding_string itself, expecting it as CtyDynamic
    check_serialization_deserialization(dynamic_val_holding_string, CtyDynamic())

    concrete_number_val = CtyNumber().validate(Decimal("123"))
    dynamic_val_holding_number = CtyDynamic().validate(concrete_number_val)
    assert isinstance(dynamic_val_holding_number.type, CtyDynamic)
    assert isinstance(dynamic_val_holding_number.value, CtyValue)
    assert dynamic_val_holding_number.value.type.equal(CtyNumber())
    check_serialization_deserialization(dynamic_val_holding_number, CtyDynamic())


# Potentially add tests for CtySet if it's a distinct type with specific serialization needs.
# For now, assuming CtySet is handled by generic collection logic if its values are standard.
# Example:
# def test_set_serialization():
#     set_type = CtySet(element_type=CtyString())
#     # Note: CtySet validation might convert to frozenset of CtyValues internally
#     original_value = set_type.validate({"apple", "banana"})
#     check_serialization_deserialization(original_value, set_type)


# Test for potential errors during deserialization
def test_deserialization_type_mismatch() -> None:
    # Serialize a number
    original_value = CtyNumber().validate(Decimal("123"))
    json_str = original_value.to_json_string()

    # Try to deserialize as a string (should fail or handle gracefully)
    with pytest.raises(ValueError, match="Type mismatch"):  # Or specific Cty...Error
        CtyValue.from_json_string(json_str, CtyString())

    msgpack_bytes = original_value.to_msgpack_bytes()
    with pytest.raises(ValueError, match="Type mismatch"):
        CtyValue.from_msgpack_bytes(msgpack_bytes, CtyString())


def test_deserialization_corrupted_data() -> None:
    # Invalid JSON
    json_str_invalid = '{"type_name": "string", "value": "test", "is_null": false, "is_unknown": false, "marks": ['  # Incomplete
    with pytest.raises(json.JSONDecodeError):
        CtyValue.from_json_string(json_str_invalid, CtyString())

    # Invalid Msgpack (e.g., truncated bytes - hard to simulate reliably without knowing format)
    # For now, assume msgpack library handles basic corruption.
    # Test with non-dict root for msgpack
    invalid_msgpack_bytes = msgpack.packb("just a string")
    with pytest.raises(ValueError, match="Invalid Msgpack data: root must be a map"):
        CtyValue.from_msgpack_bytes(invalid_msgpack_bytes, CtyString())

    # Data that is valid msgpack/json but not a valid CtyValue structure
    valid_json_wrong_structure = json.dumps(
        {"foo": "bar"}
    )  # Not the expected CtyValue dict
    with pytest.raises(
        ValueError
    ):  # Or more specific error if _serializable_to_value checks fields
        CtyValue.from_json_string(valid_json_wrong_structure, CtyString())


# Test case from problem description example
def test_problem_description_string_serialization() -> None:
    original_value = CtyString().validate("hello")
    # JSON
    json_str = original_value.to_json_string()
    deserialized_json = CtyValue.from_json_string(json_str, CtyString())
    assert original_value == deserialized_json
    assert deserialized_json.type.equal(CtyString())  # Also ensure .type.equal here
    # Msgpack
    msgpack_bytes = original_value.to_msgpack_bytes()
    deserialized_msgpack = CtyValue.from_msgpack_bytes(msgpack_bytes, CtyString())
    assert original_value == deserialized_msgpack
    assert deserialized_msgpack.type.equal(CtyString())  # Also ensure .type.equal here


# --- Tests for CtyDynamic with embedded types ---


def test_dynamic_wrapping_string_serialization() -> None:
    """Test CtyDynamic wrapping CtyString serialization and deserialization."""
    inner_val = CtyValue.string("hello")
    # When a CtyValue is assigned to a CtyDynamic, CtyDynamic's validate() should
    # store the CtyValue itself if it's already a CtyValue.
    dynamic_val = CtyDynamic().validate(inner_val)

    # Check that the type of dynamic_val is indeed CtyDynamic, but its internal value is the CtyString CtyValue
    assert isinstance(dynamic_val.type, CtyDynamic), "Outer type should be CtyDynamic"
    assert isinstance(dynamic_val.value, CtyValue), (
        "Inner value should be a CtyValue instance"
    )
    assert isinstance(dynamic_val.value.type, CtyString), (
        "Inner CtyValue's type should be CtyString"
    )
    assert dynamic_val.value.value == "hello", "Inner CtyValue's raw value is incorrect"

    # Serialization (via to_json_comparable_dict, which to_json_string uses)
    # Expected structure:
    # {
    #   "type_name": "dynamic",
    #   "value": {"type": "string", "value": "hello"},  <-- This is the embedded part
    #   "is_unknown": False,
    #   "is_null": False,
    #   "marks": []
    # }
    # Note: JsonEncoder might wrap this further, but CtyValue.to_json_string uses CtyValue.to_json_comparable_dict
    # which is then passed to json.dumps by the codec.

    json_str = dynamic_val.to_json_string()
    parsed_json = json.loads(json_str)

    assert parsed_json["type_name"] == "dynamic"
    assert parsed_json["value"] == {"type": "string", "value": "hello"}
    assert not parsed_json["is_unknown"]
    assert not parsed_json["is_null"]
    assert parsed_json["marks"] == []

    # Deserialization
    deserialized_dynamic = CtyValue.from_json_string(json_str, CtyDynamic())

    assert isinstance(deserialized_dynamic, CtyValue)
    assert isinstance(deserialized_dynamic.type, CtyDynamic)
    assert not deserialized_dynamic.is_unknown
    assert not deserialized_dynamic.is_null

    # Check the wrapped value
    inner_deserialized = deserialized_dynamic.value
    assert isinstance(inner_deserialized, CtyValue)
    assert isinstance(inner_deserialized.type, CtyString)
    assert inner_deserialized.value == "hello"


def test_dynamic_wrapping_number_serialization() -> None:
    """Test CtyDynamic wrapping CtyNumber."""
    inner_val = CtyValue.number(Decimal("123.45"))
    dynamic_val = CtyDynamic().validate(inner_val)

    json_str = dynamic_val.to_json_string()
    parsed_json = json.loads(json_str)

    assert parsed_json["type_name"] == "dynamic"
    assert parsed_json["value"] == {"type": "number", "value": "123.45"}
    assert not parsed_json["is_unknown"]
    assert not parsed_json["is_null"]

    deserialized_dynamic = CtyValue.from_json_string(json_str, CtyDynamic())
    assert isinstance(deserialized_dynamic.type, CtyDynamic)
    inner_deserialized = deserialized_dynamic.value
    assert isinstance(inner_deserialized, CtyValue)
    assert isinstance(inner_deserialized.type, CtyNumber)
    assert inner_deserialized.value == Decimal("123.45")


def test_dynamic_wrapping_bool_serialization() -> None:
    """Test CtyDynamic wrapping CtyBool."""
    inner_val = CtyValue.bool(True)
    dynamic_val = CtyDynamic().validate(inner_val)

    json_str = dynamic_val.to_json_string()
    parsed_json = json.loads(json_str)

    assert parsed_json["type_name"] == "dynamic"
    assert parsed_json["value"] == {"type": "bool", "value": True}
    assert not parsed_json["is_unknown"]
    assert not parsed_json["is_null"]

    deserialized_dynamic = CtyValue.from_json_string(json_str, CtyDynamic())
    assert isinstance(deserialized_dynamic.type, CtyDynamic)
    inner_deserialized = deserialized_dynamic.value
    assert isinstance(inner_deserialized, CtyValue)
    assert isinstance(inner_deserialized.type, CtyBool)
    assert inner_deserialized.value is True


def test_dynamic_wrapping_null_serialization() -> None:
    """Test CtyDynamic that is null (not wrapping a typed null CtyValue)."""
    # This CtyDynamic value itself is null.
    dynamic_null_val = CtyValue.null(CtyDynamic())

    json_str = dynamic_null_val.to_json_string()
    parsed_json = json.loads(json_str)

    assert parsed_json["type_name"] == "dynamic"
    assert parsed_json["value"] is None  # For null values, "value" is None
    assert not parsed_json["is_unknown"]
    assert parsed_json["is_null"] is True  # The dynamic value itself is null

    deserialized_dynamic = CtyValue.from_json_string(json_str, CtyDynamic())
    assert isinstance(deserialized_dynamic.type, CtyDynamic)
    assert not deserialized_dynamic.is_unknown
    assert deserialized_dynamic.is_null  # Should be null
    assert deserialized_dynamic.value is None  # Raw value of a null CtyValue is None


def test_dynamic_wrapping_unknown_serialization() -> None:
    """Test CtyDynamic that is unknown."""
    # This CtyDynamic value itself is unknown.
    dynamic_unknown_val = CtyValue.unknown(CtyDynamic())

    json_str = dynamic_unknown_val.to_json_string()
    parsed_json = json.loads(json_str)

    assert parsed_json["type_name"] == "dynamic"
    assert parsed_json["value"] is None  # For unknown values, "value" is None
    assert parsed_json["is_unknown"] is True  # The dynamic value itself is unknown
    assert not parsed_json["is_null"]

    deserialized_dynamic = CtyValue.from_json_string(json_str, CtyDynamic())
    assert isinstance(deserialized_dynamic.type, CtyDynamic)
    assert deserialized_dynamic.is_unknown  # Should be unknown
    assert not deserialized_dynamic.is_null
    with pytest.raises(ValueError, match="Cannot get raw value of unknown value"):
        _ = deserialized_dynamic.value  # Accessing .value of unknown raises error


# 🐍🧪🔒
