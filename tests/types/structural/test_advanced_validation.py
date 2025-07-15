import pytest
from pyvider.cty import (
    CtyDynamic, CtyList, CtyObject, CtyString, CtyNumber, CtyValue, CtyBool
)
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack
from pyvider.cty.conversion import cty_to_native

class TestAdvancedCtyValidation:
    def test_dynamic_roundtrip_of_deeply_nested_structure(self):
        deep_data = {
            "level1": {
                "items": [
                    {"id": 1, "data": "A"},
                    {"id": 2, "data": "B"},
                ],
                "metadata": None
            }
        }
        schema = CtyDynamic()
        dynamic_val = schema.validate(deep_data)
        packed_bytes = cty_to_msgpack(dynamic_val, schema)
        unpacked_val = cty_from_msgpack(packed_bytes, schema)
        
        assert dynamic_val == unpacked_val
