#!/usr/bin/env python3
from examples.example_utils import configure_for_example
from pyvider.cty import CtyNumber, CtyObject, CtyString
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

configure_for_example()

# 1. Define a type and a CtyValue
user_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
user_value = user_type.validate({"name": "Alice", "age": 30})

# 2. Serialize to Msgpack
msgpack_bytes = cty_to_msgpack(user_value, user_type)
print(f"Serialized Msgpack (bytes): {msgpack_bytes!r}")


# 3. Deserialize from Msgpack
reconstructed_value = cty_from_msgpack(msgpack_bytes, user_type)
assert reconstructed_value == user_value
print("\nSuccessfully reconstructed value from Msgpack.")
