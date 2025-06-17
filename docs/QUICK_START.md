# Quick Start Guide

Get up and running with pyvider.cty in 5 minutes!

## Installation

```bash
pip install pyvider-cty==0.1.0-preview1
```

## Basic Usage

### 1. Import Required Types

```python
from pyvider.cty import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyObject,
    CtyValue
)
```

### 2. Define a Type Schema

```python
# Simple types
name_type = CtyString()
age_type = CtyNumber()
active_type = CtyBool()

# Collection type
tags_type = CtyList(CtyString())

# Complex object type
person_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
    "active": CtyBool(),
    "tags": CtyList(CtyString())
})
```

### 3. Create Values

```python
# Simple values
name = CtyValue.string("Alice")
age = CtyValue.number(30)
active = CtyValue.bool(True)

# List value
tags = CtyValue.list([
    CtyValue.string("developer"),
    CtyValue.string("python")
])

# Object value
person = CtyValue.object(person_type, {
    "name": name,
    "age": age,
    "active": active,
    "tags": tags
})
```

### 4. Access Values

```python
# Direct access
print(person["name"].as_string())  # "Alice"
print(person["age"].as_number())   # 30

# Iterate lists
for tag in person["tags"].as_list():
    print(tag.as_string())

# Check properties
print(person.is_null)      # False
print(person.is_unknown)   # False
```

### 5. Serialize/Deserialize

```python
from pyvider.cty.conversion import to_json, from_json

# To JSON
json_str = to_json(person)
print(json_str)

# From JSON
loaded = from_json(json_str, person_type)
assert loaded["name"].as_string() == "Alice"
```

## Common Patterns

### Working with Unknown Values

```python
# Create unknown value
unknown_person = CtyValue.unknown(person_type)

# Check before accessing
if not unknown_person.is_unknown:
    name = unknown_person["name"]
```

### Handling Null Values

```python
# Create null value
null_person = CtyValue.null(person_type)

# Safe access pattern
if person.is_null:
    print("Person is null")
else:
    print(f"Name: {person['name'].as_string()}")
```

### Type Validation

```python
try:
    # This will raise an error - wrong type!
    bad_person = CtyValue.object(person_type, {
        "name": CtyValue.number(123),  # Should be string!
        "age": CtyValue.number(30),
        "active": CtyValue.bool(True),
        "tags": CtyValue.list([])
    })
except Exception as e:
    print(f"Validation error: {e}")
```

### Dynamic Types

```python
from pyvider.cty import CtyDynamic

# Accept any type
flexible_type = CtyObject({
    "id": CtyString(),
    "data": CtyDynamic()  # Can be anything
})

# Create with different data types
config1 = CtyValue.object(flexible_type, {
    "id": CtyValue.string("config-1"),
    "data": CtyValue.string("text data")
})

config2 = CtyValue.object(flexible_type, {
    "id": CtyValue.string("config-2"),
    "data": CtyValue.number(42)
})
```

## Next Steps

- Read the [full documentation](README.md)
- Explore [examples](../examples/)
- Learn about [migration from go-cty](MIGRATION_FROM_GO_CTY.md)
- Check out [API reference](api/)

## Need Help?

- 📧 Email: code@provide.io
- 🐛 [GitHub Issues](https://github.com/provide/pyvider-cty/issues)
- 💬 [GitHub Discussions](https://github.com/provide/pyvider-cty/discussions)
