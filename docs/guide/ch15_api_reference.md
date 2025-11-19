# Chapter 15: API Reference

This chapter provides a reference for the key public classes, functions, and interfaces in the `pyvider.cty` library.

## Core Types

### `pyvider.cty.CtyType`

The abstract base class for all `cty` types.

*   **`validate(self, value: Any) -> CtyValue`**: Validates a raw Python value and returns a `CtyValue` instance.
*   **`null(self) -> CtyValue`**: Returns a null value of this type.
*   **`unknown(self) -> CtyValue`**: Returns an unknown value of this type.

### Primitive Types

*   `pyvider.cty.CtyString`: Represents a string type.
*   `pyvider.cty.CtyNumber`: Represents a number type.
*   `pyvider.cty.CtyBool`: Represents a boolean type.

### Collection Types

*   `pyvider.cty.CtyList(element_type: CtyType)`: Represents a list of elements of the same type.
*   `pyvider.cty.CtySet(element_type: CtyType)`: Represents a set of unique elements of the same type.
*   `pyvider.cty.CtyMap(value_type: CtyType)`: Represents a map with string keys and values of the same type.

### Structural Types

*   `pyvider.cty.CtyObject(attribute_types: dict[str, CtyType])`: Represents an object with a fixed set of named attributes.
*   `pyvider.cty.CtyTuple(element_types: list[CtyType])`: Represents a sequence of elements with a fixed length and potentially different types.

### Special Types

*   `pyvider.cty.CtyDynamic`: Represents a type that can hold any kind of `cty` value.
*   `pyvider.cty.CtyCapsule(name: str)`: Represents a type for encapsulating foreign data types.

## Core Values

### `pyvider.cty.CtyValue`

The abstract base class for all `cty` values.

*   **`raw_value`** (property): Returns the raw Python value.
*   **`type`** (property): Returns the `CtyType` of the value.
*   **`marks`** (property): Returns a set of the marks on the value.
*   **`with_marks(*marks: str) -> CtyValue`**: Returns a new value with the given marks.
*   **`has_mark(mark: str) -> bool`**: Checks if the value has a specific mark.

## Functions

The `pyvider.cty.functions` module contains a variety of functions for working with `cty` values. See Chapter 11 for a more detailed overview.
