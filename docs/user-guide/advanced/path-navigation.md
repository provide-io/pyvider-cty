# Path Navigation

`pyvider.cty` provides a powerful path language to navigate and access elements within complex `CtyValue` structures. This is particularly useful for debugging, validation, and extracting specific data from nested objects and collections.

## The `CtyPath` Class

The `CtyPath` class is the core of the path language. It represents a sequence of steps to navigate through a `CtyValue`.

### Creating a Path

You can create a path using the class methods of `CtyPath`:

```python
from pyvider.cty.path import CtyPath

# Path to an attribute
path_to_attr = CtyPath.get_attr("my_attr")

# Path to a list/tuple element
path_to_index = CtyPath.index(0)

# Path to a map key
path_to_key = CtyPath.key("my_key")
```

Paths can be chained together to create more complex navigation:

```python
complex_path = CtyPath.get_attr("users").index(0).child("name")
```

### Applying a Path

The `apply_path` method of a `CtyPath` object is used to navigate to a specific element within a `CtyValue`:

```python
from pyvider.cty import CtyObject, CtyString

# Create a CtyValue
user_type = CtyObject(attribute_types={"name": CtyString()})
user_val = user_type.validate({"name": "Alice"})

# Create a path
name_path = CtyPath.get_attr("name")

# Apply the path
name_val = name_path.apply_path(user_val)

assert name_val.raw_value == "Alice"
```

### Applying a Path to a Type

The `apply_path_type` method of a `CtyPath` object is used to determine the type of the element that the path would navigate to:

```python
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.path import CtyPath

user_type = CtyObject(attribute_types={"name": CtyString()})
name_path = CtyPath.get_attr("name")

# Apply the path to the type
name_type = name_path.apply_path_type(user_type)

assert name_type == CtyString()
```

This is useful for static analysis and validation without needing an actual `CtyValue`.

## See Also

- **[Path API Reference](../../api/path.md)** - Complete path navigation API
- **[Structural Types](../type-reference/structural.md)** - Working with Object and Tuple types
- **[Troubleshooting](../../reference/troubleshooting.md)** - Debugging nested structures
