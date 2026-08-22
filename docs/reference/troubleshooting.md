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
- [Accessing Null and Unknown Values](#scenario-4-accessing-null-and-unknown-values)
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
│   ├── CtyStringValidationError
│   ├── CtyNumberValidationError
│   ├── CtyBoolValidationError
│   └── CtyCollectionValidationError
│       ├── CtyListValidationError
│       ├── CtyMapValidationError
│       ├── CtySetValidationError
│       └── CtyTupleValidationError
│
├── CtyConversionError
│   ├── CtyTypeConversionError
│   └── CtyTypeParseError
│
├── CtyFunctionError
│
├── EncodingError
│   ├── SerializationError
│   │   ├── CtyMarksSerializationError
│   │   └── DynamicValueError
│   ├── JsonEncodingError
│   ├── MsgPackEncodingError
│   └── DeserializationError
│
├── InvalidTypeError
├── AttributePathError
└── TransformationError
    └── WireFormatError
```

Note: `CtyListValidationError`, `CtyMapValidationError`, `CtySetValidationError` and `CtyTupleValidationError` are all `CtyCollectionValidationError`, which is itself a `CtyValidationError` — catching `CtyCollectionValidationError` catches all four. `JsonEncodingError` and `MsgPackEncodingError` are siblings of `SerializationError` under `EncodingError`, not its subclasses.

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
from pyvider.cty.exceptions import CtyValidationError

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
from pyvider.cty.exceptions import CtyAttributeValidationError

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
from pyvider.cty.exceptions import CtyListValidationError

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
from pyvider.cty.exceptions import CtyMapValidationError

config_type = CtyMap(element_type=CtyNumber())

# This will raise CtyMapValidationError - "three" is not a number.
# Note that a numeric *string* like "3" is not an error here: CtyNumber
# accepts wire-friendly string forms, so only a genuinely non-numeric
# value fails.
try:
    config = config_type.validate({"one": 1, "two": 2, "three": "not-a-number"})
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
from pyvider.cty.exceptions import CtySetValidationError

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
from pyvider.cty.exceptions import CtyTupleValidationError

point_type = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyNumber()))

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

**Description**: Raised by the low-level type API (`CtyObject.get_attribute()`, `CtyMap`'s internal `get`, and similar helpers) when it is called with something other than a `CtyValue` of the expected shape. Ordinary `.validate()` calls do not raise this — a wrong-shaped value passed to `.validate()` raises the type-specific error instead (`CtyStringValidationError`, `CtyNumberValidationError`, and so on, all subclasses of `CtyValidationError`).

**Common Causes**:
- Calling a type's low-level accessor method directly with a raw Python value instead of a `CtyValue`
- Passing something other than a dict to a method that expects an object's internal representation

**Example**:
```python
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.exceptions import CtyTypeMismatchError

person_type = CtyObject(attribute_types={"name": CtyString()})

# get_attribute() is the low-level type API: it requires an actual
# CtyValue, not a raw Python dict.
try:
    person_type.get_attribute({"name": "Bob"}, "name")
except CtyTypeMismatchError as e:
    print(f"Type mismatch: {e}")
```

**How to Fix**:
- Go through `.validate()` and indexing (`value["name"]`) instead of calling the type's low-level accessors directly
- If you do need the low-level API, pass a `CtyValue`, not a raw Python value
- For an ordinary "wrong type passed to `.validate()`" case, catch the type-specific `CtyValidationError` subclass instead (see above)

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
from pyvider.cty.exceptions import CtyConversionError

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

**Description**: A `CtyConversionError` subclass reserved for type-string parsing failures. It is part of the exception hierarchy but `parse_tf_type_to_ctytype()` does not currently raise it itself — an invalid type specification raises `CtyValidationError` instead. Catch `CtyValidationError` for a parse failure today; `CtyTypeParseError` is exported for callers building their own parsers on top of `pyvider.cty`.

**Common Causes** (of the `CtyValidationError` that `parse_tf_type_to_ctytype()` actually raises):
- Invalid or unrecognized Terraform type string syntax
- Unsupported type in string
- Malformed type expression (e.g. an object spec that is not a dict)

**Example**:
```python
from pyvider.cty import parse_tf_type_to_ctytype
from pyvider.cty.exceptions import CtyValidationError

# This will raise CtyValidationError - invalid syntax
try:
    parsed_type = parse_tf_type_to_ctytype("invalid[type{syntax")
except CtyValidationError as e:
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

**Description**: Raised when the bytes handed to `cty_from_msgpack()` are not a MessagePack payload — empty input, a reserved byte, a truncated array, trailing bytes, invalid UTF-8 inside a string, a malformed refined-unknown extension, a dynamic-value header that is not UTF-8 JSON. The `msgpack` library's own exception is chained as `__cause__`. A payload that decodes but does not fit the requested type raises that type's `CtyValidationError` instead, so `except CtyError` around `cty_from_msgpack()` catches every failure, and `except DeserializationError` catches exactly the ones where the bytes themselves are wrong.

**Common Causes**:
- Corrupted, truncated or empty MessagePack data (raises `DeserializationError`, with the `msgpack` library's exception as `__cause__`)
- A malformed refinement or dynamic-type payload inside otherwise well-formed MessagePack (raises `DeserializationError`)
- Schema mismatch between serialization and deserialization (raises a `CtyValidationError` subclass, since the decoded shape is checked against the type you pass in)

**Example**:
```python
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.exceptions import DeserializationError

schema = CtyObject(attribute_types={"key": CtyString()})

# Not valid MessagePack at all: DeserializationError, with the msgpack
# library's own exception chained as __cause__.
try:
    value = cty_from_msgpack(b"invalid msgpack data", schema)
except DeserializationError as e:
    print(f"Deserialization failed: {e}")
```

**How to Fix**:
- Verify the MessagePack data is not corrupted
- Ensure the same schema is used for serialization and deserialization
- Check data was actually serialized with cty_to_msgpack
- Catch `Exception` (or both `DeserializationError` and the `msgpack` package's exceptions) if you need to handle every decode failure uniformly

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
from pyvider.cty import CtyNumber, CtyString

number_val = CtyNumber().validate(123)
value = CtyString().validate(number_val)  # Raises CtyStringValidationError
```

Note that `CtyNumber().validate("123")` is *not* an example of this problem — `CtyNumber` accepts a numeric string directly and returns the number `123`. The failure above comes from handing an already-typed `CtyValue` of one primitive type to a different primitive type's `.validate()`, which does not cross types for you.

**Solution**:
```python
# Option 1: Use conversion
from pyvider.cty import CtyNumber, CtyString, convert

number_val = CtyNumber().validate(123)
string_val = convert(number_val, CtyString())  # Works! -> "123"

# Option 2: Provide the correct type up front
value = CtyString().validate("123")  # Works!
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

### Scenario 4: Accessing Null and Unknown Values

**Problem**: It is tempting to assume `.raw_value` needs a null check because it *looks* like the kind of access that would fail on a missing value. It does not — `.raw_value` on a null value simply returns `None`.

```python
from pyvider.cty import CtyObject, CtyString

schema = CtyObject(
    attribute_types={"name": CtyString()},
    optional_attributes={"name"}
)

value = schema.validate({})
name = value["name"].raw_value  # Returns None -- does NOT raise
print(name)  # None
```

What *does* raise is reading `.raw_value` off an **unknown** value, since there is no Python value to hand back yet:

```python
from pyvider.cty import CtyString, CtyValue

unknown_val = CtyValue.unknown(CtyString())
try:
    unknown_val.raw_value
except ValueError as e:
    print(f"Cannot read an unknown value's raw_value: {e}")
```

**Solution**:
```python
# Check .is_null when you need to tell "genuinely null" apart from other
# cases, even though .raw_value itself will not raise for it:
value = schema.validate({})
if value["name"].is_null:
    print("Name is not provided")
else:
    print(f"Name: {value['name'].raw_value}")

# Check .is_unknown before reading .raw_value off a value that might be
# unknown -- that is the case that actually raises.
if not value["name"].is_unknown:
    print(value["name"].raw_value)
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
from pyvider.cty.config.defaults import MAX_VALIDATION_DEPTH

# The limit is derived from sys.getrecursionlimit(), because each level of
# nesting costs two Python frames: 449 at the default limit of 1000.
# Validating at exactly this depth is guaranteed to work; one level past it
# returns a controlled `unknown` rather than raising.
#
# If you need deeper structures, consider:
# 1. Flattening your data structure
# 2. Using references instead of deep nesting
# 3. Raising sys.setrecursionlimit(), which raises the derived depth with it
# 4. Pinning PYVIDER_CTY_MAX_VALIDATION_DEPTH (only alongside step 3)
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
