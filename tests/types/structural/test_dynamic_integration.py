#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pyvider.cty import CtyDynamic, CtyList, CtyObject, CtyString
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.conversion import cty_to_native


class TestCtyDynamicIntegration:
    def test_dynamic_roundtrip_with_list_of_objects(self) -> None:
        list_of_objects_type = CtyList(element_type=CtyObject(attribute_types={"name": CtyString()}))
        cty_val = list_of_objects_type.validate([{"name": "Alice"}, {"name": "Bob"}])

        schema = CtyDynamic()
        dynamic_val = schema.validate(cty_val)

        packed_bytes = cty_to_msgpack(dynamic_val, schema)
        unpacked_val = cty_from_msgpack(packed_bytes, schema)

        # The unpacked value is a CtyDynamic wrapper. Compare its inner value.
        assert dynamic_val.value == unpacked_val.value
        assert cty_to_native(unpacked_val) == [{"name": "Alice"}, {"name": "Bob"}]


# 🌊🪢🔚
