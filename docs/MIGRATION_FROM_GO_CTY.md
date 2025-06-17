# Migration Guide: From go-cty to pyvider.cty

This guide helps developers familiar with HashiCorp's go-cty migrate to pyvider.cty.

## Overview

pyvider.cty is designed to be compatible with go-cty, making migration straightforward. Most concepts translate directly, with Python-specific adaptations for better ergonomics.

## Type System Mapping

### Basic Types

| go-cty | pyvider.cty | Notes |
|--------|-------------|-------|
| `cty.String` | `CtyString()` | Direct equivalent |
| `cty.Number` | `CtyNumber()` | Handles both int and float (internally Decimal) |
| `cty.Bool` | `CtyBool()` | Direct equivalent |

### Collection Types

| go-cty | pyvider.cty | Example |
|--------|-------------|---------|
| `cty.List(cty.String)` | `CtyList(element_type=CtyString())` | List of strings |
| `cty.Set(cty.Number)` | `CtySet(element_type=CtyNumber())` | Set of numbers |
| `cty.Map(cty.Bool)` | `CtyMap(key_type=CtyString(), value_type=CtyBool())` | String-keyed map to boolean values |

### Structural Types

```python
# go-cty Example (conceptual)
# objType := cty.Object(map[string]cty.Type{
#     "name": cty.String,
#     "age":  cty.Number,
# })

# pyvider.cty
# Define the schema as a dictionary
obj_schema_dict = {
    "name": CtyString(),
    "age": CtyNumber(),
}
# Create a CtyObject type instance from the schema dictionary
obj_type = CtyObject(obj_schema_dict)
```

## Value Creation

### Basic Values

```python
# go-cty
# val := cty.StringVal("hello")
# num := cty.NumberIntVal(42)

# pyvider.cty
val_str = CtyValue.string("hello")
val_num = CtyValue.number(42) # Stored as Decimal internally
```

### Collection Values

```python
# go-cty
# listVal := cty.ListVal([]cty.Value{
#     cty.StringVal("a"),
#     cty.StringVal("b"),
# })

# pyvider.cty
# To create a CtyList CtyValue directly:
list_val = CtyValue.list(CtyString(), [ # Use CtyString() instance as element type for factory
    CtyValue.string("a"),               # Items are CtyValue instances
    CtyValue.string("b"),
])

# More commonly when creating an object with a schema that includes a list:
# person_schema_dict = {"tags": CtyList(element_type=CtyString())} (defined elsewhere)
# person_type = CtyObject(person_schema_dict)
# person = CtyValue.object(person_schema_dict, {"tags": ["a", "b"]}) # Native list here
```

### Object Values

```python
# go-cty
# objVal := cty.ObjectVal(map[string]cty.Value{
#     "name": cty.StringVal("Alice"),
#     "age":  cty.NumberIntVal(30),
# })

# pyvider.cty
# obj_schema_dict and obj_type defined in "Structural Types" section
# Pass the schema *dictionary* to CtyValue.object for robustness with current library version
obj_val = CtyValue.object(obj_schema_dict, {
    "name": "Alice", # Native Python string
    "age": 30,       # Native Python number
})
# The documentation might also show passing obj_type (CtyObject instance).
# If CtyValue.object(obj_type, ...) works, it means the factory can handle CtyObject instances.
# Current robust pattern is CtyValue.object(schema_dictionary, native_values).

# Alternatively, using pre-made CtyValues:
# obj_val_from_cty = CtyValue.object(obj_schema_dict, {
#     "name": CtyValue.string("Alice"),
#     "age": CtyValue.number(30),
# })
```

## Working with Values

### Accessing Data

```python
# go-cty
# name := objVal.GetAttr("name").AsString()
# elem := listVal.Index(cty.NumberIntVal(0)).AsString()

# pyvider.cty
# obj_val and list_val from examples above

# Accessing attributes from an object CtyValue
name_cty_value = obj_val["name"] # This is a CtyValue
name_native = name_cty_value.value # Access the native Python value using .value
print(f"Name: {name_native}") # Output: Alice

# Accessing elements from a list CtyValue
# list_val.value is a Python list of CtyValues
element_cty_value = list_val.value[0] # This is a CtyValue
element_native = element_cty_value.value # Access the native Python value
print(f"First element: {element_native}") # Output: a
```

### Type Checking

```python
# go-cty
# if val.Type().Equals(cty.String) {
#     str := val.AsString()
# }

# pyvider.cty
# val_str is CtyValue.string("hello") from above
if isinstance(val_str.type, CtyString): # Check the .type attribute against the CtyType class
    native_string = val_str.value # Access the native value using .value
    print(f"It's a string: {native_string}")
```

## Serialization

### JSON

```python
from decimal import Decimal # Important for number comparisons

# go-cty (conceptual)
# jsonBytes, err := json.Marshal(val, val.Type())
# newVal, err := json.Unmarshal(jsonBytes, valType)

# pyvider.cty
# val_str is CtyValue.string("hello")
# obj_val is the object CtyValue created earlier (using obj_schema_dict)
# obj_type is its schema (CtyObject instance e.g. CtyObject(obj_schema_dict))

json_string_from_simple_val = val_str.to_json_string()
print(f"JSON from simple value: {json_string_from_simple_val}")

json_string_from_object = obj_val.to_json_string()
print(f"JSON from object value: {json_string_from_object}")

# Deserializing: provide the target CtyType instance
deserialized_str_val = CtyValue.from_json_string(json_string_from_simple_val, CtyString())
print(f"Deserialized string: {deserialized_str_val.value}")

deserialized_obj_val = CtyValue.from_json_string(json_string_from_object, obj_type)
print(f"Deserialized object name: {deserialized_obj_val['name'].value}")
assert deserialized_obj_val['age'].value == Decimal(30) # CtyNumber values are Decimals
```

### MessagePack

```python
# go-cty (conceptual)
# msgpackBytes, err := msgpack.Marshal(val, val.Type())
# newVal, err := msgpack.Unmarshal(msgpackBytes, valType)

# pyvider.cty
# obj_val and obj_type from previous examples
msgpack_bytes_from_object = obj_val.to_msgpack_bytes()
print(f"MessagePack from object (bytes): {msgpack_bytes_from_object!r}") # !r for bytes

deserialized_obj_mp = CtyValue.from_msgpack_bytes(msgpack_bytes_from_object, obj_type)
print(f"Deserialized object from MessagePack, name: {deserialized_obj_mp['name'].value}")
```

## Key Differences

1.  **Type Instantiation**: Python types are instantiated, e.g., `CtyString()`. Collections require keyword arguments for element/value types: `CtyList(element_type=CtyString())`, `CtyMap(key_type=CtyString(), value_type=CtyBool())`.
2.  **Value Access**: Use the `.value` property to get the native Python value from a `CtyValue`. Methods like `.as_string()` do not exist. For lists, `list_cty_value.value` returns a Python list of `CtyValue` items, so iterate and access `.value` on each item.
3.  **Null/Unknown**: Use `CtyValue.null(type_instance)` and `CtyValue.unknown(type_instance)`. Accessing attributes on a null object CtyValue raises a `TypeError`.
4.  **Error Handling**: Python uses exceptions (e.g., `CtyValidationError`, `TypeError`).
5.  **Object Creation**: `CtyValue.object(schema_dict, values_dict)` is the robust pattern, where `schema_dict` is the dictionary defining attribute types.

## Common Patterns

### Dynamic Type Handling

```python
from pyvider.cty import CtyDynamic # Ensure CtyDynamic is imported

# CtyDynamic is used as a type within a schema dictionary:
schema_with_dynamic_dict = {
    "id": CtyString(),
    "data": CtyDynamic()
}
# schema_with_dynamic_type = CtyObject(schema_with_dynamic_dict) # Optional CtyObject instance

# Create a CtyValue using this schema dictionary
val_with_dynamic_str = CtyValue.object(schema_with_dynamic_dict, {"id": "item1", "data": "some text"})
val_with_dynamic_num = CtyValue.object(schema_with_dynamic_dict, {"id": "item2", "data": 123})

print(f"Dynamic string data: {val_with_dynamic_str['data'].value}") # Native string
print(f"Dynamic number data type: {val_with_dynamic_num['data'].type}") # Resolved to CtyNumber
print(f"Dynamic number data value: {val_with_dynamic_num['data'].value}") # Native Decimal

# Standalone CtyValue whose type is CtyDynamic (less common than schema usage):
# Note: CtyValue.dynamic() factory does not exist.
# To create a CtyValue that IS dynamic, you assign a CtyValue of a concrete type to a dynamic slot,
# or construct it with vtype=CtyDynamic() if holding a raw Python value before its type is known/resolved.
dynamic_val_explicit = CtyValue(vtype=CtyDynamic(), value="explicitly dynamic")
print(f"Explicit dynamic: type={dynamic_val_explicit.type}, value={dynamic_val_explicit.value}")
```

### Path Operations

```python
from pyvider.cty import CtyPath # Ensure CtyPath is imported

# Constructing paths using CtyPath class methods:
path_to_user_name = CtyPath.get_attr("users").index_step(0).child("name")
path_to_config_setting = CtyPath.get_attr("config").key_step("setting")

# Example data structure:
user_list_schema = CtyList(element_type=CtyObject({"name": CtyString()}))
config_map_schema = CtyMap(value_type=CtyString()) # Assumes string keys default for CtyMap

root_schema_dict = {
    "users": user_list_schema,
    "config": config_map_schema,
    "simple": CtyString()
}
root_type = CtyObject(root_schema_dict) # CtyObject type instance

root_value = CtyValue.object(root_schema_dict, { # Use schema_dict for creation
    "users": [{"name": "Alice"}, {"name": "Bob"}], # Native list of dicts
    "config": {"setting": "enabled"},             # Native dict
    "simple": "hello"
})

# Applying paths to a CtyValue:
try:
    user_name_cty_val = path_to_user_name.apply_path(root_value) # Returns a CtyValue
    print(f"Name via path: {user_name_cty_val.value}") # Output: Alice

    setting_cty_val = path_to_config_setting.apply_path(root_value)
    print(f"Setting via path: {setting_cty_val.value}") # Output: enabled

    # Applying paths to a CtyType instance (e.g., CtyObject):
    user_name_type = path_to_user_name.apply_path_type(root_type)
    print(f"Type via path: {user_name_type}") # Output: CtyString()

except Exception as e:
    print(f"Error applying path: {e}")
```

### Error Handling

```python
from pyvider.cty.exceptions import CtyError, CtyValidationError

# Reusing obj_schema_dict from earlier examples
try:
    invalid_data = {"name": 123, "age": "thirty"} # name is number, age is string
    # Use schema_dict for CtyValue.object
    val = CtyValue.object(obj_schema_dict, invalid_data)
except CtyValidationError as e:
    print(f"Validation failed as expected: {e}")
except CtyError as e:
    print(f"A Cty specific error occurred: {e}")
```

## Best Practices

1.  **Schema Definition**: Define schemas using dictionaries mapping names to `CtyType` instances (e.g., `CtyString()`, `CtyList(element_type=...)`). Create `CtyObject` instances from these dictionaries.
2.  **Value Creation**: For `CtyValue.object`, robustly pass the schema *dictionary*. For `CtyValue.list`, pass the element type *instance*. Provide native Python data where possible; the library handles conversion.
3.  **Handle Null/Unknown**: Check `cty_value.is_null` and `cty_value.is_unknown` properties. Remember accessing attributes on a null object CtyValue raises `TypeError`.
4.  **Access Native Data**: Use the `.value` property. For list `CtyValue`s, `.value` returns a list of `CtyValue` items.
5.  **Serialization**: Use `value.to_json_string()` and `CtyValue.from_json_string(str, type_instance)`.

## Troubleshooting
(Content of Troubleshooting can remain mostly the same)

### MessagePack Compatibility
If you encounter MessagePack deserialization issues between go-cty and pyvider.cty:
1.  Use JSON for critical cross-language communication as it's often more robust for complex structures.
2.  Test specific data structures that will be exchanged.
3.  Report issues with minimal reproducible examples.

### Type Mismatches
When types don't match expected:
1.  Use `repr(cty_value.type)` or `print(cty_value.type)` to inspect type structure.
2.  Verify collection element types (e.g., `CtyList(element_type=...)`).
3.  Check for null/unknown values using `.is_null` and `.is_unknown`.

## Need Help?

- See [examples/](../examples/) for working code.
- Check [API documentation](api/). <!-- TODO: Verify this link, docs/api/ was not found -->
- Open an issue for migration problems on the project's GitHub repository.
- Email: code@provide.io
