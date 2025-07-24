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
from pyvider.cty.conversion import to_json, from_json
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

You can access attributes and elements of a `CtyValue` using standard Python square-bracket notation `[]`. The returned items are also `CtyValue`s. To get the raw Python value, use the `.value` property.

```python
# Access attributes of the object
print(f"Name: {person_value['name'].value}")  # Output: Alice
print(f"Age: {person_value['age'].value}")    # Output: 30

# Iterate over the list
print("Tags:")
for tag_value in person_value['tags']:
    print(f"- {tag_value.value}")
```

**5. Serialize to JSON**

`pyvider.cty` can serialize values to JSON for storage or transmission.

```python
json_representation = to_json(person_value)
print(f"\nJSON representation:\n{json_representation}")
```

**6. Deserialize from JSON**

To reconstruct a `CtyValue` from JSON, you must provide the `target_type` to guide the process.

```python
reconstructed_value = from_json(json_representation, person_type)
assert reconstructed_value['name'].value == "Alice"
print("\nSuccessfully reconstructed value from JSON.")
```

This fundamental pattern—Define, Validate, Access, Serialize—is the core workflow you will use repeatedly with `pyvider.cty`.
