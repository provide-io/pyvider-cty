# Chapter 7: Structural Types

Structural types represent more complex, structured data. They allow you to define the shape and layout of your data with a high degree of precision.

There are two structural types in `pyvider.cty`:

*   `CtyObject`: Represents an object with a fixed set of named attributes, each with its own type.
*   `CtyTuple`: Represents a sequence of elements with a fixed length, where each element can have a different type.

## `CtyObject`

The `CtyObject` type represents an object with a fixed set of named attributes. Each attribute has its own type, which you must specify when creating the `CtyObject` type.

To create a `CtyObject` type, you must provide a dictionary that maps the attribute names to their corresponding `cty` types:

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyBool

user_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
    "is_active": CtyBool(),
})

# Validate a valid user object
user_data = {
    "name": "Alice",
    "age": 30,
    "is_active": True,
}
cty_user = user_type.validate(user_data)
assert cty_user.raw_value == user_data

# Validate an object with a missing attribute (will raise a ValidationError)
try:
    user_type.validate({"name": "Bob", "age": 40})
except Exception as e:
    print(f"Validation failed: {e}")

# Validate an object with an extra attribute (will raise a ValidationError)
try:
    user_type.validate({
        "name": "Charlie",
        "age": 50,
        "is_active": False,
        "extra": "attribute",
    })
except Exception as e:
    print(f"Validation failed: {e}")
```

## `CtyTuple`

The `CtyTuple` type represents a sequence of elements with a fixed length, where each element can have a different type.

To create a `CtyTuple` type, you must provide a list of the `cty` types of the elements in the tuple:

```python
from pyvider.cty import CtyTuple, CtyString, CtyNumber, CtyBool

tuple_type = CtyTuple([
    CtyString(),
    CtyNumber(),
    CtyBool(),
])

# Validate a valid tuple
tuple_data = ["hello", 123, True]
cty_tuple = tuple_type.validate(tuple_data)
assert cty_tuple.raw_value == tuple_data

# Validate a tuple with the wrong number of elements (will raise a ValidationError)
try:
    tuple_type.validate(["hello", 123])
except Exception as e:
    print(f"Validation failed: {e}")

# Validate a tuple with an element of the wrong type (will raise a ValidationError)
try:
    tuple_type.validate(["hello", "world", True])
except Exception as e:
    print(f"Validation failed: {e}")
```
