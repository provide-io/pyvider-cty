# Quick Start (5 Minutes)

This quick start guide will have you working with pyvider.cty in just 5 minutes. You'll learn the fundamental pattern: **Define → Validate → Access → Serialize**.

## Your First Type-Safe Data Structure

Let's build a simple user profile system with type validation.

### 1. Import Required Types

```python
from pyvider.cty import CtyString, CtyNumber, CtyBool, CtyList, CtyObject
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack
```

### 2. Define a Type Schema

Define what a valid user profile looks like:

```python
person_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool(),
        "tags": CtyList(element_type=CtyString()),
    }
)
```

This schema says: "A person must have a name (string), age (number), active status (boolean), and a list of tags (strings)."

### 3. Validate Data

Now validate some raw Python data against this schema:

```python
# Create a raw Python dictionary
user_data = {
    "name": "Alice",
    "age": 30,
    "active": True,
    "tags": ["developer", "python"]
}

# Validate the data
try:
    person_value = person_type.validate(user_data)
    print("✅ Validation successful!")
except Exception as e:
    print(f"❌ Validation failed: {e}")
```

If the data doesn't match the schema, you'll get a clear error message explaining what's wrong.

### 4. Access Data

Once validated, you have an immutable `CtyValue` with type-safe access:

```python
# Access attributes (returns CtyValue objects)
print(f"Name: {person_value['name'].raw_value}")  # Output: Alice
print(f"Age: {person_value['age'].raw_value}")    # Output: 30

# Iterate over the list
print("Tags:")
for tag_value in person_value['tags']:
    print(f"  - {tag_value.raw_value}")
```

**Key Point**: When you access attributes or elements, you get back `CtyValue` objects. Use `.raw_value` to get the underlying Python value.

### 5. Serialize to MessagePack

Serialize the value for storage or transmission:

```python
# Serialize to MessagePack binary format
msgpack_bytes = cty_to_msgpack(person_value, person_type)
print(f"\nSerialized to {len(msgpack_bytes)} bytes")
```

MessagePack is a binary format that's compact and compatible with go-cty for cross-language interoperability.

### 6. Deserialize from MessagePack

Reconstruct the value from MessagePack:

```python
# Deserialize from MessagePack
reconstructed_value = cty_from_msgpack(msgpack_bytes, person_type)
assert reconstructed_value['name'].raw_value == "Alice"
print("✅ Successfully reconstructed value!")
```

## Complete Example

Here's the complete working example:

```python
from pyvider.cty import CtyString, CtyNumber, CtyBool, CtyList, CtyObject
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

# 1. Define schema
person_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool(),
        "tags": CtyList(element_type=CtyString()),
    }
)

# 2. Validate data
user_data = {
    "name": "Alice",
    "age": 30,
    "active": True,
    "tags": ["developer", "python"]
}

person_value = person_type.validate(user_data)

# 3. Access data
print(f"Name: {person_value['name'].raw_value}")

# 4. Serialize
msgpack_bytes = cty_to_msgpack(person_value, person_type)

# 5. Deserialize
reconstructed = cty_from_msgpack(msgpack_bytes, person_type)
assert reconstructed['name'].raw_value == "Alice"
print("✅ All done!")
```

## Try It Yourself

You can run this example from the repository:

```bash
python examples/getting-started/quick-start.py
```

## What's Next?

You've learned the core workflow! Now you can:

- **[Learn more about types and values](first-type-system.md)** - Understand the fundamentals
- **[Explore more examples](examples.md)** - See pyvider.cty in action
- **[Dive into the User Guide](../user-guide/index.md)** - Learn about all features

---

**Key Takeaways:**

- Define schemas with `CtyType` objects (like `CtyString()`, `CtyObject()`)
- Validate data with `.validate()` - returns immutable `CtyValue`
- Access data with `[]` notation - returns `CtyValue`, use `.raw_value` for Python values
- Serialize with `cty_to_msgpack()` and deserialize with `cty_from_msgpack()`
