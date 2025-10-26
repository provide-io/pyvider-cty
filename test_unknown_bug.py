#!/usr/bin/env python3
"""Test script to reproduce the unknown object bug."""

from pyvider.cty import CtyValue, CtyString, CtyObject
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack


def test_unknown_object_bug():
    """Reproduce the bug where objects with unknown fields become entirely unknown."""

    # Create schema for an object with two string fields
    schema = CtyObject(
        attribute_types={
            "input_value": CtyString(),
            "decrypted_token": CtyString()
        }
    )

    # Create object with mixed known/unknown fields (simulating plan phase)
    obj_value = {
        "input_value": CtyValue(vtype=CtyString(), value="test-verification"),
        "decrypted_token": CtyValue.unknown(CtyString())
    }

    # Create CtyValue for the object
    cty_val = CtyValue(vtype=schema, value=obj_value, is_unknown=False)

    print("=" * 60)
    print("BEFORE MARSHAL/UNMARSHAL:")
    print("=" * 60)
    print(f"Object is_unknown: {cty_val.is_unknown}")
    print(f"Object value type: {type(cty_val.value)}")
    if isinstance(cty_val.value, dict):
        for key, val in cty_val.value.items():
            print(f"  Field '{key}':")
            print(f"    is_unknown: {val.is_unknown}")
            print(f"    value: {val.value}")

    # Marshal to msgpack
    marshaled = cty_to_msgpack(cty_val, schema)
    print(f"\nMarshaled bytes length: {len(marshaled)}")

    # Unmarshal from msgpack
    unmarshaled = cty_from_msgpack(marshaled, schema)

    print("\n" + "=" * 60)
    print("AFTER MARSHAL/UNMARSHAL:")
    print("=" * 60)
    print(f"Object is_unknown: {unmarshaled.is_unknown}")  # ❌ BUG: Should be False
    print(f"Object value type: {type(unmarshaled.value)}")
    if isinstance(unmarshaled.value, dict):
        for key, val in unmarshaled.value.items():
            print(f"  Field '{key}':")
            print(f"    is_unknown: {val.is_unknown}")
            print(f"    value: {val.value}")

    print("\n" + "=" * 60)
    print("EXPECTED vs ACTUAL:")
    print("=" * 60)
    print(f"Expected object is_unknown: False")
    print(f"Actual object is_unknown: {unmarshaled.is_unknown}")

    if unmarshaled.is_unknown:
        print("\n❌ BUG CONFIRMED: Object is_unknown should be False but is True!")
        return False
    else:
        print("\n✅ Object is_unknown is correctly False!")
        return True


if __name__ == "__main__":
    success = test_unknown_object_bug()
    exit(0 if success else 1)
