# Troubleshooting

This guide helps you diagnose and resolve common issues when using `pyvider.cty`.

---

## Quick Lookup Index

**Errors:**
- [CtyValidationError](#ctyvalidationerror) - Data doesn't match schema
- [CtyAttributeValidationError](#ctyattributevalidationerror) - Object attribute validation failed
- [CtyListValidationError](#ctylistvalidationerror) - List validation failed
- [CtyMapValidationError](#ctymapvalidationerror) - Map validation failed
- [CtySetValidationError](#ctysetvalidationerror) - Set validation failed
- [CtyTupleValidationError](#ctytuplevalidationerror) - Tuple validation failed
- [CtyTypeMismatchError](#ctytypemismatcherror) - Wrong data type
- [CtyConversionError](#ctyconversionerror) - Type conversion failed
- [CtyTypeParseError](#ctytypeparseerror) - Type string parsing failed
- [SerializationError](#serializationerror) - MessagePack serialization failed
- [DeserializationError](#deserializationerror) - MessagePack deserialization failed
- [CtyFunctionError](#ctyfunctionerror) - Built-in function error

**Common Scenarios:**
- [Missing Required Attributes](#scenario-1-missing-required-attributes)
- [Type Conversion Issues](#scenario-2-type-conversion-issues)
- [Null vs Missing Attributes](#scenario-3-null-vs-missing-attributes)
- [Accessing Null Values](#scenario-4-accessing-null-values)
- [Recursion Depth Exceeded](#scenario-5-recursion-depth-exceeded)

**Resources:**
- [Debugging Tips](#debugging-tips)
- [Performance Troubleshooting](#performance-troubleshooting)
- [Getting Help](#getting-help)

---

## Exception Hierarchy

Understanding the exception hierarchy helps you catch and handle errors appropriately:

```
CtyError (base exception)
│
├── CtyValidationError
│   ├── CtyTypeMismatchError
│   ├── CtyTypeValidationError
│   ├── CtyAttributeValidationError
│   ├── CtyListValidationError
│   ├── CtyMapValidationError
│   ├── CtySetValidationError
│   ├── CtyTupleValidationError
│   ├── CtyStringValidationError
│   ├── CtyNumberValidationError
│   ├── CtyBoolValidationError
│   └── CtyCollectionValidationError
│
├── CtyConversionError
│   ├── CtyTypeConversionError
│   └── CtyTypeParseError
│
├── CtyFunctionError
│
└── EncodingError
    ├── SerializationError
    │   ├── JsonEncodingError
    │   └── MsgPackEncodingError
    ├── DeserializationError
    ├── WireFormatError
    ├── DynamicValueError
    ├── InvalidTypeError
    ├── AttributePathError
    └── TransformationError
```

**Import Path:** All exceptions can be imported from `pyvider.cty.exceptions`

```python
from pyvider.cty.exceptions import (
    CtyValidationError,
    CtyConversionError,
    SerializationError,
    # ... and others
)
```

**Catching Exceptions:**

```python
from pyvider.cty.exceptions import CtyValidationError, CtyTypeMismatchError

try:
    value = schema.validate(data)
except CtyTypeMismatchError as e:
    # Handle specific type mismatch
    print(f"Type mismatch: {e}")
except CtyValidationError as e:
    # Handle all other validation errors
    print(f"Validation error: {e}")
```

---

## Exception Reference

### Validation Errors

#### `CtyValidationError`

**Description**: Base exception raised when data doesn't conform to a type schema.

**Common Causes**:
- Wrong data type (e.g., string instead of number)
- Missing required attributes in objects
- Invalid collection elements
- Data structure doesn't match schema

**Example**:
```python
from pyvider.cty import CtyObject, CtyString, CtyNumber

user_type = CtyObject(
    attribute_types={"name": CtyString(), "age": CtyNumber()}
)

# This will raise CtyValidationError - missing 'age' attribute
try:
    user = user_type.validate({"name": "Alice"})
except CtyValidationError as e:
    print(f"Validation failed: {e}")
    # Error message will indicate which attribute is missing
```

**How to Fix**:
- Read the error message carefully - it includes the path to the invalid field
- Verify your data structure matches the schema exactly
- Check for typos in attribute names
- Ensure all required fields are present

---

#### `CtyAttributeValidationError`

**Description**: Raised when an object attribute fails validation.

**Common Causes**:
- Missing required attributes
- Extra attributes not defined in schema
- Attribute value doesn't match its type

**Example**:
```python
from pyvider.cty import CtyObject, CtyString

person_type = CtyObject(attribute_types={"name": CtyString()})

# This will raise CtyAttributeValidationError - 'age' not in schema
try:
    person = person_type.validate({"name": "Bob", "age": 30})
except CtyAttributeValidationError as e:
    print(f"Attribute error: {e}")
```

**How to Fix**:
- Use `optional_attributes` parameter for optional fields
- Remove extra attributes from data or add them to the schema
- Verify attribute types match the schema

---

#### `CtyListValidationError`

**Description**: Raised when list validation fails.

**Common Causes**:
- Element doesn't match the list's element type
- Non-list value passed to list type
- Heterogeneous elements in a homogeneous list

**Example**:
```python
from pyvider.cty import CtyList, CtyString

tags_type = CtyList(element_type=CtyString())

# This will raise CtyListValidationError - contains number
try:
    tags = tags_type.validate(["tag1", "tag2", 123])
except CtyListValidationError as e:
    print(f"List validation failed: {e}")
```

**How to Fix**:
- Ensure all elements match the declared element type
- Check for type mismatches in the list
- Use `CtyDynamic` if you need heterogeneous lists

---

#### `CtyMapValidationError`

**Description**: Raised when map validation fails.

**Common Causes**:
- Value doesn't match the map's element type
- Non-string keys
- Non-dict value passed to map type

**Example**:
```python
from pyvider.cty import CtyMap, CtyNumber

config_type = CtyMap(element_type=CtyNumber())

# This will raise CtyMapValidationError - "three" is not a number
try:
    config = config_type.validate({"one": 1, "two": 2, "three": "3"})
except CtyMapValidationError as e:
    print(f"Map validation failed: {e}")
```

**How to Fix**:
- Ensure all values match the declared element type
- Verify all keys are strings
- Check the data structure is a dictionary

---

#### `CtySetValidationError`

**Description**: Raised when set validation fails.

**Common Causes**:
- Element doesn't match the set's element type
- Duplicate elements in input
- Unhashable elements

**Example**:
```python
from pyvider.cty import CtySet, CtyString

unique_tags_type = CtySet(element_type=CtyString())

# This will raise CtySetValidationError - contains number
try:
    tags = unique_tags_type.validate({"tag1", "tag2", 123})
except CtySetValidationError as e:
    print(f"Set validation failed: {e}")
```

**How to Fix**:
- Ensure all elements match the declared element type
- Remove duplicates if present
- Verify elements are hashable

---

#### `CtyTupleValidationError`

**Description**: Raised when tuple validation fails.

**Common Causes**:
- Wrong number of elements
- Element at specific position doesn't match expected type
- Non-sequence value passed to tuple type

**Example**:
```python
from pyvider.cty import CtyTuple, CtyString, CtyNumber

point_type = CtyTuple(element_types=[CtyString(), CtyNumber(), CtyNumber()])

# This will raise CtyTupleValidationError - wrong number of elements
try:
    point = point_type.validate(["origin", 0])  # Missing third element
except CtyTupleValidationError as e:
    print(f"Tuple validation failed: {e}")
```

**How to Fix**:
- Ensure exactly the right number of elements
- Verify each element matches its positional type
- Check element order matches the schema

---

#### `CtyTypeMismatchError`

**Description**: Raised when value type doesn't match expected type.

**Common Causes**:
- Passing completely wrong type (e.g., dict instead of list)
- Type confusion in nested structures

**Example**:
```python
from pyvider.cty import CtyString

string_type = CtyString()

# This will raise CtyTypeMismatchError
try:
    value = string_type.validate(123)  # Number instead of string
except CtyTypeMismatchError as e:
    print(f"Type mismatch: {e}")
```

**How to Fix**:
- Verify the data type matches the schema
- Check for type confusion (list vs dict, string vs number)
- Use type conversion if appropriate

---

### Conversion Errors

#### `CtyConversionError`

**Description**: Base exception for type conversion failures.

**Common Causes**:
- Attempting to convert between incompatible types
- Invalid string format when converting to number
- Conversion would lose data or precision

**Example**:
```python
from pyvider.cty import CtyString, CtyNumber, convert

string_val = CtyString().validate("not-a-number")

# This will raise CtyConversionError
try:
    number_val = convert(string_val, CtyNumber())
except CtyConversionError as e:
    print(f"Conversion failed: {e}")
```

**How to Fix**:
- Check if the conversion is logically valid
- Verify string format when converting to numbers
- Use validation instead of conversion when appropriate
- Consider using `CtyDynamic` for unknown types

---

#### `CtyTypeParseError`

**Description**: Raised when parsing a type string fails.

**Common Causes**:
- Invalid Terraform type string syntax
- Unsupported type in string
- Malformed type expression

**Example**:
```python
from pyvider.cty import parse_tf_type_to_ctytype

# This will raise CtyTypeParseError - invalid syntax
try:
    parsed_type = parse_tf_type_to_ctytype("invalid[type{syntax")
except CtyTypeParseError as e:
    print(f"Parse error: {e}")
```

**How to Fix**:
- Verify the type string syntax is correct
- Check for matching brackets and braces
- Refer to Terraform type syntax documentation
- Use explicit type construction instead of parsing

---

### Serialization Errors

#### `SerializationError`

**Description**: Raised when serializing a value to MessagePack fails.

**Common Causes**:
- Unsupported data type in value
- Circular references
- Capsule types without proper serialization support

**Example**:
```python
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.exceptions import SerializationError

schema = CtyObject(attribute_types={"key": CtyString()})
value = schema.validate({"key": "value"})

# Normally this works, but can fail with incompatible data
try:
    msgpack_bytes = cty_to_msgpack(value, schema)
except SerializationError as e:
    print(f"Serialization failed: {e}")
```

**How to Fix**:
- Ensure all data types are serializable
- Check for circular references in capsule types
- Verify capsule types implement proper serialization

---

#### `DeserializationError`

**Description**: Raised when deserializing MessagePack data fails.

**Common Causes**:
- Corrupted MessagePack data
- Schema mismatch between serialization and deserialization
- Invalid MessagePack format

**Example**:
```python
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.exceptions import DeserializationError

schema = CtyObject(attribute_types={"key": CtyString()})

# This will raise DeserializationError - invalid data
try:
    value = cty_from_msgpack(b"invalid msgpack data", schema)
except DeserializationError as e:
    print(f"Deserialization failed: {e}")
```

**How to Fix**:
- Verify the MessagePack data is not corrupted
- Ensure the same schema is used for serialization and deserialization
- Check data was actually serialized with cty_to_msgpack

---

### Function Errors

#### `CtyFunctionError`

**Description**: Raised when a built-in function fails.

**Common Causes**:
- Invalid arguments to function
- Null or unknown values where concrete values expected
- Type mismatch in function parameters

**Example**:
```python
from pyvider.cty import CtyString
from pyvider.cty.functions import upper
from pyvider.cty.exceptions import CtyFunctionError

# This will raise CtyFunctionError - null value
try:
    null_val = CtyString().validate(None)
    result = upper(null_val)
except CtyFunctionError as e:
    print(f"Function error: {e}")
```

**How to Fix**:
- Check function documentation for argument requirements
- Verify values are not null or unknown unless function supports it
- Ensure argument types match function expectations

---

## Common Scenarios

### Scenario 1: Missing Required Attributes

**Problem**:
```python
from pyvider.cty import CtyObject, CtyString, CtyNumber

schema = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
    }
)

# Error: missing 'age'
data = {"name": "Alice"}
value = schema.validate(data)  # Raises CtyValidationError
```

**Solution**:
```python
# Option 1: Make 'age' optional
schema = CtyObject(
    attribute_types={"name": CtyString(), "age": CtyNumber()},
    optional_attributes={"age"}
)
value = schema.validate({"name": "Alice"})  # Works!

# Option 2: Provide all required fields
value = schema.validate({"name": "Alice", "age": 30})  # Works!
```

---

### Scenario 2: Type Conversion Issues

**Problem**:
```python
from pyvider.cty import CtyNumber

number_type = CtyNumber()
value = number_type.validate("123")  # Raises CtyTypeMismatchError
```

**Solution**:
```python
# Option 1: Use conversion
from pyvider.cty import CtyString, convert

string_val = CtyString().validate("123")
number_val = convert(string_val, CtyNumber())  # Works!

# Option 2: Provide correct type
value = number_type.validate(123)  # Works!
```

---

### Scenario 3: Null vs Missing Attributes

**Problem**:
```python
from pyvider.cty import CtyObject, CtyString, CtyValue

schema = CtyObject(
    attribute_types={"name": CtyString(), "nickname": CtyString()},
    optional_attributes={"nickname"}
)

# What's the difference between these?
data1 = {"name": "Alice"}                    # nickname is missing
data2 = {"name": "Alice", "nickname": None}  # nickname is explicitly null
```

**Solution**:
```python
# Missing optional attribute becomes null automatically
value1 = schema.validate(data1)
print(value1["nickname"].is_null)  # True

# Explicit None also becomes null
value2 = schema.validate(data2)
print(value2["nickname"].is_null)  # True

# Both are equivalent in cty
```

---

### Scenario 4: Accessing Null Values

**Problem**:
```python
from pyvider.cty import CtyObject, CtyString

schema = CtyObject(
    attribute_types={"name": CtyString()},
    optional_attributes={"name"}
)

value = schema.validate({})
name = value["name"].raw_value  # Raises error - can't get raw_value of null
```

**Solution**:
```python
# Check for null before accessing
value = schema.validate({})
if value["name"].is_null:
    print("Name is not provided")
else:
    print(f"Name: {value['name'].raw_value}")
```

---

### Scenario 5: Recursion Depth Exceeded

**Problem**:
```python
# Creating extremely deep nested structure
deep_data = {"level": {}}
current = deep_data["level"]
for i in range(1000):
    current["level"] = {}
    current = current["level"]

# This may raise recursion depth error
```

**Solution**:
```python
from pyvider.cty.context import MAX_VALIDATION_DEPTH

# The default limit is 500 levels
# If you need deeper structures, consider:
# 1. Flattening your data structure
# 2. Using references instead of deep nesting
# 3. Adjusting MAX_VALIDATION_DEPTH (with caution)
```

---

## Debugging Tips

### 1. Enable Detailed Error Messages

Validation errors include the full path to the problematic field:

```python
try:
    value = complex_schema.validate(data)
except CtyValidationError as e:
    print(f"Error at: {e}")
    # Example output: "at path.users[2].address.city: expected CtyString, got int"
```

### 2. Inspect Raw Values

When debugging, inspect the raw Python values:

```python
from pyvider.cty import CtyObject, CtyString

schema = CtyObject(attribute_types={"name": CtyString()})
data = {"name": "Alice"}

print(f"Raw data: {repr(data)}")
value = schema.validate(data)
print(f"Validated value: {value}")
print(f"Name raw value: {value['name'].raw_value}")
```

### 3. Use a Debugger

Set breakpoints in your validation code:

```python
import pdb

try:
    value = schema.validate(data)
except CtyValidationError as e:
    pdb.set_trace()  # Drop into debugger to inspect state
```

### 4. Simplify the Problem

When dealing with complex structures, test incrementally:

```python
# Instead of validating everything at once
full_data = {"user": {"profile": {"settings": {...}}}}

# Test each level separately
user_data = {"profile": {...}}
profile_data = {"settings": {...}}

# Validate from inside out
settings_value = settings_schema.validate(settings_data)
profile_value = profile_schema.validate(profile_data)
user_value = user_schema.validate(user_data)
```

### 5. Check Type Compatibility

Use the type system to verify compatibility:

```python
from pyvider.cty import CtyString, CtyNumber, unify

# Check if types can be unified
try:
    unified_type = unify([CtyString(), CtyNumber()])
    print(f"Unified to: {unified_type}")
except Exception as e:
    print(f"Types are incompatible: {e}")
```

### 6. Validate Incrementally

For complex nested structures, validate step by step:

```python
# Bad: One massive validation that's hard to debug
full_config = {...deeply nested...}
config_value = config_schema.validate(full_config)

# Good: Validate subsections
db_value = db_schema.validate(config["database"])
api_value = api_schema.validate(config["api"])
full_value = full_schema.validate({"database": db_value, "api": api_value})
```

---

## Performance Troubleshooting

### Large Data Structures

**Problem**: Validation is slow for large datasets.

**Solutions**:
- Cache schema objects - don't recreate types repeatedly
- Validate once, reuse the validated `CtyValue`
- Consider batching for very large datasets
- Profile to identify bottlenecks

```python
# Bad: Creating schema inside loop
for item in large_dataset:
    schema = CtyObject(attribute_types={"field": CtyString()})  # Recreated every time!
    value = schema.validate(item)

# Good: Create schema once
schema = CtyObject(attribute_types={"field": CtyString()})
for item in large_dataset:
    value = schema.validate(item)
```

### Deep Nesting

**Problem**: Deeply nested structures cause performance issues.

**Solutions**:
- Flatten data structures where possible
- Use references instead of deep nesting
- Consider alternative data modeling

---

## Getting Help

If you're still stuck after consulting this guide:

1. **Check the documentation**: Review the [User Guide](../user-guide/index.md) and [API Reference](../api/index.md)
2. **Review examples**: Look at the [Examples](../getting-started/examples.md) for similar use cases
3. **Search issues**: Check [GitHub Issues](https://github.com/provide-io/pyvider-cty/issues) for similar problems
4. **Ask for help**: Open a new issue with a minimal reproducible example

When reporting issues, include:
- Complete error message and stack trace
- Minimal code example that reproduces the issue
- Your Python version and pyvider.cty version
- What you expected vs what actually happened
