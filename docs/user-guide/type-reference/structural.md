# Structural Types

Structural types represent more complex, structured data. They allow you to define the shape and layout of your data with a high degree of precision.

There are two structural types in `pyvider.cty`:

*   `CtyObject`: Represents an object with a fixed set of named attributes, each with its own type.
*   `CtyTuple`: Represents a sequence of elements with a fixed length, where each element can have a different type.

## `CtyObject`

The `CtyObject` type represents an object with a fixed set of named attributes. Each attribute has its own type, which you must specify when creating the `CtyObject` type.

### Syntax Options

`CtyObject` supports two equivalent syntaxes for defining attribute types:

```python
# Explicit syntax (recommended for clarity and consistency)
user_type = CtyObject(
    attribute_types={"name": CtyString(), "age": CtyNumber()},
    optional_attributes={"age"}
)

# Shorthand syntax (also supported)
user_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
```

Both syntaxes are valid, but the explicit `attribute_types=` parameter is recommended for consistency and clarity across your codebase. Use the shorthand syntax only when appropriate for your team's coding standards.

### Optional Attributes

You can also define certain attributes as optional. If an optional attribute is missing from the input data during validation, it will be present in the resulting `CtyValue` as a `null` value of the correct type.

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyBool

# Define a schema with 'is_active' as an optional attribute
user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "is_active": CtyBool(),
    },
    optional_attributes={"is_active"}
)

# Validate data where the optional attribute is missing
user_data = {"name": "Alice", "age": 30}
cty_user = user_type.validate(user_data)

# Accessing the missing optional attribute returns a null value
active_val = cty_user["is_active"]
print(f"Active: {active_val.raw_value} (Is Null: {active_val.is_null})")

# Validation fails for missing required attributes or extra attributes
try:
    user_type.validate({"name": "Bob"}) # Missing 'age'
except Exception as e:
    print(f"\nValidation failed as expected: {e}")
```

## `CtyTuple`

The `CtyTuple` type represents a sequence of elements with a fixed length, where each element can have a different type.

```python
from pyvider.cty import CtyTuple, CtyString, CtyNumber, CtyBool

tuple_type = CtyTuple(element_types=(
    CtyString(),
    CtyNumber(),
    CtyBool(),
))

# Validate a valid tuple
tuple_data = ["hello", 123, True]
cty_tuple = tuple_type.validate(tuple_data)
assert cty_tuple.raw_value == ("hello", 123, True)

# Validate a tuple with the wrong number of elements (will raise a ValidationError)
try:
    tuple_type.validate(["hello", 123])
except Exception as e:
    print(f"Validation failed as expected: {e}")
```

## See Also

- **[Understanding Types](../core-concepts/types.md)** - Core type system concepts
- **[Collection Types](collections.md)** - List, Map, and Set types
- **[Dynamic Types](dynamic.md)** - Using dynamic types within structures
- **[Path Navigation](../advanced/path-navigation.md)** - Navigating nested structures
- **[Terraform Interoperability](../advanced/terraform-interop.md)** - Working with Terraform object types
