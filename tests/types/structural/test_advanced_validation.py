#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty import (
    CtyDynamic,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack


class TestAdvancedCtyValidation:
    def test_dynamic_roundtrip_of_deeply_nested_structure(self) -> None:
        deep_data = {
            "level1": {
                "items": [
                    {"id": 1, "data": "A"},
                    {"id": 2, "data": "B"},
                ],
                "metadata": None,
            }
        }
        schema = CtyDynamic()
        dynamic_val = schema.validate(deep_data)
        packed_bytes = cty_to_msgpack(dynamic_val, schema)
        unpacked_val = cty_from_msgpack(packed_bytes, schema)

        # The unpacked value is a CtyDynamic wrapper. Compare its inner value.
        assert dynamic_val.value == unpacked_val.value


# 🌊🪢🔚
