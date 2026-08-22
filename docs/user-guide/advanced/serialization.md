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

### Unknown and Refined Values

An unknown value serializes to its own MessagePack extension type (a bare unknown is the two-byte fixext1 `d4 00 00`) and decodes back to an unknown of the same type:

```python
from pyvider.cty import CtyString, CtyValue
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

unknown_value = CtyValue.unknown(CtyString())
msgpack_bytes = cty_to_msgpack(unknown_value, CtyString())
assert msgpack_bytes.hex() == "d40000"

reconstructed = cty_from_msgpack(msgpack_bytes, CtyString())
assert reconstructed.is_unknown
```

A *refined* unknown — one built with `pyvider.cty.refinement.refine` to carry a constraint such as "not null" or a numeric range — keeps that refinement across the wire instead of flattening to a bare unknown. It uses a different extension type (12) to carry the extra payload:

```python
from pyvider.cty import CtyString, CtyValue
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack
from pyvider.cty.refinement import refine

refined = refine(CtyValue.unknown(CtyString())).not_null().new_value()
msgpack_bytes = cty_to_msgpack(refined, CtyString())

reconstructed = cty_from_msgpack(msgpack_bytes, CtyString())
assert reconstructed.is_unknown

# A refined unknown's constraints live on .value, as a RefinedUnknownValue,
# rather than flattening to a plain marker the way a bare unknown does.
assert reconstructed.value.is_known_null is False
```

### Marked Values Must Be Unmarked First

Unlike the other value kinds, a value carrying marks **cannot** be serialized directly — `cty_to_msgpack` raises rather than silently dropping the marks, matching go-cty's own `marshal.go` ("value has marks, so it cannot be serialized"):

```python
from pyvider.cty import CtyString
from pyvider.cty.marks import CtyMark
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.exceptions import CtyMarksSerializationError

string_type = CtyString()
sensitive_mark = CtyMark("sensitive")

password = string_type.validate("secret123")
marked_password = password.with_marks({sensitive_mark})

try:
    cty_to_msgpack(marked_password, string_type)
except CtyMarksSerializationError as e:
    print(f"refused: {e}")
```

The reason is the same one Terraform's own wire format follows: marks like "sensitive" never travel on the value itself — `DynamicValue` on the wire carries only the msgpack bytes, with sensitivity tracked separately by the schema. To serialize a marked value, strip its marks first with `unmark_deep` and carry them out of band; re-apply them with `with_marks` once you have the value back:

```python
from pyvider.cty import CtyString
from pyvider.cty.marks import CtyMark, unmark_deep
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

string_type = CtyString()
sensitive_mark = CtyMark("sensitive")
marked_password = string_type.validate("secret123").with_marks({sensitive_mark})

unmarked, collected_marks = unmark_deep(marked_password)
msgpack_bytes = cty_to_msgpack(unmarked, string_type)

reconstructed = cty_from_msgpack(msgpack_bytes, string_type)
rehydrated = reconstructed.with_marks(collected_marks)
assert sensitive_mark in rehydrated.marks
```

## JSON Support

`pyvider.cty` has two distinct ways to work with JSON, and they answer different questions.

### `jsonencode` / `jsondecode`: JSON as a Terraform Language Feature

These are stdlib functions in `pyvider.cty.functions`, the same ones the Terraform language exposes. They operate on `CtyValue`s and produce or consume a JSON document held as a `CtyValue` string — useful when a JSON blob is itself one attribute among others:

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
# Output: JSON: {"name": "Alice", "age": 30}

# Decode from JSON string
json_input = CtyString().validate('{"name":"Bob","age":25}')
decoded_value = jsondecode(json_input)

# jsondecode infers a concrete type from the document, not a dynamic
# wrapper: an object stays an object, and a JSON array decodes as a
# tuple (a list would have to invent one shared element type).
assert decoded_value.type == CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})
```

### `cty_to_json` / `cty_from_json`: the Value Codec

For storage and transmission, use the JSON *value codec* in `pyvider.cty.json_codec` — the JSON counterpart to the MessagePack codec above, and the form Terraform itself uses wherever a value has to be human-readable, such as state files and `terraform show -json`. Like the MessagePack codec, it is type-directed: you supply the `CtyType` you expect, both to serialize and to parse.

```python
from pyvider.cty import CtyObject, CtyString, cty_to_json, cty_from_json

schema = CtyObject(attribute_types={"note": CtyString()})
value = schema.validate({"note": "<draft>"})

document = cty_to_json(value, schema)
print(document)
# b'{"note":"\\u003cdraft\\u003e"}'

reconstructed = cty_from_json(document, schema)
assert reconstructed == value
```

Note the escaping: `cty_to_json` escapes `<`, `>` and `&` the way Go's `encoding/json` does, so the bytes match what a Go-based tool would produce for the same value — a plain `json.dumps` would leave those characters alone. Decoding is stricter than you might expect from a generic JSON parser, too: an attribute the schema doesn't declare is a hard error rather than a silently dropped key, an attribute the document omits decodes as null rather than being refused, and a JSON number or bool in a string-typed position converts to its literal text (`1.50` decodes to the string `"1.50"`, matching how the document was written, not how the number would print).

Like the MessagePack codec, `cty_to_json` cannot represent an unknown value (there is no JSON spelling for "not yet decided") or a marked one — both raise. Unmark with `unmark_deep` first, exactly as with MessagePack.

**Which to use**: `jsonencode`/`jsondecode` when JSON is data flowing through your `CtyValue`s, as Terraform configuration would produce or consume it. `cty_to_json`/`cty_from_json` when you're persisting or transmitting a whole `CtyValue` and want JSON instead of MessagePack — typically for human-readable output, since MessagePack remains the more complete and more compact format for that role.

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
from pathlib import Path
from tempfile import TemporaryDirectory

from pyvider.cty import CtyObject, CtyString
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

config_type = CtyObject(attribute_types={"setting": CtyString()})
config_value = config_type.validate({"setting": "production"})

with TemporaryDirectory() as directory:
    path = Path(directory) / "config.msgpack"

    # Serialize and save
    path.write_bytes(cty_to_msgpack(config_value, config_type))

    # Load and deserialize
    loaded_value = cty_from_msgpack(path.read_bytes(), config_type)

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

`cty_to_msgpack` raises `SerializationError` (or the more specific `CtyMarksSerializationError` for marked values); `cty_from_msgpack` raises `DeserializationError` whenever the bytes themselves are not a MessagePack payload — empty input, a truncated or trailing-byte stream, a malformed refined-unknown or dynamic-type payload — with the `msgpack` library's own exception chained as `__cause__`:

```python
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.exceptions import DeserializationError
import msgpack

schema = CtyObject(attribute_types={"key": CtyString()})

# A refined-unknown extension payload (ext type 12) that is itself invalid
# msgpack. This is the shape of corruption cty_from_msgpack recognizes.
corrupted = msgpack.packb(msgpack.ExtType(12, b"\xff\xff\xff"))

try:
    cty_from_msgpack(corrupted, CtyString())
except DeserializationError as e:
    print(f"Deserialization failed: {e}")
```

`DeserializationError` covers the bytes being wrong; it does not cover the bytes being *right but for a different type*. A payload that decodes cleanly and then fails to conform to the schema you supplied raises that type's `CtyValidationError` subclass instead. If you're deserializing data from an untrusted or unreliable source, catch `pyvider.cty.exceptions.CtyError` (the common base of both) rather than `DeserializationError` alone; no `msgpack` exception escapes `cty_from_msgpack` on its own.

## Related Topics

- **[Codec API Reference](../../api/codec.md)** - Complete API documentation
- **[Functions Reference](../../api/functions.md)** - JSON encoding functions
- **[Terraform Interoperability](terraform-interop.md)** - Working with Terraform
- **[Go-Cty Comparison](../../reference/go-cty-comparison.md)** - Serialization compatibility details
