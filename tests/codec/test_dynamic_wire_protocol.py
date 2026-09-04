#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import json

import msgpack

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack

_UNKNOWN_EXT_BYTES = msgpack.ExtType(0, b"\x00")
"""The three bytes `d4 00 00`: an unknown with nothing refined about it."""


def _refined_unknown_ext(payload: dict[int, object]) -> msgpack.ExtType:
    """go-cty's ext-12: an unknown carrying a refinement map."""
    return msgpack.ExtType(12, msgpack.packb(payload, use_bin_type=True))


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


def test_unknown_at_a_nested_dynamic_attribute_leaves_its_siblings_known() -> None:
    """A bare unknown in a dynamic attribute is that attribute's, not the object's.

    Terraform writes `d4 00 00` for a dynamic-typed attribute whose value is
    unknown and whose type is not yet determined -- `objchange` produces
    `cty.UnknownVal(cty.DynamicPseudoType)` whenever the prior value was unknown,
    and `jsondecode` of an unknown returns the same. The whole object used to come
    back unknown, so the planned state of every resource with a dynamic attribute
    lost its known attributes and Terraform core refused the plan.
    """
    schema = CtyObject(attribute_types={"d": CtyDynamic(), "s": CtyString()})
    wire = msgpack.packb({"d": _UNKNOWN_EXT_BYTES, "s": "x"}, use_bin_type=True)

    value = cty_from_msgpack(wire, schema)

    assert not value.is_unknown
    assert value["d"].is_unknown
    assert isinstance(value["d"].type, CtyDynamic)
    assert value["s"] == CtyString().validate("x")

    reencoded = msgpack.unpackb(cty_to_msgpack(value, schema), raw=False)
    assert reencoded == {"d": _UNKNOWN_EXT_BYTES, "s": "x"}


def test_unknown_in_a_list_of_dynamic_leaves_the_other_elements_known() -> None:
    schema = CtyList(element_type=CtyDynamic())
    wire = msgpack.packb([_UNKNOWN_EXT_BYTES, "x"], use_bin_type=True)

    value = cty_from_msgpack(wire, schema)

    assert not value.is_unknown
    assert value[0].is_unknown
    assert value[1].value == CtyString().validate("x")

    reencoded = msgpack.unpackb(cty_to_msgpack(value, schema), raw=False)
    assert reencoded[0] == _UNKNOWN_EXT_BYTES
    assert json.loads(reencoded[1][0]) == "string"
    assert reencoded[1][1] == "x"


def test_unknown_in_a_map_of_dynamic_leaves_the_other_entries_known() -> None:
    schema = CtyMap(element_type=CtyDynamic())
    wire = msgpack.packb({"d": _UNKNOWN_EXT_BYTES, "s": "x"}, use_bin_type=True)

    value = cty_from_msgpack(wire, schema)

    assert not value.is_unknown
    assert value["d"].is_unknown
    assert value["s"].value == CtyString().validate("x")

    reencoded = msgpack.unpackb(cty_to_msgpack(value, schema), raw=False)
    assert reencoded["d"] == _UNKNOWN_EXT_BYTES
    assert json.loads(reencoded["s"][0]) == "string"
    assert reencoded["s"][1] == "x"


def test_a_refined_unknown_at_a_dynamic_position_arrives_unrefined() -> None:
    """A refinement means nothing without a type to constrain, so it is dropped.

    go-cty's msgpack decoder answers `cty.UnknownVal(ty)` and ignores the whole
    refinement map when `ty` is `DynamicPseudoType` (`cty/msgpack/unknown.go`),
    and `Refine()` on `DynamicVal` echoes the unrefined value back
    (`cty/unknown_refinement.go`). Inferring a type from the refinement marker
    instead produced an `object` of the refinement's own fields on the wire.
    """
    schema = CtyObject(attribute_types={"d": CtyDynamic(), "s": CtyString()})
    refined = _refined_unknown_ext({1: False, 2: "ab"})
    wire = msgpack.packb({"d": refined, "s": "x"}, use_bin_type=True)

    value = cty_from_msgpack(wire, schema)

    assert not value.is_unknown
    assert value["d"].is_unknown
    assert value["s"] == CtyString().validate("x")

    reencoded = msgpack.unpackb(cty_to_msgpack(value, schema), raw=False)
    assert reencoded == {"d": _UNKNOWN_EXT_BYTES, "s": "x"}


def test_null_at_a_nested_dynamic_attribute_stays_a_null() -> None:
    schema = CtyObject(attribute_types={"d": CtyDynamic(), "s": CtyString()})
    wire = msgpack.packb({"d": None, "s": "x"}, use_bin_type=True)

    value = cty_from_msgpack(wire, schema)

    assert not value.is_unknown
    assert value["d"].is_null
    assert value["s"] == CtyString().validate("x")

    reencoded = msgpack.unpackb(cty_to_msgpack(value, schema), raw=False)
    assert reencoded == {"d": None, "s": "x"}


# 🌊🪢🔚
