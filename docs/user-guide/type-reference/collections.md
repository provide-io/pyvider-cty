# Collection Types

Collection types represent collections of other types. They allow you to group multiple values together into a single, cohesive unit.

There are three collection types in `pyvider.cty`:

*   `CtyList`: Represents a list of elements of the same type.
*   `CtySet`: Represents a set of unique elements of the same type.
*   `CtyMap`: Represents a map of key-value pairs, where the keys are strings and the values are all of the same type.

## `CtyList`

The `CtyList` type represents a list of elements, where all elements are of the same type.

To create a `CtyList` type, you must specify the type of the elements in the list:

```python
from pyvider.cty import CtyList, CtyString

string_list_type = CtyList(element_type=CtyString())

# Validate a valid list of strings
cty_list = string_list_type.validate(["a", "b", "c"])

# Note: raw_value returns a tuple for immutability
assert cty_list.raw_value == ("a", "b", "c")
assert isinstance(cty_list.raw_value, tuple)

# Validate a list with an invalid element (will raise a ValidationError)
try:
    string_list_type.validate(["a", "b", 123])
except Exception as e:
    print(f"Validation failed: {e}")
```

## `CtySet`

The `CtySet` type represents a set of unique elements of the same type. Like `CtyList`, you must specify the element type when creating a `CtySet` type.

```python
from pyvider.cty import CtySet, CtyNumber

number_set_type = CtySet(element_type=CtyNumber())

# Validate a valid set of numbers
cty_set = number_set_type.validate({1, 2, 3})
assert sorted(list(cty_set.raw_value)) == [1, 2, 3]

# Validate a set with duplicate elements (will be silently deduplicated)
cty_set_dedup = number_set_type.validate({1, 2, 2, 3})
assert sorted(list(cty_set_dedup.raw_value)) == [1, 2, 3]

# Validate a set with an invalid element (will raise a ValidationError)
try:
    number_set_type.validate({1, 2, "c"})
except Exception as e:
    print(f"Validation failed: {e}")
```

## `CtyMap`

The `CtyMap` type represents a map of key-value pairs, where the keys are strings and the values are all of the same type.

To create a `CtyMap` type, you must specify the type of the values in the map:

```python
from pyvider.cty import CtyMap, CtyBool

bool_map_type = CtyMap(element_type=CtyBool())

# Validate a valid map of booleans
cty_map = bool_map_type.validate({"a": True, "b": False})
assert cty_map.raw_value == {"a": True, "b": False}

# Validate a map with an invalid value (will raise a ValidationError)
try:
    bool_map_type.validate({"a": True, "b": 123})
except Exception as e:
    print(f"Validation failed: {e}")
```

## See Also

- **[Understanding Types](../core-concepts/types.md)** - Core type system concepts
- **[Primitive Types](primitives.md)** - String, Number, and Bool types
- **[Structural Types](structural.md)** - Object and Tuple types
- **[Collection Functions](../advanced/functions.md)** - Built-in functions for working with collections
- **[Validation](../core-concepts/validation.md)** - Understanding validation behavior
