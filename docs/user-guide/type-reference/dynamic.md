# Dynamic Types

The `CtyDynamic` type is a special type in `pyvider.cty` that can represent any type of value. It is useful when you are working with data that has an unknown or varying structure.

## The `CtyDynamic` Type

When you validate a value against a `CtyDynamic` type, the resulting `cty` value will have the most specific type that can be inferred from the raw Python value.

```python
from pyvider.cty import CtyDynamic, CtyString, CtyNumber

dynamic_type = CtyDynamic()

# Validate a string
cty_string = dynamic_type.validate("hello")
# The resulting value is a CtyDynamic that wraps a CtyString
assert isinstance(cty_string.value.type, CtyString)

# Validate a number
cty_number = dynamic_type.validate(123)
assert isinstance(cty_number.value.type, CtyNumber)
```

## `CtyDynamic` in Collections

You can also use the `CtyDynamic` type within collection and structural types. This is powerful for creating flexible data structures.

### Example: Tuple with a Dynamic Element

Here we define a tuple where the last element can be of any type.

```python
from pyvider.cty import CtyDynamic, CtyNumber, CtyObject, CtyString, CtyTuple

# 1. Define a tuple type with a dynamic last element.
coordinate_type = CtyTuple(
    element_types=(CtyString(), CtyNumber(), CtyNumber(), CtyDynamic())
)

# 2. Create raw data that matches the tuple's structure.
point_data = ("GPS", 37.7749, -122.4194, {"accuracy": 10})

# 3. Validate the data.
validated_tuple = coordinate_type.validate(point_data)

# 4. Access the dynamic element.
# CtyDynamic.validate infers the most specific type, which is CtyObject here.
metadata_val = validated_tuple
print(f"Metadata Type (inferred): {metadata_val.value.type}")
print(f"Metadata is an object: {isinstance(metadata_val.value.type, CtyObject)}")
print(f"Metadata accuracy: {metadata_val.value['accuracy'].raw_value}")
```

## See Also

- **[Understanding Types](../core-concepts/types.md)** - Core type system concepts
- **[Structural Types](structural.md)** - Object and Tuple types that can contain dynamic elements
- **[Type Conversion](../core-concepts/conversion.md)** - Understanding type inference and conversion
- **[Validation](../core-concepts/validation.md)** - How dynamic validation works
