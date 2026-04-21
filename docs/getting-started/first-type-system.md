# Your First Type System

Now that you've seen the basics, let's dive deeper into understanding how pyvider.cty's type system works.

## Core Concepts

Before building more complex types, let's understand the main components:

### Types

A **Type** defines the shape and constraints of your data. Types in pyvider.cty include:

- **Primitives**: `CtyString`, `CtyNumber`, `CtyBool`
- **Collections**: `CtyList`, `CtyMap`, `CtySet`
- **Structural**: `CtyObject`, `CtyTuple`
- **Special**: `CtyDynamic` (runtime type determination)

### Values

A **Value** is an instance of a type. Values are:

- **Immutable** - Once created, they cannot be changed
- **Type-safe** - They always conform to their type schema
- **Rich** - They carry metadata like marks and null status

### Validation

**Validation** is the process of checking if raw Python data conforms to a type. If valid, you get a `CtyValue`. If not, you get a clear error.

### Conversion

**Conversion** transforms between cty values and raw Python values, or between different cty types.

## Building a More Complex Type

Let's build a type for a blog post system:

```python
from pyvider.cty import (
    CtyObject, CtyString, CtyNumber, CtyList, CtyBool
)

# Define a comment type
comment_type = CtyObject(
    attribute_types={
        "author": CtyString(),
        "text": CtyString(),
        "likes": CtyNumber()
    }
)

# Define a blog post type
post_type = CtyObject(
    attribute_types={
        "title": CtyString(),
        "content": CtyString(),
        "author": CtyString(),
        "published": CtyBool(),
        "comments": CtyList(element_type=comment_type),
        "tags": CtyList(element_type=CtyString())
    }
)
```

Notice how we can nest types - the `comments` field is a list of `comment_type` objects.

## Validating Complex Data

Now let's validate some data:

```python
post_data = {
    "title": "Getting Started with Pyvider CTY",
    "content": "This is a great library for type-safe data...",
    "author": "Alice",
    "published": True,
    "comments": [
        {
            "author": "Bob",
            "text": "Great post!",
            "likes": 5
        },
        {
            "author": "Charlie",
            "text": "Very helpful, thanks!",
            "likes": 3
        }
    ],
    "tags": ["python", "types", "tutorial"]
}

try:
    post_value = post_type.validate(post_data)
    print("✅ Post validated successfully!")
except Exception as e:
    print(f"❌ Validation failed: {e}")
```

## Optional Attributes

Sometimes you want fields to be optional:

```python
user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "email": CtyString(),
        "age": CtyNumber(),
        "bio": CtyString()
    },
    optional_attributes={"age", "bio"}
)

# This is valid - age and bio are optional
user_data = {
    "name": "Alice",
    "email": "alice@example.com"
}

user_value = user_type.validate(user_data)

# Optional attributes that weren't provided are null
print(f"Age is null: {user_value['age'].is_null}")  # True
print(f"Bio is null: {user_value['bio'].is_null}")  # True
```

## Accessing Nested Data

With nested structures, you can chain access:

```python
post_value = post_type.validate(post_data)

# Access nested data
first_comment = post_value['comments'][0]
print(f"First comment by: {first_comment['author'].raw_value}")
print(f"Comment text: {first_comment['text'].raw_value}")

# Iterate over comments
for i, comment in enumerate(post_value['comments']):
    author = comment['author'].raw_value
    text = comment['text'].raw_value
    likes = comment['likes'].raw_value
    print(f"Comment {i+1} by {author}: {text} ({likes} likes)")
```

## What About Invalid Data?

pyvider.cty provides clear error messages when validation fails:

```python
invalid_data = {
    "title": "My Post",
    "content": "Content here",
    "author": "Alice",
    "published": "yes",  # Should be boolean!
    "comments": [],
    "tags": []
}

try:
    post_value = post_type.validate(invalid_data)
except Exception as e:
    print(f"Error: {e}")
    # Output: Error: Attribute 'published': expected CtyBool, got str
```

## Next Steps

Now you understand the fundamentals! Continue learning:

- **[Explore Examples](examples.md)** - See more practical examples
- **[User Guide: Core Concepts](../user-guide/core-concepts/types.md)** - Deep dive into types
- **[User Guide: Type Reference](../user-guide/type-reference/primitives.md)** - Learn about all available types

---

**Key Concepts:**

- Types define data structure, values hold the actual data
- Values are immutable and type-safe
- Validation converts raw Python data to cty values
- Optional attributes can be marked when defining objects
- Nested structures are fully supported
- Error messages are clear and actionable
