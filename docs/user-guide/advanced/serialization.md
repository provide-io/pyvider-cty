# Serialization

Serialization is the process of converting your in-memory `CtyValue` into a format (like a byte sequence) that can be easily stored or transmitted. Deserialization is the reverse: taking that stored format and faithfully reconstructing the original `CtyValue`.

`pyvider.cty` provides built-in support for **Msgpack**, a binary format that's often more compact and faster to process than JSON. This is the primary format used for `go-cty` interoperability.

## Key Concepts

1.  **Type Fidelity**: `pyvider.cty`'s serialization aims to preserve as much type information and value precision as possible. The serialized form includes information about the value's `cty` type, its actual data, its known/null status, and any marks.

2.  **Handling of Null and Unknown Values**: Null and unknown values are explicitly represented in the serialized output, so they can be correctly restored.

3.  **The Role of `target_type` in Deserialization**: When you deserialize data, you **must** provide the `target_type`—the `CtyType` you expect the data to conform to. This guides the reconstruction process and ensures the data is validated against the correct schema.

## Msgpack Serialization

The `pyvider.cty.codec` module provides functions for Msgpack serialization.

*   `cty_to_msgpack(value: CtyValue, schema: CtyType) -> bytes`: Serializes a `CtyValue` to a Msgpack byte string.
*   `cty_from_msgpack(data: bytes, cty_type: CtyType) -> CtyValue`: Deserializes a Msgpack byte string to a `CtyValue`.

```python
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
```
