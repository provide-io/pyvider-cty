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

## Traversing a Value

Building paths by hand is fine when you know the shape you're navigating to. When you need to visit *everything* inside a value, `pyvider.cty` provides three traversal functions, mirroring go-cty's `cty/walk.go`: `deep_values`, `walk` and `transform`.

`deep_values` is a generator that yields every value inside a value, itself first, each paired with the `CtyPath` that reaches it:

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, deep_values

user_type = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})
user_val = user_type.validate({"name": "Alice", "age": 30})

for path, value in deep_values(user_val):
    print(path, "->", value)
```

A map's keys and an object's attributes are visited in **sorted order**, not the order they were inserted or declared — go-cty does this "so that results will always be stable given the same input", and `deep_values`, `walk` and `transform` all follow the same rule:

```python
from pyvider.cty import CtyMap, CtyString, deep_values

map_type = CtyMap(element_type=CtyString())
map_val = map_type.validate({"zebra": "z", "apple": "a", "mango": "m"})

for path, value in deep_values(map_val):
    print(path)
# (root)
# ['apple']
# ['mango']
# ['zebra']
```

`walk` is the same traversal driven by a callback that decides whether to descend — return `False` to skip a value's contents and continue with its siblings:

```python
from pyvider.cty import walk

def visit(path, value) -> bool:
    print("visiting", path)
    return True

walk(user_val, visit)
```

`transform` rebuilds a value bottom-up, applying a function to every value inside it, innermost first — this is how you express what looks like a deep, in-place edit of an otherwise immutable structure:

```python
from pyvider.cty import CtyString, transform

def upper_strings(path, value):
    if value.type == CtyString() and not value.is_null and not value.is_unknown:
        return value.type.validate(value.raw_value.upper())
    return value

shouted = transform(user_val, upper_strings)
assert shouted.raw_value == {"name": "ALICE", "age": 30}
```

`fn` is responsible for preserving each container's invariants — changing the type of a list element or an object attribute is refused when the container is rebuilt. A tuple is the exception: since its type already records each element's type individually, a transform that changes an element's type changes the tuple's type along with it.

### Sets in a Path

A set has no positional index, so go-cty addresses a set element by the element itself — "a set element effectively acts as its own key in the set". `pyvider.cty` expresses that as a `KeyStep` whose key is the element's own `CtyValue`, and elements are visited in the set's canonical sorted order:

```python
from pyvider.cty import CtySet, CtyString, deep_values

set_type = CtySet(element_type=CtyString())
set_val = set_type.validate({"b", "a", "c"})

for path, value in deep_values(set_val):
    print(path)
# (root)
# ['a']
# ['b']
# ['c']
```

Applying a path back through that same `KeyStep` looks up the element by value, not by position:

```python
first_path, _ = list(deep_values(set_val))[1]  # [0] is the set itself
found = first_path.steps[0].apply(set_val)
assert found.raw_value == "a"
```

## See Also

- **[Path API Reference](../../api/path.md)** - Complete path navigation API
- **[Structural Types](../type-reference/structural.md)** - Working with Object and Tuple types
- **[Troubleshooting](../../reference/troubleshooting.md)** - Debugging nested structures
