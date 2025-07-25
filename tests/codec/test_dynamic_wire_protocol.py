import json

import msgpack

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyObject,
    CtyString,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack


def test_dynamic_string_wire_format() -> None:
    schema = CtyDynamic()
    concrete_value = CtyString().validate("hello")
    actual_packed = cty_to_msgpack(concrete_value, schema)
    expected_type_spec = json.dumps("string").encode("utf-8")
    expected_payload = "hello"
    expected_packed = msgpack.packb(
        [expected_type_spec, expected_payload], use_bin_type=True
    )
    assert actual_packed == expected_packed
    deserialized = cty_from_msgpack(actual_packed, schema)
    assert isinstance(deserialized.type, CtyDynamic)
    assert deserialized.value == concrete_value


def test_dynamic_object_wire_format() -> None:
    schema = CtyDynamic()
    # CORRECTED: The raw data has heterogeneous types, so it will be inferred as an object.
    raw_data = {"name": "test", "enabled": True}
    obj_type = CtyObject(attribute_types={"name": CtyString(), "enabled": CtyBool()})
    concrete_value = obj_type.validate(raw_data)
    
    # Pass the raw data to the dynamic validator to trigger inference.
    dynamic_value = schema.validate(raw_data)
    actual_packed = cty_to_msgpack(dynamic_value, schema)

    expected_type_spec = json.dumps(
        ["object", {"name": "string", "enabled": "bool"}]
    ).encode("utf-8")
    serializable_inner = {"name": "test", "enabled": True}
    expected_payload = serializable_inner
    expected_packed = msgpack.packb(
        [expected_type_spec, expected_payload], use_bin_type=True
    )
    assert actual_packed == expected_packed
    deserialized = cty_from_msgpack(actual_packed, schema)
    assert isinstance(deserialized.type, CtyDynamic)
    assert deserialized.value == concrete_value


def test_dynamic_list_of_primitives_wire_format() -> None:
    schema = CtyDynamic()
    # CORRECTED: The raw data has uniform types, so it will be inferred as a list.
    raw_data = [10, 20, 30]
    list_type = CtyList(element_type=CtyNumber())
    concrete_value = list_type.validate(raw_data)

    # Pass the raw data to the dynamic validator.
    dynamic_value = schema.validate(raw_data)
    actual_packed = cty_to_msgpack(dynamic_value, schema)

    expected_type_spec = json.dumps(["list", "number"]).encode("utf-8")
    # Numbers are serialized as strings to preserve precision.
    serializable_inner = ["10", "20", "30"]
    expected_payload = serializable_inner
    expected_packed = msgpack.packb(
        [expected_type_spec, expected_payload], use_bin_type=True
    )
    assert actual_packed == expected_packed
    deserialized = cty_from_msgpack(actual_packed, schema)
    assert isinstance(deserialized.type, CtyDynamic)
    assert deserialized.value == concrete_value
