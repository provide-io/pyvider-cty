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

### `value: CtyValue.to_json_string() -> str`

This function takes a `CtyValue` and converts it into a JSON string. The JSON string will typically be a structured representation containing the value's type information, its actual data (converted to JSON-compatible types), its known/null status, and any marks.

### `CtyValue.from_json_string(json_str: str, target_type: CtyType) -> CtyValue`

This function takes a JSON string (previously created by `cty_value_to_json_string`) and a `target_type` (the `CtyType` you expect the JSON to represent). It parses the JSON and reconstructs the `CtyValue`, validating it against the `target_type`.

**Code Example for JSON Serialization/Deserialization:**

```python
# example_json_serialization.py

