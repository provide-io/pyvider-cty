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
    raw_data = {"name": "test", "enabled": True}
    obj_type = CtyObject(attribute_types={"name": CtyString(), "enabled": CtyBool()})
    concrete_value = obj_type.validate(raw_data)
    
    dynamic_value = schema.validate(raw_data)
    actual_packed = cty_to_msgpack(dynamic_value, schema)

    # Unpack both actual and an expected version to compare dictionaries.
    # This is robust against key ordering differences in msgpack libraries.
    unpacked_actual = msgpack.unpackb(actual_packed, raw=False)
    
    expected_type_spec_json = ["object", {"enabled": "bool", "name": "string"}]
    expected_payload = {"enabled": True, "name": "test"}
    
    # Verify the structure and content of the unpacked data
    assert isinstance(unpacked_actual, list)
    assert len(unpacked_actual) == 2
    assert json.loads(unpacked_actual[0]) == expected_type_spec_json
    assert unpacked_actual[1] == expected_payload

    # Also verify the roundtrip still works
    deserialized = cty_from_msgpack(actual_packed, schema)
    assert isinstance(deserialized.type, CtyDynamic)
    assert deserialized.value == concrete_value


def test_dynamic_list_of_primitives_wire_format() -> None:
    schema = CtyDynamic()
    raw_data = [10, 20, 30]
    list_type = CtyList(element_type=CtyNumber())
    concrete_value = list_type.validate(raw_data)

    dynamic_value = schema.validate(raw_data)
    actual_packed = cty_to_msgpack(dynamic_value, schema)

    expected_type_spec = json.dumps(["list", "number"]).encode("utf-8")
    serializable_inner = ["10", "20", "30"]
    expected_payload = serializable_inner
    expected_packed = msgpack.packb(
        [expected_type_spec, expected_payload], use_bin_type=True
    )
    assert actual_packed == expected_packed
    deserialized = cty_from_msgpack(actual_packed, schema)
    assert isinstance(deserialized.type, CtyDynamic)
    assert deserialized.value == concrete_value
