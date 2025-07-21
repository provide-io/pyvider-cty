# Chapter 3: Understanding Types

In `pyvider.cty`, types are the cornerstone of the entire system. They define the structure, constraints, and expectations for your data. By creating precise type definitions, you can ensure that your data is valid and consistent.

## The Role of Types

A `pyvider.cty` type serves several key purposes:

1.  **Validation**: A type acts as a schema against which you can validate raw Python data. It enforces the structure and types of the data, ensuring that it conforms to your expectations.

2.  **Immutability**: When you validate raw data against a type, you get back an immutable `cty` value. This means that once a value is created, it cannot be changed, which helps to prevent bugs and makes your code more predictable.

3.  **Type-Safe Operations**: `pyvider.cty` provides a set of built-in functions that operate on `cty` values. These functions are type-safe, meaning that they will only work with the correct types of values.

## The `CtyType` Base Class

All `pyvider.cty` types inherit from the `CtyType` base class. This class provides the common interface for all types, including the `validate` method.

### The `validate` Method

The `validate` method is the most important method of a `cty` type. It takes a raw Python value as input and attempts to convert it into a `cty` value of the corresponding type.

```python
cty_value = my_type.validate(raw_python_value)
```

If the validation is successful, `validate` returns a new `cty` value. If the validation fails, it raises a `ValidationError` with detailed information about what went wrong.

## Categories of Types

`pyvider.cty` provides a rich set of built-in types that can be divided into three main categories:

### 1. Primitive Types

These are the basic building blocks of the type system. They represent simple, single values.

*   `CtyString`: Represents a string of text.
*   `CtyNumber`: Represents a number (integer or float).
*   `CtyBool`: Represents a boolean value (`True` or `False`).

**Example:**
```python
from pyvider.cty import CtyString, CtyNumber, CtyBool

# A type for a simple configuration setting
setting_type = CtyString()

# A type for a measurement
measurement_type = CtyNumber()

# A type for a feature flag
flag_type = CtyBool()
```

### 2. Collection Types

These types represent collections of other types.

*   `CtyList(element_type)`: Represents a list of elements of the same type.
*   `CtySet(element_type)`: Represents a set of unique elements of the same type.
*   `CtyMap(element_type)`: Represents a map of string keys to values, where all values are of the same type.

**Example:**
```python
from pyvider.cty import CtyList, CtySet, CtyMap, CtyString, CtyNumber

# A list of tags
tags_type = CtyList(element_type=CtyString())

# A set of unique user IDs
user_ids_type = CtySet(element_type=CtyNumber())

# A map of environment variables
env_vars_type = CtyMap(element_type=CtyString())
```

### 3. Structural Types

These types represent more complex, structured data.

*   `CtyObject(attribute_types)`: Represents an object with a fixed set of named attributes, each with its own type.
*   `CtyTuple(element_types)`: Represents a sequence of elements with a fixed length, where each element can have a different type.

**Example:**
```python
from pyvider.cty import CtyObject, CtyTuple, CtyString, CtyNumber, CtyBool

# A type for a user object
user_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
    "is_active": CtyBool(),
})

# A type for a coordinate pair
coordinate_type = CtyTuple(element_types=(CtyNumber(), CtyNumber()))
```

In the following chapters, we will explore each of these categories in more detail.
