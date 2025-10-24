# Understanding Types

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

1.  **Primitive Types**: These are the basic building blocks of the type system. They represent simple, single values.
    *   `CtyString`: Represents a string of text.
    *   `CtyNumber`: Represents a number (integer or float).
    *   `CtyBool`: Represents a boolean value (`True` or `False`).

2.  **Collection Types**: These types represent collections of other types.
    *   `CtyList`: Represents a list of elements of the same type.
    *   `CtySet`: Represents a set of unique elements of the same type.
    *   `CtyMap`: Represents a map of key-value pairs, where the keys are strings and the values are all of the same type.

3.  **Structural Types**: These types represent more complex, structured data.
    *   `CtyObject`: Represents an object with a fixed set of named attributes, each with its own type.
    *   `CtyTuple`: Represents a sequence of elements with a fixed length, where each element can have a different type.

In the following chapters, we will explore each of these categories in more detail.

## See Also

- **[Type Reference: Primitives](../type-reference/primitives.md)** - Detailed guide to String, Number, and Bool types
- **[Type Reference: Collections](../type-reference/collections.md)** - Working with List, Map, and Set
- **[Type Reference: Structural](../type-reference/structural.md)** - Object and Tuple types
- **[Working with Values](values.md)** - Understanding CtyValue objects
- **[Validation](validation.md)** - How type validation works
