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

## Example: Quick Start - Basic Type Validation

This example demonstrates the most common use case: defining a `cty` type and using it to validate a raw Python dictionary.

**1. The `cty` Type Definition**

First, let's define a `cty` type for a user object. This type will specify the expected attributes and their corresponding types.

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber

user_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
})
```

**2. The Raw Python Data**

Next, let's create a raw Python dictionary that we want to validate against our `user_type`.

```python
user_data = {
    "name": "Alice",
    "age": 30,
}
```

**3. Validation**

Now, let's use the `validate` method of our `user_type` to validate the `user_data`.

```python
try:
    cty_user = user_type.validate(user_data)
    print("Validation successful!")
    print(f"cty_user: {cty_user}")
except Exception as e:
    print(f"Validation failed: {e}")
```

If the validation is successful, `cty_user` will be a `pyvider.cty` value that you can work with. If the validation fails, a `ValidationError` will be raised.

**To Run This Example:**

1.  Ensure you have `pyvider.cty` installed.
2.  Save the code above into a Python file (e.g., `quick_start.py`).
3.  Run the file: `python quick_start.py`

You should see the "Validation successful!" message and the `cty` representation of the user data. This demonstrates the fundamental pattern of defining a type and using it to validate raw Python data.
