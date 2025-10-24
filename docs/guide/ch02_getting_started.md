# Chapter 2: Getting Started

This chapter will guide you through installing `pyvider.cty` and understanding its fundamental concepts, culminating in validating your first data structure.

## Installation

You can install `pyvider.cty` using `uv` (recommended) or `pip`:

```bash
# With uv (recommended)
uv add pyvider-cty
```

```bash
# With pip
pip install pyvider-cty
```

This will install the core library and its dependencies.

## Core Concepts

Before diving into examples, let's briefly cover the main components of the `pyvider.cty` framework:

*   **Type**: A `pyvider.cty` type defines the shape and constraints of your data. The library provides a rich set of built-in types, including primitive types (like `CtyString`, `CtyNumber`, `CtyBool`), collection types (`CtyList`, `CtyMap`, `CtySet`), and structural types (`CtyObject`, `CtyTuple`).

*   **Value**: A `pyvider.cty` value is an instance of a `cty` type. It holds the actual data and is immutable. You can't create `cty` values directly; instead, you create them by validating raw Python data against a `cty` type.

*   **Validation**: The process of checking if a raw Python value conforms to a given `cty` type. If the value is valid, the validation process returns a new `cty` value. If it's not, it raises a `ValidationError`.

*   **Conversion**: The process of converting between `cty` values and raw Python values. `pyvider.cty` provides functions to convert `cty` values back into their raw Python representation.

*   **Functions**: A set of built-in functions for manipulating `cty` values. These functions operate on `cty` values and return new `cty` values.

## Quick Start: 5-Minute Example

This example demonstrates the most common use case: defining a `cty` type and using it to validate a raw Python dictionary.

**1. Import Required Types**

```python
from pyvider.cty import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyObject, CtyDynamic,
    CtyValue
)
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack
```

**2. Define a Type Schema**

```python
# Define a complex object type for a user
person_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
    "active": CtyBool(),
    "tags": CtyList(element_type=CtyString())
})
```

**3. Create and Validate a Value**

The `validate` method checks if the raw Python data conforms to the type schema and returns a `CtyValue` instance.

```python
# Create a raw Python dictionary
user_data = {
    "name": "Alice",
    "age": 30,
    "active": True,
    "tags": ["developer", "python"]
}

# Validate the data
try:
    person_value = person_type.validate(user_data)
    print("Validation successful!")
except Exception as e:
    print(f"Validation failed: {e}")
```

**4. Access Data from the `CtyValue`**

You can access attributes and elements of a `CtyValue` using standard Python square-bracket notation `[]`. The returned items are also `CtyValue`s. To get the raw Python value, use the `.raw_value` property.

```python
# Access attributes of the object
print(f"Name: {person_value['name'].raw_value}")  # Output: Alice
print(f"Age: {person_value['age'].raw_value}")    # Output: 30

# Iterate over the list
print("Tags:")
for tag_value in person_value['tags']:
    print(f"- {tag_value.raw_value}")
```

**5. Serialize to MessagePack**

`pyvider.cty` can serialize values to MessagePack binary format for storage or transmission. This format is compatible with go-cty for cross-language interoperability.

```python
msgpack_bytes = cty_to_msgpack(person_value, person_type)
print(f"\nSerialized to {len(msgpack_bytes)} bytes of MessagePack data")
```

**6. Deserialize from MessagePack**

To reconstruct a `CtyValue` from MessagePack, you must provide the `cty_type` to guide the process.

```python
reconstructed_value = cty_from_msgpack(msgpack_bytes, person_type)
assert reconstructed_value['name'].raw_value == "Alice"
print("\nSuccessfully reconstructed value from MessagePack.")
```

This fundamental pattern—Define, Validate, Access, Serialize—is the core workflow you will use repeatedly with `pyvider.cty`.
