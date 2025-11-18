# Validation

Validation is the process of checking whether raw Python data conforms to a defined type schema. In pyvider.cty, validation is the gateway between untrusted or untyped data and type-safe `CtyValue` objects.

## How Validation Works

Every `CtyType` provides a `validate()` method that:

1. **Accepts raw Python data** (dicts, lists, primitives, etc.)
2. **Checks conformance** against the type schema
3. **Returns a CtyValue** if valid
4. **Raises a CtyValidationError** if invalid

```python
from pyvider.cty import CtyString, CtyValidationError

string_type = CtyString()

# Valid: returns CtyValue
result = string_type.validate("hello")
print(result.raw_value)  # "hello"

# Invalid: raises CtyValidationError
try:
    string_type.validate(123)
except CtyValidationError as e:
    print(f"Error: {e}")  # Error: expected CtyString, got int
```

## Validation vs Direct Construction

You should always prefer `validate()` over direct `CtyValue` construction:

```python
# ✅ RECOMMENDED: Use validate()
value = CtyString().validate("hello")

# ❌ AVOID: Direct construction (internal API)
# from pyvider.cty.values import CtyValue
# value = CtyValue(...)  # Don't do this!
```

The `validate()` method provides:
- Type checking and coercion
- Clear error messages
- Consistent behavior across all types
- Protection against malformed data

## Validation Rules by Type

### Primitives

**CtyString**
- Accepts: `str` values
- Rejects: Non-string types
- Special handling: Unicode normalization (NFC)

**CtyNumber**
- Accepts: `int`, `float`, `Decimal`
- Rejects: Non-numeric types
- Special handling: Preserves precision with `Decimal`

**CtyBool**
- Accepts: `bool` values (`True`, `False`)
- Rejects: Non-boolean types (including truthy/falsy values like `1`, `0`, `""`)

### Collections

**CtyList**
- Accepts: `list` or other iterables
- Element validation: Each element must match `element_type`
- Preserves: Order

**CtySet**
- Accepts: `set`, `frozenset`, or iterables
- Element validation: Each element must match `element_type`
- Removes: Duplicates (enforces set semantics)

**CtyMap**
- Accepts: `dict` with string keys
- Element validation: All values must match `element_type`
- Key requirement: Keys must be strings

### Structural Types

**CtyObject**
- Accepts: `dict` with specific attributes
- Attribute validation: Each attribute validated against its type
- Optional attributes: Missing optional attributes become null values
- Required attributes: Must be present (unless optional)

**CtyTuple**
- Accepts: `list`, `tuple`, or iterables
- Element validation: Each position validated against its element type
- Length requirement: Must match declared element count

## Recursive Validation

Validation works recursively through nested structures:

```python
from pyvider.cty import CtyObject, CtyList, CtyString, CtyNumber

# Nested schema
company_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "employees": CtyList(
            element_type=CtyObject(
                attribute_types={
                    "name": CtyString(),
                    "salary": CtyNumber()
                }
            )
        )
    }
)

# Validation descends through the structure
company_data = {
    "name": "Acme Corp",
    "employees": [
        {"name": "Alice", "salary": 100000},
        {"name": "Bob", "salary": 95000}
    ]
}

company = company_type.validate(company_data)
# If Bob's salary was "95000" (string), validation would fail
# at the path: employees[1].salary
```

## Validation Context and Depth Limits

pyvider.cty tracks validation depth to prevent infinite recursion:

```python
from pyvider.cty.context import deeper_validation, MAX_VALIDATION_DEPTH

# Context tracks current validation depth
with deeper_validation():
    # Validation depth increased by 1
    pass

# Maximum depth: 500 (configurable via MAX_VALIDATION_DEPTH)
```

This protection prevents stack overflow with:
- Circular references (if raw data contains them)
- Extremely deep nesting
- Malicious input designed to cause resource exhaustion

## Error Handling

Validation errors provide detailed context:

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber
from pyvider.cty.exceptions import CtyAttributeValidationError

user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    }
)

try:
    user_type.validate({
        "name": "Alice",
        "age": "thirty"  # Wrong type!
    })
except CtyAttributeValidationError as e:
    print(e.attribute_name)  # "age"
    print(e.path)            # Path to error location
    print(e)                 # Full error message
```

### Exception Hierarchy

```
CtyValidationError (base)
├── CtyTypeMismatchError
├── CtyAttributeValidationError
├── CtyListValidationError
├── CtyMapValidationError
├── CtySetValidationError
└── CtyTupleValidationError
```

Catch specific exceptions for targeted error handling:

```python
try:
    value = schema.validate(data)
except CtyAttributeValidationError as e:
    # Handle object attribute errors
    log.error(f"Attribute {e.attribute_name} is invalid")
except CtyListValidationError as e:
    # Handle list validation errors
    log.error(f"List validation failed at index {e.index}")
except CtyValidationError as e:
    # Catch-all for other validation errors
    log.error(f"Validation failed: {e}")
```

## Validation Best Practices

### 1. Validate at System Boundaries

Always validate data when it enters your system:

```python
def handle_api_request(request_data):
    """Validate incoming API data."""
    try:
        validated = request_schema.validate(request_data)
        return process_request(validated)
    except CtyValidationError as e:
        return {"error": str(e)}, 400
```

### 2. Use Specific Error Handling

Catch specific validation errors for better error messages:

```python
try:
    config = config_schema.validate(raw_config)
except CtyAttributeValidationError as e:
    print(f"Invalid configuration: {e.attribute_name} is incorrect")
except CtyValidationError as e:
    print(f"Configuration validation failed: {e}")
```

### 3. Build Schemas Incrementally

Define sub-schemas and compose them:

```python
# Define reusable schemas
address_type = CtyObject(
    attribute_types={
        "street": CtyString(),
        "city": CtyString(),
        "zip": CtyString()
    }
)

# Compose into larger schemas
person_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "address": address_type  # Reuse
    }
)
```

### 4. Document Optional Fields

Make it clear which fields are optional:

```python
# Clear documentation of optional fields
user_type = CtyObject(
    attribute_types={
        "username": CtyString(),  # Required
        "email": CtyString(),      # Required
        "phone": CtyString(),      # Optional
        "bio": CtyString()         # Optional
    },
    optional_attributes={"phone", "bio"}
)
```

### 5. Test Edge Cases

Test validation with edge cases:

```python
def test_user_validation():
    """Test user validation with various inputs."""
    # Test valid data
    valid_user = user_type.validate({"username": "alice", "email": "a@ex.com"})
    assert valid_user is not None

    # Test missing required field
    with pytest.raises(CtyValidationError):
        user_type.validate({"username": "bob"})  # Missing email

    # Test wrong type
    with pytest.raises(CtyValidationError):
        user_type.validate({"username": 123, "email": "a@ex.com"})
```

## Performance Considerations

Validation has computational cost:

1. **Type checking** - Every value is type-checked
2. **Recursion** - Nested structures validated recursively
3. **Immutable construction** - Creates new immutable values

For performance-critical paths:

```python
# Validate once at the boundary
config = config_schema.validate(raw_config)

# Reuse the validated value
for _ in range(1000):
    # Don't validate again inside the loop
    process(config)
```

## Integration with Type Conversion

Validation and type conversion work together:

```python
from pyvider.cty import convert, CtyString, CtyNumber

# Validation: Strict type checking
number_type = CtyNumber()
number_type.validate("123")  # ❌ Raises error: expected number, got str

# Conversion: Flexible type transformation
string_val = CtyString().validate("123")
number_val = convert(string_val, CtyNumber())  # ✅ Converts "123" to 123
```

## See Also

- **[Type Conversion](../../api/conversion.md)** - Converting between types
- **[How-To: Validate Data](../../how-to/validate-data.md)** - Practical validation patterns
- **[Error Handling](../../reference/troubleshooting.md)** - Handling validation errors
