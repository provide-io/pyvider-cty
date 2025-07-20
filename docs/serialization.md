# Serializing `CtyValue`s: Packing and Unpacking Your Data 💾

So you've defined your types, created your values, navigated them with paths, and performed operations. Awesome! But what happens when you want to save your precious `CtyValue`s to a file, send them across the internet to another service, or just interoperate with systems that speak different data languages? That's where **serialization** comes in! 📦✈️

Serialization is the process of converting your in-memory `CtyValue` into a format (like a string or byte sequence) that can be easily stored or transmitted. Deserialization is the reverse: taking that stored format and faithfully reconstructing the original `CtyValue`.

`pyvider.cty` provides built-in support for two popular serialization formats:
-   **JSON**: Human-readable, web-friendly, and widely supported.
-   **Msgpack**: A binary format that's often more compact and faster to process than JSON.

The goal is not just to convert the data, but to do so with **type fidelity**, ensuring that when you deserialize, you get back a `CtyValue` that is equivalent in type, value, and special states (like null or unknown) to the original.

## Key Concepts in `cty` Serialization 🗝️

Before we dive into examples, a few crucial ideas:

1.  **Type Fidelity**: `pyvider.cty`'s serialization isn't just a dumb dump of data. It aims to preserve as much type information and value precision as possible. For example, `CtyNumber` values (which use `Decimal`) are serialized in a way that allows them to be deserialized back into `Decimal` without precision loss, where possible. The serialized form typically includes information about the value's `cty` type, its actual data, its known/null status, and any marks.

2.  **Handling of Null and Unknown Values**:
    *   **Null values** are explicitly represented in the serialized output, so they can be correctly restored as `CtyValue.null(some_type)`.
    *   **Unknown values** are also specially marked, allowing them to be deserialized back into `CtyValue.unknown(some_type)`.

3.  **The Role of `target_type` in Deserialization**: This is super important! When you deserialize data (from JSON or Msgpack) back into a `CtyValue`, you **must** provide the `target_type` – the `CtyType` you expect the data to conform to. The serialized data alone might be ambiguous. For instance, a JSON number `123` could be a standalone `CtyNumber`, or it could be an integer that's part of a `CtyObject`'s attribute. The `target_type` guides the reconstruction process and ensures the data is validated against the correct schema.

## JSON: The Lingua Franca of the Web 🌐

JSON (JavaScript Object Notation) is a lightweight, text-based format that's easy for humans to read and for machines to parse.

### `cty_value_to_json_string(value: CtyValue) -> str`

This function takes a `CtyValue` and converts it into a JSON string. The JSON string will typically be a structured representation containing the value's type information, its actual data (converted to JSON-compatible types), its known/null status, and any marks.

### `cty_value_from_json_string(json_str: str, target_type: CtyType) -> CtyValue`

This function takes a JSON string (previously created by `cty_value_to_json_string`) and a `target_type` (the `CtyType` you expect the JSON to represent). It parses the JSON and reconstructs the `CtyValue`, validating it against the `target_type`.

**Code Example for JSON Serialization/Deserialization:**

```python
# example_json_serialization.py
from pyvider.cty import (
    CtyString, CtyNumber, CtyList, CtyObject, CtyBool, CtyValue,
    # Assuming these functions are exposed at the top level of pyvider.cty
    # or from a specific serialization module like pyvider.cty.codec
    cty_value_to_json_string, cty_value_from_json_string,
    CtyTypeError # For error handling
)
from decimal import Decimal

# 1. Define a type and a CtyValue
user_profile_type = CtyObject({
    "username": CtyString(),
    "posts": CtyNumber(),
    "is_active": CtyBool(),
    "tags": CtyList(element_type=CtyString()),
    "preferences": CtyString() # To demonstrate a null value
})

user_value_data = {
    "username": "DevMasterDepy",
    "posts": Decimal("1024"),
    "is_active": True,
    "tags": ["python", "cty", "serialization"],
    "preferences": CtyValue.null(CtyString()) # Explicitly null
}
# For an unknown example, let's say 'tags' could be unknown:
# user_value_data_with_unknown = {
#     "username": "NewbieNora", "posts": Decimal("3"), "is_active": True,
#     "tags": CtyValue.unknown(CtyList(element_type=CtyString())), # 'tags' is unknown
#     "preferences": "dark_theme"
# }
# original_cty_value = CtyValue(user_profile_type, user_value_data_with_unknown)

original_cty_value = CtyValue(user_profile_type, user_value_data)
print(f"Original CtyValue:\n{original_cty_value}")
print(f"  Username: {original_cty_value['username']}")
print(f"  Preferences (is null?): {original_cty_value['preferences'].is_null}")

# 2. Serialize to JSON string
# The actual JSON output from pyvider.cty's codec includes type info, value, known/null status, and marks.
json_string_output = cty_value_to_json_string(original_cty_value)
print(f"\nSerialized JSON Output:\n{json_string_output}") # This will be a structured JSON

# 3. Deserialize from JSON string back to CtyValue
# We MUST provide the target_type to guide deserialization.
deserialized_cty_value = cty_value_from_json_string(json_string_output, user_profile_type)
print(f"\nDeserialized CtyValue:\n{deserialized_cty_value}")

# Verify correctness
print(f"\nIs original value == deserialized value? {original_cty_value == deserialized_cty_value}")
print(f"  Username from deserialized: {deserialized_cty_value['username']}")
print(f"  Tags from deserialized: {deserialized_cty_value['tags'].value}")
print(f"  Preferences from deserialized (is null?): {deserialized_cty_value['preferences'].is_null}")

# 4. Example of Deserialization with Type Mismatch
# Let's say we have the JSON string for 'original_cty_value' (which is an object)
# but we incorrectly try to deserialize it as a simple CtyString.
print("\nAttempting deserialization with a mismatched target type (expecting an error)...")
try:
    # This will fail because json_string_output represents an object, not just a plain string.
    cty_value_from_json_string(json_string_output, CtyString())
except (ValueError, CtyTypeError) as e: # Catch appropriate error (ValueError from JSON parsing, CtyTypeError from type validation)
    print(f"💥 Expected error due to type mismatch during deserialization: {e}")

# Depy: JSON - making your cty data understandable to the whole wide web (with type safety specs on!). 🤓📜
```

## Msgpack: Efficient Binary Serialization 📦

Msgpack is a binary serialization format. It's often more efficient than JSON in terms of both space (producing smaller output) and speed (faster to encode/decode). The downside is that it's not human-readable.

### `cty_value_to_msgpack_bytes(value: CtyValue) -> bytes`

This function takes a `CtyValue` and serializes it into a sequence of bytes using the Msgpack format. Similar to JSON, this will include type information, value, known/null status, and marks.

### `cty_value_from_msgpack_bytes(msgpack_bytes: bytes, target_type: CtyType) -> CtyValue`

This function takes a byte sequence (previously created by `cty_value_to_msgpack_bytes`) and the `target_type`. It decodes the Msgpack data and reconstructs the `CtyValue`.

**Code Example for Msgpack Serialization/Deserialization:**

```python
# example_msgpack_serialization.py
from pyvider.cty import (
    CtyString, CtyNumber, CtyMap, CtyBool, CtyList, CtyValue,
    # Assuming these functions are exposed at the top level of pyvider.cty
    # or from a specific serialization module like pyvider.cty.codec
    cty_value_to_msgpack_bytes, cty_value_from_msgpack_bytes,
    CtyTypeError # For error handling
)
from decimal import Decimal

# 1. Define a type and a CtyValue
# Let's use a map with various data, including an unknown value.
complex_map_type = CtyMap(element_type=CtyObject({
    "id": CtyString(),
    "value": CtyNumber(),
    "active": CtyBool(),
    "history": CtyList(element_type=CtyNumber()) # To show a nested unknown
}))

map_value_data = {
    "itemA": {
        "id": "alpha-001", "value": Decimal("123.45"), "active": True,
        "history": CtyValue.unknown(CtyList(element_type=CtyNumber())) # History for itemA is unknown
    },
    "itemB": {
        "id": "beta-002", "value": Decimal("67.89"), "active": False,
        "history": [Decimal("10"), Decimal("20")]
    }
}
original_cty_value = CtyValue(complex_map_type, map_value_data)
print(f"Original CtyValue:\n{original_cty_value}")
print(f"  Item A's history (is unknown?): {original_cty_value['itemA']['history'].is_unknown}")

# 2. Serialize to Msgpack bytes
msgpack_bytes_output = cty_value_to_msgpack_bytes(original_cty_value)
print(f"\nSerialized Msgpack Output (bytes length): {len(msgpack_bytes_output)}")
# print(f"Raw Msgpack (first 50 bytes): {msgpack_bytes_output[:50]}") # Avoid printing huge byte strings

# 3. Deserialize from Msgpack bytes back to CtyValue
# We MUST provide the target_type.
deserialized_cty_value = cty_value_from_msgpack_bytes(msgpack_bytes_output, complex_map_type)
print(f"\nDeserialized CtyValue:\n{deserialized_cty_value}")

# Verify correctness
print(f"\nIs original value == deserialized value? {original_cty_value == deserialized_cty_value}")
print(f"  Item A's ID from deserialized: {deserialized_cty_value['itemA']['id'].value}")
print(f"  Item B's history from deserialized: {deserialized_cty_value['itemB']['history'].value}")
print(f"  Item A's history from deserialized (is unknown?): {deserialized_cty_value['itemA']['history'].is_unknown}")

# 4. Example of Deserialization with Type Mismatch (conceptual)
print("\nAttempting deserialization with a mismatched target type (expecting an error)...")
try:
    # msgpack_bytes_output represents a map, but we try to deserialize as CtyString
    cty_value_from_msgpack_bytes(msgpack_bytes_output, CtyString())
except (ValueError, CtyTypeError) as e: # Catch appropriate error
    print(f"💥 Expected error due to type mismatch during deserialization: {e}")

# Depy: Msgpack - for when your data needs to be lean, mean, and super speedy (but shy in public). 🕶️🧱
```

---

Reliable serialization and deserialization are cornerstones of any robust data handling system. `pyvider.cty`'s built-in support for JSON and Msgpack, coupled with its focus on type fidelity and proper handling of special states like null and unknown, ensures that your data can travel safely and be reconstructed accurately, wherever its journey may take it. Happy serializing! ✨
