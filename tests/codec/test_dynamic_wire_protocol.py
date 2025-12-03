#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


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
    # This is the raw Python value we want to wrap.
    raw_value = "hello"
    # The correct pattern is to use the schema's validator, which creates
    # the CtyDynamic wrapper around the inferred concrete CtyValue.
    dynamic_value = schema.validate(raw_value)

    actual_packed = cty_to_msgpack(dynamic_value, schema)

    expected_type_spec = json.dumps("string", separators=(",", ":")).encode("utf-8")
    expected_payload = "hello"
    expected_packed = msgpack.packb([expected_type_spec, expected_payload], use_bin_type=True)
    assert actual_packed == expected_packed

    deserialized = cty_from_msgpack(actual_packed, schema)
    assert isinstance(deserialized.type, CtyDynamic)
    # The deserialized value's inner value should equal the concrete value.
    assert deserialized.value == CtyString().validate(raw_value)


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

    expected_type_spec = json.dumps(["list", "number"], separators=(",", ":")).encode("utf-8")
    # Numbers are now encoded as native msgpack integers for Terraform compatibility
    serializable_inner = [10, 20, 30]
    expected_payload = serializable_inner
    expected_packed = msgpack.packb([expected_type_spec, expected_payload], use_bin_type=True)
    assert actual_packed == expected_packed
    deserialized = cty_from_msgpack(actual_packed, schema)
    assert isinstance(deserialized.type, CtyDynamic)
    assert deserialized.value == concrete_value


# 🌊🪢🔚
