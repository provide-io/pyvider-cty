# Capsule Types

The `CtyCapsule` type is a special type in `pyvider.cty` that allows you to encapsulate and protect foreign data types within the `cty` system. This is useful when you need to work with data that cannot be represented by the standard `cty` types, such as file handles, database connections, or other external resources.

## The `CtyCapsule` Type

To create a `CtyCapsule` type, you must provide a name for the type and the
Python type it is allowed to wrap:

```python
from pyvider.cty import CtyCapsule

class FileHandle:
    def __init__(self, path):
        self.path = path

file_handle_type = CtyCapsule("FileHandle", FileHandle)
```

This creates a new `CtyCapsule` type that can be used to encapsulate
`FileHandle` objects specifically -- `validate` checks the wrapped value
against `py_type` with `isinstance`, so it refuses any other kind of object.

## Encapsulating and Accessing Data

You can encapsulate a foreign data type in a `CtyCapsule` value using the `validate` method:

```python
file_handle = FileHandle("/path/to/file")

# Encapsulate the file handle in a CtyCapsule value
cty_file_handle = file_handle_type.validate(file_handle)
```

You can then access the encapsulated object using the `raw_value` property:

```python
encapsulated_handle = cty_file_handle.raw_value
assert encapsulated_handle.path == "/path/to/file"
```

## Type Safety

`CtyCapsule` types are type-safe. This means that you can only encapsulate objects of the correct type in a `CtyCapsule` value.

```python
# This will raise a ValidationError
try:
    file_handle_type.validate("not a file handle")
except Exception as e:
    print(f"Validation failed: {e}")
```

This type safety ensures that you can't accidentally mix up different types of encapsulated data.

## Capsules in Sets

A `CtyCapsule` value is hashable, so it can be an element type for `CtySet`.
Without a custom `hash_fn` (see `CtyCapsuleWithOps` for supplying one), every
value of a given capsule type hashes the same way -- capsules hash *per
type*, not per wrapped object, which mirrors go-cty's own default. That is a
statement about hash bucketing, not equality: two distinct `FileHandle`
instances placed in the same set both land in it, since neither has told cty
how to tell them apart.

## See Also

- **[Understanding Types](../core-concepts/types.md)** - Core type system concepts
- **[Create Custom Types](../../how-to/create-custom-types.md)** - Building custom type wrappers
- **[Serialization](../advanced/serialization.md)** - Capsule serialization considerations
- **[API Reference: Capsule Types](../../api/types/capsule.md)** - Complete capsule API documentation
