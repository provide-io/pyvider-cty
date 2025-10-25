# Type Conversion

Type conversion in pyvider.cty allows you to transform values from one type to another when they are compatible. This is different from validation, which requires exact type matches.

## Conversion vs Validation

**Validation** is strict - it checks that data matches a type exactly:

```python
from pyvider.cty import CtyNumber

number_type = CtyNumber()
number_type.validate("123")  # ❌ Raises CtyValidationError
number_type.validate(123)     # ✅ Returns CtyValue(123)
```

**Conversion** is flexible - it transforms values between compatible types:

```python
from pyvider.cty import CtyString, CtyNumber, convert

string_val = CtyString().validate("123")
number_val = convert(string_val, CtyNumber())  # ✅ Converts to number
print(number_val.raw_value)  # 123
```

## The `convert()` Function

The primary interface for conversion is the `convert()` function:

```python
from pyvider.cty import convert

converted_value = convert(source_value, target_type)
```

**Parameters:**
- `source_value`: A `CtyValue` to convert from
- `target_type`: A `CtyType` to convert to

**Returns:**
- A new `CtyValue` of the target type

**Raises:**
- `CtyConversionError` if conversion is not possible

## Conversion Rules

### Primitive Conversions

**String → Number**
```python
from pyvider.cty import CtyString, CtyNumber, convert

str_val = CtyString().validate("42.5")
num_val = convert(str_val, CtyNumber())
print(num_val.raw_value)  # Decimal('42.5')
```

**Number → String**
```python
num_val = CtyNumber().validate(42)
str_val = convert(num_val, CtyString())
print(str_val.raw_value)  # "42"
```

**Bool → String**
```python
from pyvider.cty import CtyBool

bool_val = CtyBool().validate(True)
str_val = convert(bool_val, CtyString())
print(str_val.raw_value)  # "true"
```

**String → Bool**
```python
str_val = CtyString().validate("true")
bool_val = convert(str_val, CtyBool())
print(bool_val.raw_value)  # True

# Accepts: "true", "false" (case-insensitive)
# Rejects: Other strings
```

**Number → Bool**
```python
# Non-zero → True, Zero → False
num_val = CtyNumber().validate(1)
bool_val = convert(num_val, CtyBool())
print(bool_val.raw_value)  # True
```

### Collection Conversions

**List → Set**
```python
from pyvider.cty import CtyList, CtySet, CtyString

list_val = CtyList(CtyString()).validate(["a", "b", "a"])
set_val = convert(list_val, CtySet(CtyString()))
print(set_val.raw_value)  # {"a", "b"} - duplicates removed
```

**Set → List**
```python
set_val = CtySet(CtyString()).validate({"x", "y", "z"})
list_val = convert(set_val, CtyList(CtyString()))
# Order may vary (sets are unordered)
```

**List → Tuple**
```python
from pyvider.cty import CtyTuple

list_val = CtyList(CtyString()).validate(["a", "b", "c"])
tuple_val = convert(list_val, CtyTuple([CtyString(), CtyString(), CtyString()]))
```

### Converting to Dynamic

Any type can convert to `CtyDynamic`:

```python
from pyvider.cty import CtyDynamic

string_val = CtyString().validate("hello")
dynamic_val = convert(string_val, CtyDynamic())

# The dynamic value wraps the original type
print(dynamic_val.wrapped_type)  # CtyString
```

### Converting Element Types

Convert collections by converting their elements:

```python
from pyvider.cty import CtyList, CtyString, CtyNumber

# List of strings
str_list = CtyList(CtyString()).validate(["1", "2", "3"])

# Convert to list of numbers
num_list = convert(str_list, CtyList(CtyNumber()))
print(num_list.raw_value)  # [Decimal('1'), Decimal('2'), Decimal('3')]
```

## The `unify()` Function

Type unification finds a common type that can represent multiple types:

```python
from pyvider.cty import unify, CtyString, CtyNumber

# Find common type for string and number
unified_type = unify([CtyString(), CtyNumber()])
print(unified_type)  # CtyDynamic - the most general common type
```

**Use Cases:**
- Merging data from multiple sources
- Finding common type for heterogeneous collections
- Type inference for mixed data

**Examples:**

```python
from pyvider.cty import unify, CtyNumber, CtyBool

# Unify numbers and booleans
result = unify([CtyNumber(), CtyBool()])
# Result: CtyNumber (bools can convert to numbers)

# Unify identical types
result = unify([CtyString(), CtyString()])
# Result: CtyString

# Unify incompatible types
result = unify([CtyString(), CtyNumber(), CtyBool()])
# Result: CtyDynamic (fallback to most general type)
```

## Conversion with Marks

Marks (metadata) are preserved during conversion:

```python
from pyvider.cty.marks import CtyMark

sensitive = CtyMark("sensitive")

# Mark a string value
str_val = CtyString().validate("secret")
marked_str = str_val.with_marks({sensitive})

# Convert to number (marks preserved)
num_val = convert(marked_str, CtyNumber())  # Converts "secret" if numeric
print(sensitive in num_val.marks)  # True - marks preserved
```

## Null and Unknown Values

Conversion behavior with special values:

```python
from pyvider.cty.values import CtyValue

# Null values
null_string = CtyValue.null(CtyString())
null_number = convert(null_string, CtyNumber())
print(null_number.is_null)  # True - nullness preserved

# Unknown values
unknown_string = CtyValue.unknown(CtyString())
unknown_number = convert(unknown_string, CtyNumber())
print(unknown_number.is_unknown)  # True - unknown status preserved
```

## Error Handling

Conversions can fail:

```python
from pyvider.cty.exceptions import CtyConversionError

try:
    # Can't convert non-numeric string to number
    str_val = CtyString().validate("hello")
    num_val = convert(str_val, CtyNumber())
except CtyConversionError as e:
    print(f"Conversion failed: {e}")
    # Conversion failed: Cannot convert "hello" to CtyNumber
```

Common conversion failures:
- String to Number: Non-numeric strings
- String to Bool: Strings other than "true"/"false"
- List to Tuple: Length mismatch
- Object to Object: Missing required attributes

## Type Inference

Infer cty types from raw Python data:

```python
from pyvider.cty.conversion import infer_cty_type_from_raw

# Infer from primitive
inferred = infer_cty_type_from_raw("hello")
print(inferred)  # CtyString

# Infer from list
inferred = infer_cty_type_from_raw([1, 2, 3])
print(inferred)  # CtyList(element_type=CtyNumber)

# Infer from dict
inferred = infer_cty_type_from_raw({"name": "Alice", "age": 30})
print(inferred)  # CtyObject with inferred attributes
```

**Type Inference Rules:**

1. **Primitives**: Direct mapping (str → CtyString, int → CtyNumber, etc.)
2. **Lists**: Infers element type from first element or uses CtyDynamic for mixed types
3. **Dicts with string keys**: CtyObject (if all keys are valid identifiers) or CtyMap
4. **Dicts with non-string keys**: CtyMap
5. **Sets**: CtySet with inferred element type
6. **Tuples**: CtyTuple with per-element types
7. **None**: CtyDynamic

**Inference Caching:**

Type inference can be expensive. Use caching for repeated inference:

```python
from pyvider.cty.conversion import InferenceCacheContext

with InferenceCacheContext():
    # Repeated inference uses cache
    for data in large_dataset:
        schema = infer_cty_type_from_raw(data)
        validated = schema.validate(data)
```

## Conversion Best Practices

### 1. Prefer Explicit Schemas

Use `convert()` for known conversions, not as a substitute for proper schemas:

```python
# ✅ GOOD: Define explicit schema
config_schema = CtyObject(
    attribute_types={
        "timeout": CtyNumber(),
        "retries": CtyNumber()
    }
)
config = config_schema.validate(raw_data)

# ❌ AVOID: Over-reliance on conversion
config = infer_cty_type_from_raw(raw_data).validate(raw_data)
```

### 2. Handle Conversion Errors

Always handle potential conversion failures:

```python
def safe_convert(value, target_type):
    """Convert with error handling."""
    try:
        return convert(value, target_type)
    except CtyConversionError as e:
        logger.warning(f"Conversion failed: {e}")
        return None
```

### 3. Document Conversion Requirements

Make it clear when conversion is necessary:

```python
def process_config(config_data: dict) -> CtyValue:
    """Process configuration data.

    Args:
        config_data: Raw configuration (may have string numbers)

    Returns:
        Validated and converted configuration

    Note:
        Numeric config values provided as strings will be
        automatically converted to numbers.
    """
    raw_config = config_schema.validate(config_data)
    # Convert string numbers to actual numbers if needed
    return convert(raw_config, normalized_config_schema)
```

### 4. Use Type Unification Carefully

Unification to `CtyDynamic` loses type safety:

```python
# ⚠️ Use with caution
unified = unify([CtyString(), CtyNumber(), CtyBool()])
# Result: CtyDynamic - lost all type specificity

# ✅ Better: Find more specific common type if possible
unified = unify([CtyNumber(), CtyBool()])
# Result: CtyNumber - more specific, maintains some type safety
```

## Performance Considerations

Conversion has computational cost:

1. **Type checking** - Validates source and target compatibility
2. **Value transformation** - Creates new immutable values
3. **Deep conversion** - Converts nested structures recursively

For performance-critical paths:

```python
# Convert once, reuse many times
converted_config = convert(raw_config, target_schema)

for _ in range(1000):
    # Use converted value without reconverting
    process(converted_config)
```

## See Also

- **[Validation](validation.md)** - Strict type checking
- **[API: Conversion](../../api/conversion.md)** - Conversion API reference
- **[Type Reference](../type-reference/primitives.md)** - All available types
