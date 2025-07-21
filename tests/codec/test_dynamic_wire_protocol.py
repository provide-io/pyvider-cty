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
    obj_type = CtyObject(attribute_types={"name": CtyString(), "enabled": CtyBool()})
    concrete_value = obj_type.validate({"name": "test", "enabled": True})
    actual_packed = cty_to_msgpack(concrete_value, schema)
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
    list_type = CtyList(element_type=CtyNumber())
    concrete_value = list_type.validate([10, 20, 30])
    actual_packed = cty_to_msgpack(concrete_value, schema)
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
