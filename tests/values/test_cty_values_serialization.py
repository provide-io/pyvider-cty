# tests/values/test_cty_values_serialization.py
# 🐍🧪🔒

import pytest
from decimal import Decimal

# CtyValue and CtyType imports
from pyvider.cty import CtyValue
from pyvider.cty.types import (
    CtyType, # Base type, useful for isinstance checks if needed
    CtyString,
    CtyNumber,
    CtyBool,
    CtyList,
    CtyMap,
    CtySet,
    CtyObject,
    CtyTuple,
    CtyDynamic
)
from pyvider.cty.marks import CtyMark
from pyvider.cty.exceptions import CtyValidationError

# Helper to make test cases more concise
def check_serialization_deserialization(original_value: CtyValue, target_type: CtyType):
    """
    Checks JSON and Msgpack serialization and deserialization for a CtyValue.
    """
    # JSON Serialization/Deserialization
    json_str = original_value.to_json_string()
    deserialized_json = CtyValue.from_json_string(json_str, target_type)

    assert original_value.type.equals(deserialized_json.type), \
        f"JSON: Type mismatch after deserialization. Expected {original_value.type}, got {deserialized_json.type}"
    assert original_value.equals(deserialized_json).value, \
        f"JSON: Value mismatch. Original: {original_value!r}, Deserialized: {deserialized_json!r}"
    assert original_value.is_known == deserialized_json.is_known, "JSON: Known status mismatch"
    assert original_value.is_null == deserialized_json.is_null, "JSON: Null status mismatch"
    assert original_value.is_unknown == deserialized_json.is_unknown, "JSON: Unknown status mismatch"
    assert original_value._marks == deserialized_json._marks, "JSON: Marks mismatch"


    # Msgpack Serialization/Deserialization
    msgpack_bytes = original_value.to_msgpack_bytes()
    deserialized_msgpack = CtyValue.from_msgpack_bytes(msgpack_bytes, target_type)

    assert original_value.type.equals(deserialized_msgpack.type), \
        f"Msgpack: Type mismatch. Expected {original_value.type}, got {deserialized_msgpack.type}"
    assert original_value.equals(deserialized_msgpack).value, \
        f"Msgpack: Value mismatch. Original: {original_value!r}, Deserialized: {deserialized_msgpack!r}"
    assert original_value.is_known == deserialized_msgpack.is_known, "Msgpack: Known status mismatch"
    assert original_value.is_null == deserialized_msgpack.is_null, "Msgpack: Null status mismatch"
    assert original_value.is_unknown == deserialized_msgpack.is_unknown, "Msgpack: Unknown status mismatch"
    assert original_value._marks == deserialized_msgpack._marks, "Msgpack: Marks mismatch"


# --- Test Cases ---

def test_string_serialization():
    original_value = CtyString().validate("hello world")
    check_serialization_deserialization(original_value, CtyString())

    original_value_empty = CtyString().validate("")
    check_serialization_deserialization(original_value_empty, CtyString())

def test_number_serialization():
    original_value_int = CtyNumber().validate(Decimal("123"))
    check_serialization_deserialization(original_value_int, CtyNumber())

    original_value_float = CtyNumber().validate(Decimal("123.456"))
    check_serialization_deserialization(original_value_float, CtyNumber())

    original_value_zero = CtyNumber().validate(Decimal("0"))
    check_serialization_deserialization(original_value_zero, CtyNumber())

def test_bool_serialization():
    original_value_true = CtyBool().validate(True)
    check_serialization_deserialization(original_value_true, CtyBool())

    original_value_false = CtyBool().validate(False)
    check_serialization_deserialization(original_value_false, CtyBool())

def test_list_serialization_simple():
    list_type = CtyList(CtyString())
    original_value = list_type.validate(["a", "b", "c"])
    check_serialization_deserialization(original_value, list_type)

    list_type_empty = CtyList(CtyNumber())
    original_value_empty = list_type_empty.validate([])
    check_serialization_deserialization(original_value_empty, list_type_empty)

def test_list_serialization_nested():
    nested_list_type = CtyList(CtyList(CtyNumber()))
    data = [[Decimal("1"), Decimal("2")], [Decimal("3")]]
    # Need to create CtyValues for inner lists if validate expects that
    # Assuming validate can handle raw python lists of appropriate types for now
    # If not, this would be:
    # data = [CtyList(CtyNumber()).validate([Decimal("1"), Decimal("2")]), CtyList(CtyNumber()).validate([Decimal("3")])]
    # However, the current CtyValue structure stores raw python values internally after validation.
    original_value = nested_list_type.validate(data)
    check_serialization_deserialization(original_value, nested_list_type)

def test_map_serialization_simple():
    map_type = CtyMap(CtyNumber()) # Assumes string keys
    original_value = map_type.validate({"a": Decimal("1"), "b": Decimal("2")})
    check_serialization_deserialization(original_value, map_type)

    map_type_empty = CtyMap(CtyString())
    original_value_empty = map_type_empty.validate({})
    check_serialization_deserialization(original_value_empty, map_type_empty)

def test_map_serialization_nested():
    # map of lists of strings
    map_type_nested = CtyMap(CtyList(CtyString()))
    data = {"list1": ["x", "y"], "list2": ["z"]}
    original_value = map_type_nested.validate(data)
    check_serialization_deserialization(original_value, map_type_nested)

def test_object_serialization_simple():
    object_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
    data = {"name": "Alice", "age": Decimal("30")}
    original_value = object_type.validate(data)
    check_serialization_deserialization(original_value, object_type)

    object_type_empty_schema = CtyObject({})
    original_value_empty_obj = object_type_empty_schema.validate({})
    check_serialization_deserialization(original_value_empty_obj, object_type_empty_schema)

def test_object_serialization_nested():
    nested_object_type = CtyObject({
        "id": CtyString(),
        "data": CtyObject({
            "value": CtyNumber(),
            "tags": CtyList(CtyString())
        })
    })
    data = {
        "id": "item123",
        "data": {
            "value": Decimal("101.5"),
            "tags": ["tagA", "tagB"]
        }
    }
    original_value = nested_object_type.validate(data)
    check_serialization_deserialization(original_value, nested_object_type)

def test_tuple_serialization_simple():
    tuple_type = CtyTuple([CtyString(), CtyNumber(), CtyBool()])
    data = ("hello", Decimal("42"), True)
    original_value = tuple_type.validate(data)
    check_serialization_deserialization(original_value, tuple_type)

    tuple_type_empty = CtyTuple([])
    original_value_empty = tuple_type_empty.validate(())
    check_serialization_deserialization(original_value_empty, tuple_type_empty)


def test_tuple_serialization_nested():
    tuple_type_nested = CtyTuple([
        CtyString(),
        CtyList(CtyNumber()),
        CtyObject({"name": CtyString()})
    ])
    data = (
        "tuple_id",
        [Decimal("1"), Decimal("2"), Decimal("3")],
        {"name": "NestedObjInTuple"}
    )
    original_value = tuple_type_nested.validate(data)
    check_serialization_deserialization(original_value, tuple_type_nested)

# Tests for special states: null, unknown

def test_null_value_serialization():
    null_string = CtyValue.null(CtyString())
    check_serialization_deserialization(null_string, CtyString())

    null_list_of_numbers = CtyValue.null(CtyList(CtyNumber()))
    check_serialization_deserialization(null_list_of_numbers, CtyList(CtyNumber()))

    complex_object_type = CtyObject({"a": CtyString(), "b": CtyList(CtyNumber())})
    null_object = CtyValue.null(complex_object_type)
    check_serialization_deserialization(null_object, complex_object_type)


def test_unknown_value_serialization():
    unknown_number = CtyValue.unknown(CtyNumber())
    check_serialization_deserialization(unknown_number, CtyNumber())

    unknown_map_of_bools = CtyValue.unknown(CtyMap(CtyBool()))
    check_serialization_deserialization(unknown_map_of_bools, CtyMap(CtyBool()))

    complex_tuple_type = CtyTuple([CtyString(), CtyObject({"id": CtyNumber()})])
    unknown_tuple = CtyValue.unknown(complex_tuple_type)
    check_serialization_deserialization(unknown_tuple, complex_tuple_type)


# Tests for values with marks

def test_marked_value_serialization():
    mark1 = CtyMark("sensitive")
    mark2 = CtyMark("source", "user_input") # Assuming CtyMark can take value or details

    # Marked string
    string_val = CtyString().validate("secret data").mark(mark1).mark(mark2)
    check_serialization_deserialization(string_val, CtyString())

    # Marked list (mark on the list itself, not elements)
    list_type = CtyList(CtyNumber())
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

def test_dynamic_value_resolved_serialization():
    # When a dynamic value resolves to a concrete type
    concrete_string = CtyString().validate("dynamic turned string")
    dynamic_val_holding_string = CtyDynamic().validate(concrete_string) # This should resolve type

    # The type of dynamic_val_holding_string should now be CtyString
    assert dynamic_val_holding_string.type.equals(CtyString())
    check_serialization_deserialization(dynamic_val_holding_string, CtyString())

    concrete_number_val = CtyNumber().validate(Decimal("123"))
    dynamic_val_holding_number = CtyDynamic().validate(concrete_number_val)
    assert dynamic_val_holding_number.type.equals(CtyNumber())
    check_serialization_deserialization(dynamic_val_holding_number, CtyNumber())

# Potentially add tests for CtySet if it's a distinct type with specific serialization needs.
# For now, assuming CtySet is handled by generic collection logic if its values are standard.
# Example:
# def test_set_serialization():
#     set_type = CtySet(CtyString())
#     # Note: CtySet validation might convert to frozenset of CtyValues internally
#     original_value = set_type.validate({"apple", "banana"})
#     check_serialization_deserialization(original_value, set_type)


# Test for potential errors during deserialization
def test_deserialization_type_mismatch():
    # Serialize a number
    original_value = CtyNumber().validate(Decimal("123"))
    json_str = original_value.to_json_string()

    # Try to deserialize as a string (should fail or handle gracefully)
    with pytest.raises(ValueError, match="Type mismatch"): # Or specific Cty...Error
        CtyValue.from_json_string(json_str, CtyString())

    msgpack_bytes = original_value.to_msgpack_bytes()
    with pytest.raises(ValueError, match="Type mismatch"):
        CtyValue.from_msgpack_bytes(msgpack_bytes, CtyString())


def test_deserialization_corrupted_data():
    # Invalid JSON
    json_str_invalid = '{"type_name": "string", "value": "test", "is_null": false, "is_unknown": false, "marks": [' # Incomplete
    with pytest.raises(json.JSONDecodeError):
        CtyValue.from_json_string(json_str_invalid, CtyString())

    # Invalid Msgpack (e.g., truncated bytes - hard to simulate reliably without knowing format)
    # For now, assume msgpack library handles basic corruption.
    # Test with non-dict root for msgpack
    invalid_msgpack_bytes = msgpack.packb("just a string")
    with pytest.raises(ValueError, match="Invalid Msgpack data: root must be a map"):
        CtyValue.from_msgpack_bytes(invalid_msgpack_bytes, CtyString())

    # Data that is valid msgpack/json but not a valid CtyValue structure
    valid_json_wrong_structure = json.dumps({"foo": "bar"}) # Not the expected CtyValue dict
    with pytest.raises(ValueError): # Or more specific error if _serializable_to_value checks fields
        CtyValue.from_json_string(valid_json_wrong_structure, CtyString())


# Test case from problem description example
def test_problem_description_string_serialization():
    original_value = CtyString().validate("hello")
    # JSON
    json_str = original_value.to_json_string()
    deserialized_json = CtyValue.from_json_string(json_str, CtyString())
    assert original_value.equals(deserialized_json).value
    assert deserialized_json.type.equals(CtyString())
    # Msgpack
    msgpack_bytes = original_value.to_msgpack_bytes()
    deserialized_msgpack = CtyValue.from_msgpack_bytes(msgpack_bytes, CtyString())
    assert original_value.equals(deserialized_msgpack).value
    assert deserialized_msgpack.type.equals(CtyString())

# 🐍🧪🔒
