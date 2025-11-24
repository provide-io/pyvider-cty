#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import attrs
import msgpack

from pyvider.cty import CtyDynamic, CtyObject, CtyValue
from pyvider.cty.codec import cty_from_msgpack


@attrs.define
class MyComponentState:
    name: str
    count: int


def test_validate_raw_attrs_object_with_ctydynamic() -> None:
    raw_state_obj = MyComponentState(name="test", count=123)
    # When deserializing to a dynamic type, we don't have a schema,
    # so we simulate a simple msgpack payload from the raw dict.
    packed_data = msgpack.packb(attrs.asdict(raw_state_obj), use_bin_type=True)

    # The schema for deserialization is CtyDynamic
    schema = CtyDynamic()

    # cty_from_msgpack will infer the type and wrap it
    cty_val = cty_from_msgpack(packed_data, schema)

    assert isinstance(cty_val, CtyValue)
    assert isinstance(cty_val.type, CtyDynamic)

    # The inner value should be the inferred CtyObject
    inner_value = cty_val.value
    assert isinstance(inner_value.type, CtyObject)
    assert "name" in inner_value.type.attribute_types
    assert "count" in inner_value.type.attribute_types
    assert inner_value["name"].value == "test"
    assert inner_value["count"].value == 123


# 🌊🪢🔚
