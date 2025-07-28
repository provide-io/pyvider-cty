from pyvider.cty import CtyString, CtyObject
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

# 1. Define a type and a CtyValue
user_type = CtyObject({"name": CtyString()})
user_value = user_type.validate({"name": "Alice"})

# 2. Serialize to Msgpack
msgpack_bytes = cty_to_msgpack(user_value, user_type)

# 3. Deserialize from Msgpack
reconstructed_value = cty_from_msgpack(msgpack_bytes, user_type)

assert reconstructed_value == user_value
print("Chapter 12 examples successful.")
