# Serialization

Serialization is the process of converting your in-memory `CtyValue` into a format (like a byte sequence) that can be easily stored or transmitted. Deserialization is the reverse: taking that stored format and faithfully reconstructing the original `CtyValue`.

`pyvider.cty` provides built-in support for **MessagePack**, a binary format that's compact, fast, and **fully compatible with HashiCorp's go-cty**. This is the primary and recommended serialization format for cross-language interoperability with Terraform providers and other Go-based tools.

## Key Concepts

1.  **Type Fidelity**: `pyvider.cty`'s serialization aims to preserve as much type information and value precision as possible. The serialized form includes information about the value's `cty` type, its actual data, its known/null status, and any marks.

2.  **Handling of Null and Unknown Values**: Null and unknown values are explicitly represented in the serialized output, so they can be correctly restored.

3.  **The Role of `target_type` in Deserialization**: When you deserialize data, you **must** provide the `target_type`—the `CtyType` you expect the data to conform to. This guides the reconstruction process and ensures the data is validated against the correct schema.

## MessagePack Serialization

The `pyvider.cty.codec` module provides functions for MessagePack serialization.

*   `cty_to_msgpack(value: CtyValue, schema: CtyType) -> bytes`: Serializes a `CtyValue` to a MessagePack byte string.
*   `cty_from_msgpack(data: bytes, cty_type: CtyType) -> CtyValue`: Deserializes a MessagePack byte string to a `CtyValue`.

### Basic Example

```python
from pyvider.cty import CtyString, CtyObject
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

# 1. Define a type and a CtyValue
user_type = CtyObject(attribute_types={"name": CtyString()})
user_value = user_type.validate({"name": "Alice"})

# 2. Serialize to MessagePack
msgpack_bytes = cty_to_msgpack(user_value, user_type)
print(f"Serialized to {len(msgpack_bytes)} bytes")

# 3. Deserialize from MessagePack
reconstructed_value = cty_from_msgpack(msgpack_bytes, user_type)

assert reconstructed_value == user_value
```

### Complex Structures

MessagePack serialization works seamlessly with complex, nested structures:

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyList, CtyBool
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

# Define a complex nested type
config_type = CtyObject(
    attribute_types={
        "database": CtyObject(
            attribute_types={
                "host": CtyString(),
                "port": CtyNumber(),
                "replicas": CtyList(element_type=CtyString()),
            }
        ),
        "features": CtyObject(
            attribute_types={
                "enabled": CtyBool(),
                "flags": CtyList(element_type=CtyString()),
            }
        ),
    }
)

# Create and validate data
config_data = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "replicas": ["replica1", "replica2"],
    },
    "features": {
        "enabled": True,
        "flags": ["feature_a", "feature_b"],
    },
}

config_value = config_type.validate(config_data)

# Serialize
msgpack_bytes = cty_to_msgpack(config_value, config_type)

# Deserialize
reconstructed = cty_from_msgpack(msgpack_bytes, config_type)
assert reconstructed == config_value
```

### Preserving Null and Unknown Values

MessagePack serialization correctly preserves null and unknown values:

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyValue
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
    },
    optional_attributes={"age"}
)

# Create a value with a null attribute
user_data = {"name": "Bob"}  # age will be null
user_value = user_type.validate(user_data)

# Serialize and deserialize
msgpack_bytes = cty_to_msgpack(user_value, user_type)
reconstructed = cty_from_msgpack(msgpack_bytes, user_type)

# Null is preserved
assert reconstructed["age"].is_null
```

### Preserving Marks

Marks (metadata) are preserved during serialization:

```python
from pyvider.cty import CtyString
from pyvider.cty.marks import CtyMark
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

string_type = CtyString()
sensitive_mark = CtyMark("sensitive")

# Create a marked value
password = string_type.validate("secret123")
marked_password = password.with_marks({sensitive_mark})

# Serialize and deserialize
msgpack_bytes = cty_to_msgpack(marked_password, string_type)
reconstructed = cty_from_msgpack(msgpack_bytes, string_type)

# Marks are preserved
assert sensitive_mark in reconstructed.marks
```

## JSON Support

For JSON workflows, `pyvider.cty` provides the `jsonencode()` and `jsondecode()` functions in the `pyvider.cty.functions` module. These work with JSON strings as `CtyValue` objects:

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber
from pyvider.cty.functions import jsonencode, jsondecode

# Create a value
user_type = CtyObject(
    attribute_types={"name": CtyString(), "age": CtyNumber()}
)
user_value = user_type.validate({"name": "Alice", "age": 30})

# Encode to JSON string (returns CtyValue containing a JSON string)
json_string_value = jsonencode(user_value)
json_str = json_string_value.raw_value  # Get the actual JSON string

print(f"JSON: {json_str}")
# Output: JSON: {"name":"Alice","age":30}

# Decode from JSON string
json_input = CtyString().validate('{"name":"Bob","age":25}')
decoded_value = jsondecode(json_input)

# Note: jsondecode returns dynamic data, may need type conversion
```

**Key Difference**: Unlike MessagePack serialization which is designed for storage and transmission, `jsonencode`/`jsondecode` are for working with JSON data as strings within the cty type system.

## Cross-Language Compatibility

The MessagePack format is **fully compatible** with go-cty, enabling seamless data exchange:

```python
# Python serializes data
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.codec import cty_to_msgpack

schema = CtyObject(attribute_types={"message": CtyString()})
value = schema.validate({"message": "Hello from Python"})
msgpack_data = cty_to_msgpack(value, schema)

# This msgpack_data can be sent to a Go application using go-cty
# Go can deserialize it with: msgpack.Unmarshal(msgpack_data, goSchema)

# Similarly, data serialized by go-cty can be deserialized by pyvider.cty
```

## Storage and Transmission

### Saving to File

```python
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

config_type = CtyObject(attribute_types={"setting": CtyString()})
config_value = config_type.validate({"setting": "production"})

# Serialize and save
msgpack_bytes = cty_to_msgpack(config_value, config_type)
with open("config.msgpack", "wb") as f:
    f.write(msgpack_bytes)

# Load and deserialize
with open("config.msgpack", "rb") as f:
    loaded_bytes = f.read()
loaded_value = cty_from_msgpack(loaded_bytes, config_type)

assert loaded_value == config_value
```

### Network Transmission

```python
import socket
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

data_type = CtyObject(attribute_types={"payload": CtyString()})

# Serialize for transmission
data = data_type.validate({"payload": "important data"})
msgpack_bytes = cty_to_msgpack(data, data_type)

# Send over network (example with sockets)
# sock.sendall(msgpack_bytes)

# Receive and deserialize
# received_bytes = sock.recv(4096)
# reconstructed = cty_from_msgpack(received_bytes, data_type)
```

## Performance Considerations

**MessagePack Benefits:**
- **Compact**: Typically smaller than JSON
- **Fast**: Binary format is faster to parse than text-based JSON
- **Type-safe**: Preserves type information and cty semantics
- **Compatible**: Works seamlessly with go-cty

**When to Use MessagePack:**
- Storing configuration data
- Transmitting data between Python and Go services
- Working with Terraform providers
- Any scenario requiring type fidelity and performance

**When to Use JSON Functions:**
- When you need human-readable output
- Integrating with JSON-based APIs
- Debugging and inspection
- When cross-language compatibility with non-cty systems is needed

## Best Practices

1. **Always provide the type during deserialization**: The type parameter is required for proper reconstruction
2. **Cache schemas**: Don't recreate `CtyType` instances repeatedly; create once and reuse
3. **Handle serialization errors**: Wrap serialize/deserialize calls in try-except blocks
4. **Validate after deserialization**: While the type is enforced during deserialization, consider additional validation for external data
5. **Use MessagePack for production**: Prefer MessagePack over JSON for production systems requiring reliability and performance

## Error Handling

```python
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack
from pyvider.cty.exceptions import SerializationError, DeserializationError

schema = CtyObject(attribute_types={"key": CtyString()})

try:
    value = schema.validate({"key": "value"})
    msgpack_bytes = cty_to_msgpack(value, schema)
except SerializationError as e:
    print(f"Serialization failed: {e}")

try:
    # Attempt to deserialize potentially corrupted data
    reconstructed = cty_from_msgpack(msgpack_bytes, schema)
except DeserializationError as e:
    print(f"Deserialization failed: {e}")
```

## Related Topics

- **[Codec API Reference](../../api/codec.md)** - Complete API documentation
- **[Functions Reference](../../api/functions.md)** - JSON encoding functions
- **[Terraform Interoperability](terraform-interop.md)** - Working with Terraform
- **[Go-Cty Comparison](../../reference/go-cty-comparison.md)** - Serialization compatibility details
