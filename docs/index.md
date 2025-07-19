# pyvider.cty Documentation

Welcome to the documentation for `pyvider.cty`, a Python implementation of the `cty` type system used in HashiCorp's Terraform.

## Introduction

`pyvider.cty` provides a rich, dynamic type system that allows for robust and flexible data validation and manipulation. It is designed to be a powerful tool for building applications that require a strong and expressive type system, such as infrastructure-as-code tools, configuration management systems, and more.

## Core Concepts

The `pyvider.cty` library is built around a few core concepts:

*   **Types:** The fundamental building blocks of the `cty` type system. Types define the shape and constraints of data.
*   **Values:** Instances of a `cty` type. Values hold the actual data and are immutable.
*   **Validation:** The process of checking if a raw Python value conforms to a given `cty` type.
*   **Conversion:** The process of converting between `cty` values and raw Python values.
*   **Functions:** A set of built-in functions for manipulating `cty` values.

## Getting Started

To start using `pyvider.cty`, you will first need to install it:

```bash
pip install pyvider.cty
```

Once installed, you can start defining and using `cty` types in your Python code.

### Defining a Simple Type

Here's an example of how to define a simple `cty` type:

```python
from pyvider.cty import CtyString

# Define a string type
string_type = CtyString()

# Validate a raw Python value
cty_value = string_type.validate("hello")

# Access the raw value
assert cty_value.raw_value == "hello"
```

### Defining a Complex Type

You can also define more complex types, such as objects and lists:

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyList

# Define an object type
user_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
})

# Define a list of users type
user_list_type = CtyList(element_type=user_type)

# Validate a raw Python value
users_data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 40},
]
cty_users = user_list_type.validate(users_data)

# Access the raw value
assert cty_users.raw_value == (
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 40},
)
```

## Next Steps

This was just a brief introduction to `pyvider.cty`. To learn more, check out the other pages in this documentation:

*   **[Types](./types.md):** A detailed guide to all the available `cty` types.
*   **[Values](./values.md):** Learn more about working with `cty` values.
*   **[Functions](./functions.md):** Explore the built-in functions for manipulating `cty` values.
*   **[Validation](./validation.md):** A deep dive into the validation process.
*   **[Conversion](./conversion.md):** Learn how to convert between `cty` values and raw Python values.
