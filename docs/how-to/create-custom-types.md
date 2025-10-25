# How to Create Custom Types

This guide shows advanced techniques for creating custom types and extending pyvider.cty's type system.

## When to Create Custom Types

Consider custom types when you need:
- Domain-specific validation logic
- Reusable type compositions
- Complex validation rules
- Custom serialization behavior

## Type Composition

The simplest way to create "custom" types is through composition:

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyBool, CtyList

# Create reusable composite types
def EmailType():
    """String type for email addresses."""
    return CtyString()  # In practice, add validation

def URLType():
    """String type for URLs."""
    return CtyString()

def PositiveNumberType():
    """Number type for positive values."""
    return CtyNumber()  # In practice, add validation

# Use them in schemas
user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "email": EmailType(),
        "website": URLType(),
        "age": PositiveNumberType()
    }
)
```

## Factory Functions

Create factory functions for common type patterns:

```python
def TimestampType():
    """ISO 8601 timestamp as string."""
    return CtyString()

def IDType():
    """Unique identifier as string."""
    return CtyString()

def EnumType(*allowed_values):
    """Constrained string enum."""
    # Note: Real implementation would validate against allowed_values
    return CtyString()

# Usage
resource_type = CtyObject(
    attribute_types={
        "id": IDType(),
        "status": EnumType("active", "inactive", "pending"),
        "created_at": TimestampType()
    }
)
```

## Validation Wrappers

Wrap types with additional validation:

```python
from pyvider.cty import CtyString, CtyNumber
from pyvider.cty.exceptions import CtyValidationError
import re

class EmailString:
    """Email validated string type."""

    def __init__(self):
        self.base_type = CtyString()

    def validate(self, value):
        # First validate as string
        cty_value = self.base_type.validate(value)

        # Then check email format
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, cty_value.raw_value):
            raise CtyValidationError(f"Invalid email format: {value}")

        return cty_value

# Usage
email_type = EmailString()
valid_email = email_type.validate("user@example.com")
```

## Range-Constrained Numbers

```python
class RangeNumber:
    """Number type with min/max constraints."""

    def __init__(self, min_value=None, max_value=None):
        self.base_type = CtyNumber()
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value):
        cty_value = self.base_type.validate(value)
        num = float(cty_value.raw_value)

        if self.min_value is not None and num < self.min_value:
            raise CtyValidationError(
                f"Value {num} is less than minimum {self.min_value}"
            )

        if self.max_value is not None and num > self.max_value:
            raise CtyValidationError(
                f"Value {num} is greater than maximum {self.max_value}"
            )

        return cty_value

# Usage
age_type = RangeNumber(min_value=0, max_value=150)
port_type = RangeNumber(min_value=1, max_value=65535)

person = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": age_type
    }
)
```

## Pattern-Validated Strings

```python
class PatternString:
    """String type with regex pattern validation."""

    def __init__(self, pattern, error_message=None):
        self.base_type = CtyString()
        self.pattern = re.compile(pattern)
        self.error_message = error_message or f"Must match pattern: {pattern}"

    def validate(self, value):
        cty_value = self.base_type.validate(value)

        if not self.pattern.match(cty_value.raw_value):
            raise CtyValidationError(self.error_message)

        return cty_value

# Usage
phone_type = PatternString(
    r'^\+?1?\d{10,14}$',
    "Must be a valid phone number"
)

zip_code_type = PatternString(
    r'^\d{5}(-\d{4})?$',
    "Must be a valid US ZIP code"
)

contact = CtyObject(
    attribute_types={
        "phone": phone_type,
        "zip": zip_code_type
    }
)
```

## Length-Constrained Collections

```python
from pyvider.cty import CtyList

class SizedList:
    """List type with size constraints."""

    def __init__(self, element_type, min_length=None, max_length=None):
        self.base_type = CtyList(element_type=element_type)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        cty_value = self.base_type.validate(value)

        length = len(value)

        if self.min_length is not None and length < self.min_length:
            raise CtyValidationError(
                f"List length {length} is less than minimum {self.min_length}"
            )

        if self.max_length is not None and length > self.max_length:
            raise CtyValidationError(
                f"List length {length} is greater than maximum {self.max_length}"
            )

        return cty_value

# Usage
tags_type = SizedList(CtyString(), min_length=1, max_length=10)
```

## Conditional Validation

```python
class ConditionalObject:
    """Object type with conditional field requirements."""

    def __init__(self, base_schema, conditionals):
        self.base_schema = base_schema
        self.conditionals = conditionals

    def validate(self, value):
        # First validate against base schema
        cty_value = self.base_schema.validate(value)

        # Then check conditional rules
        for condition, required_fields in self.conditionals:
            if condition(value):
                for field in required_fields:
                    if field not in value or value[field] is None:
                        raise CtyValidationError(
                            f"Field '{field}' is required when condition is met"
                        )

        return cty_value

# Usage
payment_schema = CtyObject(
    attribute_types={
        "method": CtyString(),
        "credit_card": CtyString(),
        "bank_account": CtyString()
    },
    optional_attributes={"credit_card", "bank_account"}
)

conditionals = [
    (lambda v: v["method"] == "card", ["credit_card"]),
    (lambda v: v["method"] == "bank", ["bank_account"])
]

payment_type = ConditionalObject(payment_schema, conditionals)
```

## Type Registries

Organize custom types in registries:

```python
class TypeRegistry:
    """Registry for custom types."""

    def __init__(self):
        self.types = {}

    def register(self, name, type_factory):
        """Register a type factory."""
        self.types[name] = type_factory

    def get(self, name):
        """Get a registered type."""
        if name not in self.types:
            raise ValueError(f"Unknown type: {name}")
        return self.types[name]()

    def create_object(self, schema_dict):
        """Create object from schema dictionary."""
        attribute_types = {}
        for attr, type_name in schema_dict.items():
            attribute_types[attr] = self.get(type_name)

        return CtyObject(attribute_types)

# Usage
registry = TypeRegistry()
registry.register("email", EmailString)
registry.register("age", lambda: RangeNumber(0, 150))
registry.register("phone", lambda: PatternString(r'^\+?1?\d{10,14}$'))

# Create types from registry
user_schema = registry.create_object({
    "name": "string",
    "email": "email",
    "age": "age"
})
```

## Best Practices

1. **Compose before creating**: Use existing types when possible
2. **Validate incrementally**: Build on base type validation
3. **Provide clear errors**: Make validation failures informative
4. **Document constraints**: Clearly document what your types enforce
5. **Test thoroughly**: Custom types need comprehensive tests
6. **Consider reusability**: Design for use across your codebase

## Common Patterns

### Domain-Specific Types

```python
# Application-specific types
class UserIDType:
    """User ID with format validation."""
    def __init__(self):
        self.base_type = PatternString(r'^user_[a-f0-9]{16}$')

    def validate(self, value):
        return self.base_type.validate(value)

class ResourceARNType:
    """AWS ARN type."""
    def __init__(self):
        self.base_type = PatternString(r'^arn:aws:[a-z0-9-]+:[a-z0-9-]*:\d+:.+$')

    def validate(self, value):
        return self.base_type.validate(value)
```

### Versioned Schemas

```python
def UserSchemaV1():
    """User schema version 1."""
    return CtyObject(
        attribute_types={
            "name": CtyString(),
            "email": EmailString()
        }
    )

def UserSchemaV2():
    """User schema version 2 with additional fields."""
    return CtyObject(
        attribute_types={
            "name": CtyString(),
            "email": EmailString(),
            "phone": PatternString(r'^\+?1?\d{10,14}$'),
            "created_at": TimestampType()
        }
    )

# Select schema based on version
def get_user_schema(version):
    schemas = {
        1: UserSchemaV1,
        2: UserSchemaV2
    }
    return schemas[version]()
```

## Next Steps

- [Validate complex data](validate-data.md)
- [Work with Terraform types](work-with-terraform.md)
- [Learn about capsule types](../user-guide/type-reference/capsule.md)
