# Chapter 8: Dynamic Types

The `CtyDynamic` type is a special type in `pyvider.cty` that can represent any type of value. It is useful when you are working with data that has an unknown or varying structure.

## The `CtyDynamic` Type

You can use the `CtyDynamic` type to create a type that can accept any valid `cty` value:

```python
from pyvider.cty import CtyDynamic, CtyString, CtyNumber

dynamic_type = CtyDynamic()

# Validate a string
cty_string = dynamic_type.validate("hello")
assert isinstance(cty_string.type, CtyString)

# Validate a number
cty_number = dynamic_type.validate(123)
assert isinstance(cty_number.type, CtyNumber)
```

When you validate a value against a `CtyDynamic` type, the resulting `cty` value will have the most specific type that can be inferred from the raw Python value.

## Use Cases for `CtyDynamic`

The `CtyDynamic` type is particularly useful in the following scenarios:

*   **Working with Unstructured Data**: If you are working with data that does not have a fixed schema, you can use the `CtyDynamic` type to represent it.

*   **Building Generic Functions**: You can use the `CtyDynamic` type to build generic functions that can operate on any type of `cty` value.

*   **Delayed Type-Checking**: In some cases, you may want to defer type-checking until a later stage in your data processing pipeline. You can use the `CtyDynamic` type to represent the data in the intermediate stages, and then perform the final validation at the end.

## `CtyDynamic` in Collections

You can also use the `CtyDynamic` type within collection and structural types:

```python
from pyvider.cty import CtyList, CtyDynamic

# A list of any type of value
dynamic_list_type = CtyList(element_type=CtyDynamic())

# Validate a list with mixed types
cty_list = dynamic_list_type.validate(["hello", 123, True])
```
