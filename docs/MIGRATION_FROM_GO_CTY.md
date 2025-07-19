# Migration Guide: From go-cty to pyvider.cty

This guide helps developers familiar with HashiCorp's go-cty migrate to pyvider.cty.

## Overview

pyvider.cty is designed to be compatible with go-cty, making migration straightforward. Most concepts translate directly, with Python-specific adaptations for better ergonomics.

## Type System Mapping

### Basic Types

| go-cty | pyvider.cty | Notes |
|--------|-------------|-------|
| `cty.String` | `CtyString()` | Direct equivalent |
| `cty.Number` | `CtyNumber()` | Handles both int and float |
| `cty.Bool` | `CtyBool()` | Direct equivalent |

### Collection Types

| go-cty | pyvider.cty | Example |
|--------|-------------|---------|
| `cty.List(cty.String)` | `CtyList(element_type=CtyString())` | List of strings |
| `cty.Set(cty.Number)` | `CtySet(element_type=CtyNumber())` | Set of numbers |
| `cty.Map(cty.Bool)` | `CtyMap(element_type=CtyBool())` | String-keyed map |

### Structural Types

```python
# go-cty
objType := cty.Object(map[string]cty.Type{
    "name": cty.String,
    "age":  cty.Number,
})

# pyvider.cty
obj_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
})
```

## Value Creation

### Basic Values

```python
# go-cty
val := cty.StringVal("hello")
num := cty.NumberIntVal(42)

# pyvider.cty
val = CtyString().validate("hello")
num = CtyNumber().validate(42)
```

### Collection Values

```python
# go-cty
listVal := cty.ListVal([]cty.Value{
    cty.StringVal("a"),
    cty.StringVal("b"),
})

# pyvider.cty
list_val = CtyList(element_type=CtyString()).validate([
    "a",
    "b",
])
```

### Object Values

```python
# go-cty
objVal := cty.ObjectVal(map[string]cty.Value{
    "name": cty.StringVal("Alice"),
    "age":  cty.NumberIntVal(30),
})

# pyvider.cty
obj_val = obj_type.validate({
    "name": "Alice",
    "age": 30,
})
```

## Working with Values

### Accessing Data

```python
# go-cty
name := objVal.GetAttr("name")
elem := listVal.Index(cty.NumberIntVal(0))

# pyvider.cty
name = obj_val["name"]
elem = list_val[0]
```

### Type Checking

```python
# go-cty
if val.Type().Equals(cty.String) {
    str := val.AsString()
}

# pyvider.cty
if val.type == CtyString():
    str_val = val.value
```

## Serialization

### JSON

```python
# go-cty
jsonBytes, err := json.Marshal(val, val.Type())
newVal, err := json.Unmarshal(jsonBytes, valType)

# pyvider.cty
from pyvider.cty.conversion import to_json, from_json

json_str = to_json(val)
new_val = from_json(json_str, val_type)
```

### MessagePack

```python
# go-cty
msgpackBytes, err := msgpack.Marshal(val, val.Type())

# pyvider.cty
from pyvider.cty.conversion import to_msgpack, from_msgpack

msgpack_bytes = to_msgpack(val)
new_val = from_msgpack(msgpack_bytes, val_type)
```

## Key Differences

1. **Instantiation**: Python types require parentheses: `CtyString()` vs `cty.String`
2. **Null/Unknown**: Use `CtyValue.null(type)` and `CtyValue.unknown(type)`
3. **Error Handling**: Python uses exceptions instead of error returns
4. **Indexing**: Python uses native indexing syntax (`val[0]`, `val["key"]`)

## Common Patterns

### Dynamic Type Handling

```python
# Check if type is dynamic
if isinstance(val.type, CtyDynamic):
    # Handle dynamic value
    pass

# Create dynamic value
dyn_val = CtyDynamic().validate(actual_value)
```

### Path Operations

```python
# Build a path
path = CtyPath.get_attr("users").index_step(0).child("name")

# Apply path to value
result = path.apply_path(root_value)
```

### Error Handling

```python
from pyvider.cty.exceptions import CtyError

try:
    val = obj_type.validate(data)
except CtyError as e:
    print(f"Validation failed: {e}")
```

## Best Practices

1. **Use Type Validation**: Always validate data against types
2. **Handle Null/Unknown**: Check `is_null` and `is_unknown` properties
3. **Leverage Type Safety**: Use type-specific accessors (`as_string()`, etc.)
4. **Test Serialization**: Verify cross-language compatibility early

## Troubleshooting

### MessagePack Compatibility

If you encounter MessagePack deserialization issues between go-cty and pyvider.cty:
1. Use JSON for critical cross-language communication
2. Test specific data structures that will be exchanged
3. Report issues with minimal reproducible examples

### Type Mismatches

When types don't match expected:
1. Use `repr(type)` to inspect type structure
2. Verify collection element types match
3. Check for null/unknown values

## Need Help?

- See [examples/](../examples/) for working code
- Check [API documentation](api/)
- Open an issue for migration problems
- Email: code@provide.io
