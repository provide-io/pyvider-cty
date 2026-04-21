# How to Validate Complex Data Structures

This guide shows you how to validate complex, nested data structures with pyvider.cty.

## Basic Validation Pattern

The fundamental pattern for validation is:

1. Define a type schema
2. Call `.validate()` with raw Python data
3. Handle validation errors
4. Work with the validated `CtyValue`

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber

# 1. Define schema
user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    }
)

# 2. Validate
try:
    user_value = user_type.validate({"name": "Alice", "age": 30})
    # 3. Success - work with the value
    print(f"Valid user: {user_value['name'].raw_value}")
except Exception as e:
    # 3. Handle errors
    print(f"Validation failed: {e}")
```

## Validating Nested Structures

For complex nested data, build your schema from the inside out:

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyList, CtyBool

# Define nested types
address_type = CtyObject(
    attribute_types={
        "street": CtyString(),
        "city": CtyString(),
        "zip": CtyString()
    }
)

contact_type = CtyObject(
    attribute_types={
        "email": CtyString(),
        "phone": CtyString()
    }
)

# Use nested types in main schema
person_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "address": address_type,
        "contact": contact_type,
        "active": CtyBool()
    }
)

# Validate nested data
person_data = {
    "name": "Bob",
    "age": 25,
    "address": {
        "street": "123 Main St",
        "city": "Boston",
        "zip": "02101"
    },
    "contact": {
        "email": "bob@example.com",
        "phone": "555-0100"
    },
    "active": True
}

person_value = person_type.validate(person_data)
```

## Optional Fields

Mark fields as optional when they may be missing:

```python
user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "email": CtyString(),
        "phone": CtyString(),
        "bio": CtyString()
    },
    optional_attributes={"phone", "bio"}  # These can be omitted
)

# Valid: missing optional fields
minimal_user = user_type.validate({
    "name": "Alice",
    "email": "alice@example.com"
})

# Optional fields are null
print(minimal_user['phone'].is_null)  # True
print(minimal_user['bio'].is_null)    # True
```

## Validating Collections

### Lists with Consistent Types

```python
from pyvider.cty import CtyList, CtyString

# All elements must be strings
tags_type = CtyList(element_type=CtyString())

tags_value = tags_type.validate(["python", "types", "validation"])

# Access elements
for tag in tags_value:
    print(tag.raw_value)
```

### Lists of Objects

```python
# List of user objects
users_type = CtyList(
    element_type=CtyObject(
        attribute_types={
            "name": CtyString(),
            "email": CtyString()
        }
    )
)

users_data = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"}
]

users_value = users_type.validate(users_data)

# Access nested data
for user in users_value:
    print(f"{user['name'].raw_value}: {user['email'].raw_value}")
```

### Maps

```python
from pyvider.cty import CtyMap, CtyNumber

# Map of string keys to number values
scores_type = CtyMap(element_type=CtyNumber())

scores_value = scores_type.validate({
    "alice": 95,
    "bob": 87,
    "charlie": 92
})

# Access map values
print(scores_value["alice"].raw_value)  # 95
```

## Handling Validation Errors

Validation errors provide detailed information about what went wrong:

```python
from pyvider.cty.exceptions import CtyValidationError

try:
    user_value = user_type.validate({
        "name": "Alice",
        "age": "thirty"  # Wrong type!
    })
except CtyValidationError as e:
    print(f"Validation error: {e}")
    # Output: Attribute 'age': expected CtyNumber, got str
```

### Validate Multiple Items

```python
def validate_many(data_list, schema):
    """Validate multiple items and collect errors."""
    results = []
    errors = []

    for i, data in enumerate(data_list):
        try:
            value = schema.validate(data)
            results.append(value)
        except CtyValidationError as e:
            errors.append((i, str(e)))

    return results, errors

# Use it
users_data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": "invalid"},  # Error
    {"name": "Charlie", "age": 25}
]

valid_users, validation_errors = validate_many(users_data, user_type)

print(f"Valid: {len(valid_users)}, Errors: {len(validation_errors)}")
for index, error in validation_errors:
    print(f"Item {index}: {error}")
```

## Dynamic Validation

Use `CtyDynamic` when you don't know the type ahead of time:

```python
from pyvider.cty import CtyDynamic, CtyObject

flexible_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "data": CtyDynamic()  # Can be any type
    }
})

# The 'data' field can hold any type
example1 = flexible_type.validate({
    "name": "Example 1",
    "data": "some text"
})

example2 = flexible_type.validate({
    "name": "Example 2",
    "data": {"nested": "object"}
})

example3 = flexible_type.validate({
    "name": "Example 3",
    "data": [1, 2, 3]
})
```

## Validating Against Multiple Schemas

Sometimes you need to try different schemas:

```python
def try_validate(data, schemas):
    """Try validating against multiple schemas."""
    for i, schema in enumerate(schemas):
        try:
            return schema.validate(data)
        except CtyValidationError:
            continue
    raise ValueError("Data doesn't match any schema")

# Define alternative schemas
schema_v1 = CtyObject(
    attribute_types={"name": CtyString(), "value": CtyNumber()}
)
schema_v2 = CtyObject(
    attribute_types={"name": CtyString(), "count": CtyNumber()}
)

schemas = [schema_v1, schema_v2]

# Try validation
data = {"name": "Test", "count": 42}
result = try_validate(data, schemas)  # Matches schema_v2
```

## Best Practices

1. **Build schemas incrementally**: Start with simple types and compose them
2. **Use descriptive variable names**: `user_type`, `address_type` are clear
3. **Validate early**: Validate at system boundaries (API inputs, file loads)
4. **Handle errors gracefully**: Provide clear error messages to users
5. **Reuse schemas**: Define common schemas once and import them
6. **Document optional fields**: Make it clear which fields can be omitted

## Common Patterns

### Configuration Validation

```python
config_type = CtyObject(
    attribute_types={
        "api_key": CtyString(),
        "api_url": CtyString(),
        "timeout": CtyNumber(),
        "retries": CtyNumber(),
        "debug": CtyBool()
    },
    optional_attributes={"timeout", "retries", "debug"}
)

def load_config(config_dict):
    """Load and validate configuration."""
    try:
        return config_type.validate(config_dict)
    except CtyValidationError as e:
        raise ValueError(f"Invalid configuration: {e}")
```

### API Response Validation

```python
api_response_type = CtyObject(
    attribute_types={
        "status": CtyString(),
        "data": CtyDynamic(),
        "error": CtyString()
    },
    optional_attributes={"error"}
)

def validate_api_response(response_data):
    """Validate API response structure."""
    response = api_response_type.validate(response_data)

    if response['status'].raw_value == "error":
        error_msg = response['error'].raw_value
        raise Exception(f"API error: {error_msg}")

    return response['data']
```

## Next Steps

- [Serialize validated data](serialize-values.md)
- [Work with Terraform types](work-with-terraform.md)
- [Learn about custom types](create-custom-types.md)
