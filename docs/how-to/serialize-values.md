# How to Serialize and Deserialize Values

This guide shows you how to serialize pyvider.cty values to MessagePack format for storage or transmission, and how to deserialize them back.

## Why MessagePack?

MessagePack is a binary serialization format that:
- Is more compact than JSON
- Preserves type information precisely
- Is compatible with go-cty for cross-language interoperability
- Handles all cty types including marks and unknown values

## Basic Serialization

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

# 1. Create a type and value
person_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    }
)

person_value = person_type.validate({
    "name": "Alice",
    "age": 30
})

# 2. Serialize to MessagePack bytes
msgpack_bytes = cty_to_msgpack(person_value, person_type)
print(f"Serialized to {len(msgpack_bytes)} bytes")

# 3. Deserialize back to CtyValue
reconstructed = cty_from_msgpack(msgpack_bytes, person_type)

# 4. Verify it matches
assert reconstructed['name'].raw_value == "Alice"
assert reconstructed['age'].raw_value == 30
```

## Serializing Complex Structures

### Nested Objects

```python
from pyvider.cty import CtyObject, CtyString, CtyList

# Complex nested type
company_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "employees": CtyList(
            element_type=CtyObject(
                attribute_types={
                    "name": CtyString(),
                    "title": CtyString()
                }
            )
        )
    }
)

company_data = {
    "name": "Acme Corp",
    "employees": [
        {"name": "Alice", "title": "Engineer"},
        {"name": "Bob", "title": "Designer"}
    ]
}

company_value = company_type.validate(company_data)

# Serialize and deserialize
msgpack_bytes = cty_to_msgpack(company_value, company_type)
restored = cty_from_msgpack(msgpack_bytes, company_type)

# Access nested data
first_employee = restored['employees'][0]
print(first_employee['name'].raw_value)  # "Alice"
```

### Lists and Collections

```python
from pyvider.cty import CtyList, CtyString, CtyMap, CtyNumber

# List serialization
tags_type = CtyList(element_type=CtyString())
tags_value = tags_type.validate(["python", "types", "cty"])

tags_msgpack = cty_to_msgpack(tags_value, tags_type)
restored_tags = cty_from_msgpack(tags_msgpack, tags_type)

# Map serialization
scores_type = CtyMap(element_type=CtyNumber())
scores_value = scores_type.validate({"alice": 95, "bob": 87})

scores_msgpack = cty_to_msgpack(scores_value, scores_type)
restored_scores = cty_from_msgpack(scores_msgpack, scores_type)
```

## Saving to Files

```python
from pathlib import Path

def save_to_file(value, schema, filepath):
    """Save a cty value to a MessagePack file."""
    msgpack_bytes = cty_to_msgpack(value, schema)
    Path(filepath).write_bytes(msgpack_bytes)

def load_from_file(schema, filepath):
    """Load a cty value from a MessagePack file."""
    msgpack_bytes = Path(filepath).read_bytes()
    return cty_from_msgpack(msgpack_bytes, schema)

# Usage
save_to_file(person_value, person_type, "person.msgpack")
loaded_person = load_from_file(person_type, "person.msgpack")
```

## Handling Null and Unknown Values

pyvider.cty preserves null and unknown values during serialization:

```python
# Object with optional fields
user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "email": CtyString(),
        "phone": CtyString()
    },
    optional_attributes={"phone"}
)

# Create value with null field
user_value = user_type.validate({
    "name": "Alice",
    "email": "alice@example.com"
    # phone is omitted, will be null
})

# Serialize and deserialize
msgpack_bytes = cty_to_msgpack(user_value, user_type)
restored = cty_from_msgpack(msgpack_bytes, user_type)

# Null status is preserved
assert restored['phone'].is_null == True
```

## Working with Marks

Marks (metadata) are preserved during serialization:

```python
from pyvider.cty import CtyString
from pyvider.cty.marks import CtyMark

# Create a mark
sensitive_mark = CtyMark("sensitive")

# Create value with mark
password_type = CtyString()
password_value = password_type.validate("secret123")

# Add mark
marked_password = password_value.with_marks({sensitive_mark})

# Serialize preserves marks
msgpack_bytes = cty_to_msgpack(marked_password, password_type)
restored = cty_from_msgpack(msgpack_bytes, password_type)

# Mark is preserved
assert sensitive_mark in restored.marks
```

## Batch Serialization

Serialize multiple values efficiently:

```python
def serialize_batch(values_and_schemas):
    """Serialize multiple values to MessagePack."""
    serialized = []
    for value, schema in values_and_schemas:
        msgpack_bytes = cty_to_msgpack(value, schema)
        serialized.append(msgpack_bytes)
    return serialized

def deserialize_batch(msgpack_list, schema):
    """Deserialize multiple values from MessagePack."""
    values = []
    for msgpack_bytes in msgpack_list:
        value = cty_from_msgpack(msgpack_bytes, schema)
        values.append(value)
    return values

# Usage
values = [
    (person1, person_type),
    (person2, person_type),
    (person3, person_type)
]

serialized_batch = serialize_batch(values)
# ... save, transmit, etc.
restored_batch = deserialize_batch(serialized_batch, person_type)
```

## Cross-Language Interoperability

MessagePack serialization is compatible with go-cty:

```python
# Serialize in Python
python_value = person_type.validate({"name": "Alice", "age": 30})
msgpack_bytes = cty_to_msgpack(python_value, person_type)

# These bytes can be read by go-cty in Go
# And go-cty serialized bytes can be read here
```

### Sending Over Network

```python
import requests

def send_cty_value(value, schema, url):
    """Send a cty value over HTTP."""
    msgpack_bytes = cty_to_msgpack(value, schema)

    response = requests.post(
        url,
        data=msgpack_bytes,
        headers={'Content-Type': 'application/msgpack'}
    )
    return response

def receive_cty_value(response, schema):
    """Receive a cty value from HTTP response."""
    msgpack_bytes = response.content
    return cty_from_msgpack(msgpack_bytes, schema)

# Usage
send_cty_value(person_value, person_type, "https://api.example.com/person")
```

## Error Handling

Handle serialization/deserialization errors:

```python
def safe_serialize(value, schema):
    """Safely serialize with error handling."""
    try:
        return cty_to_msgpack(value, schema)
    except Exception as e:
        print(f"Serialization failed: {e}")
        return None

def safe_deserialize(msgpack_bytes, schema):
    """Safely deserialize with error handling."""
    try:
        return cty_from_msgpack(msgpack_bytes, schema)
    except Exception as e:
        print(f"Deserialization failed: {e}")
        return None
```

## Compression

For large data, combine with compression:

```python
import gzip

def serialize_compressed(value, schema):
    """Serialize and compress."""
    msgpack_bytes = cty_to_msgpack(value, schema)
    return gzip.compress(msgpack_bytes)

def deserialize_compressed(compressed_bytes, schema):
    """Decompress and deserialize."""
    msgpack_bytes = gzip.decompress(compressed_bytes)
    return cty_from_msgpack(msgpack_bytes, schema)

# Usage
compressed = serialize_compressed(large_value, large_schema)
print(f"Compressed to {len(compressed)} bytes")

restored = deserialize_compressed(compressed, large_schema)
```

## Best Practices

1. **Always provide the schema**: Deserialization requires the type schema
2. **Use binary mode for files**: MessagePack is binary, use `'wb'` and `'rb'`
3. **Validate after deserialization**: Extra safety check
4. **Version your schemas**: Include version info if schemas might change
5. **Handle errors gracefully**: Network/disk operations can fail
6. **Test round-trips**: Ensure serialize → deserialize → serialize is stable

## Common Patterns

### Configuration Storage

```python
from pathlib import Path

class ConfigStore:
    """Store and load configuration with type safety."""

    def __init__(self, config_type, filepath):
        self.config_type = config_type
        self.filepath = Path(filepath)

    def save(self, config_value):
        """Save configuration to file."""
        msgpack_bytes = cty_to_msgpack(config_value, self.config_type)
        self.filepath.write_bytes(msgpack_bytes)

    def load(self):
        """Load configuration from file."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Config not found: {self.filepath}")

        msgpack_bytes = self.filepath.read_bytes()
        return cty_from_msgpack(msgpack_bytes, self.config_type)

# Usage
config_store = ConfigStore(config_type, "app.config")
config_store.save(config_value)
loaded_config = config_store.load()
```

### Caching

```python
from functools import lru_cache
import hashlib

def cache_key(value, schema):
    """Generate cache key from serialized value."""
    msgpack_bytes = cty_to_msgpack(value, schema)
    return hashlib.sha256(msgpack_bytes).hexdigest()

class CtyCache:
    """Cache cty values."""

    def __init__(self):
        self.cache = {}

    def set(self, key, value, schema):
        """Store value in cache."""
        msgpack_bytes = cty_to_msgpack(value, schema)
        self.cache[key] = msgpack_bytes

    def get(self, key, schema):
        """Retrieve value from cache."""
        if key not in self.cache:
            return None
        msgpack_bytes = self.cache[key]
        return cty_from_msgpack(msgpack_bytes, schema)
```

## Next Steps

- [Validate complex data](validate-data.md)
- [Work with Terraform types](work-with-terraform.md)
- [Learn about path navigation](../user-guide/advanced/path-navigation.md)
