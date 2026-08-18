# Type Conversion

Type conversion in pyvider.cty allows you to transform values from one type to another when they are compatible. This is different from validation, which requires exact type matches.

## Conversion vs Validation

**Validation** is strict about the *shape* of a position, though a couple of
primitive types coerce a handful of natural spellings on the way in
(`CtyNumber` accepts a numeric string, `CtyBool` accepts `1`/`0` and
`"true"`/`"false"`). `CtyString` does not coerce at all, so it is the clean
example of validation refusing anything but its own type:

```python
from pyvider.cty import CtyString

string_type = CtyString()
string_type.validate(123)     # ❌ Raises CtyValidationError
string_type.validate("123")   # ✅ Returns CtyValue("123")
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

# Accepts (case-sensitively!): "true", "1", "false", "0"
# Any other casing of "true"/"false" (e.g. "TRUE", "True") raises with a
# message telling you to lowercase it; any other string raises outright.
```

Note that `CtyBool().validate(1)` accepts a bare Python `int` directly (see
[Validation](validation.md)), but `convert()` has no Number → Bool entry at
all — go-cty has none either, so `convert(CtyNumber().validate(1), CtyBool())`
raises `CtyConversionError`. Validation's coercion and conversion's table are
two different mechanisms and do not always agree.

### Collection Conversions

`CtyList`, `CtySet` and `CtyMap` all take their element type as the keyword
argument `element_type` — there is no positional form.

**List → Set**
```python
from pyvider.cty import CtyList, CtySet, CtyString

list_val = CtyList(element_type=CtyString()).validate(["a", "b", "a"])
set_val = convert(list_val, CtySet(element_type=CtyString()))
print(set_val.raw_value)  # ['a', 'b'] - duplicates removed
```

`raw_value` on a set is a plain Python `list`, not a `set` or `frozenset` —
`CtySet`'s own payload is an ordered tuple internally (go-cty's canonical
element order), and `raw_value` renders that as a list.

**Set → List**
```python
set_val = CtySet(element_type=CtyString()).validate({"x", "y", "z"})
list_val = convert(set_val, CtyList(element_type=CtyString()))
# Order follows the set's canonical order, not insertion order.
```

**List → Tuple is not a supported conversion**

go-cty has no List → Tuple entry in its conversion table — a collection's
length is a property of the *value*, while a tuple's length is part of its
*type*, and the two are not interchangeable that way. `convert()` matches
that exactly, so this raises `CtyConversionError`:

```python
from pyvider.cty import CtyTuple

list_val = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
# convert(list_val, CtyTuple((CtyString(), CtyString(), CtyString())))  # ❌ raises

# Build the tuple directly instead:
tuple_val = CtyTuple((CtyString(), CtyString(), CtyString())).validate(["a", "b", "c"])
```

`CtyTuple` takes a genuine Python `tuple` of element types (not a `list`) —
`CtyTuple([CtyString()])` raises `CtyTupleValidationError`.

### Converting to Dynamic

Any type can convert to `CtyDynamic`:

```python
from pyvider.cty import CtyDynamic

string_val = CtyString().validate("hello")
dynamic_val = convert(string_val, CtyDynamic())

# CtyDynamic marks a *position* that accepts any type; converting into it is a
# no-op that hands the value back with its own concrete type intact -- it is
# not re-wrapped, and there is no `wrapped_type` attribute to unwrap it with.
print(dynamic_val.type)  # string
```

### Converting Element Types

Convert collections by converting their elements:

```python
from pyvider.cty import CtyList, CtyString, CtyNumber

# List of strings
str_list = CtyList(element_type=CtyString()).validate(["1", "2", "3"])

# Convert to list of numbers
num_list = convert(str_list, CtyList(element_type=CtyNumber()))
print(num_list.raw_value)  # [1, 2, 3]
```

Each element is a `CtyNumber` backed by `Decimal` internally (see
[Values](values.md)), but `raw_value` renders whole numbers as plain Python
`int`, not `Decimal`.

## The `unify()` Function

Type unification finds the single type every input type can convert *to* —
not the vaguest type that could describe them all. `unify()` ports go-cty's
own algorithm, and returns `None` (not `CtyDynamic`) when the given types
have nothing in common — `None` is unambiguously "no common type", where
`CtyDynamic` is also a legitimate unification result in its own right (for a
group of collections that each hold a dynamic element, for instance), so
using it for "no answer" as well made failure indistinguishable from success.

`CtyString` is the one supertype among the primitives — every primitive
value has a string form, so string is the common type whenever a string is
in the mix. Number and bool, on the other hand, have no supertype between
them at all (there is no number ↔ bool conversion; see above), so unifying
those two returns `None`:

```python
from pyvider.cty import unify, CtyString, CtyNumber

# String is the supertype of number
unified_type = unify([CtyString(), CtyNumber()])
print(unified_type)  # string
```

**Use Cases:**
- Merging data from multiple sources
- Finding common type for heterogeneous collections
- Type inference for mixed data

**Examples:**

```python
from pyvider.cty import unify, CtyNumber, CtyBool, CtyString

# Unify numbers and booleans: neither converts to the other, so there is no
# common type at all.
result = unify([CtyNumber(), CtyBool()])
print(result)  # None

# Unify identical types
result = unify([CtyString(), CtyString()])
print(result)  # string

# String, number and bool: string is still the common type, since both
# number and bool convert to string.
result = unify([CtyString(), CtyNumber(), CtyBool()])
print(result)  # string
```

## Conversion with Marks

Marks (metadata) are preserved during conversion:

```python
from pyvider.cty.marks import CtyMark

sensitive = CtyMark("sensitive")

# Mark a numeric string value -- convert() still has to be able to perform
# the underlying conversion; marking a value doesn't change what it converts to.
str_val = CtyString().validate("42")
marked_str = str_val.with_marks({sensitive})

# Convert to number (marks preserved)
num_val = convert(marked_str, CtyNumber())
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
    # Conversion failed: Cannot convert string to number: Number validation
    # error: Cannot represent str value 'hello' as Decimal (...)
```

Common conversion failures:
- String to Number: Non-numeric strings
- String to Bool: Anything other than exactly `"true"`/`"1"`/`"false"`/`"0"` (a
  differently-cased `"TRUE"`/`"False"` raises with a message telling you to
  lowercase it)
- List to Tuple: no such conversion exists at all now (see above)
- Object to Object: Missing required attributes

## Type Inference

Infer cty types from raw Python data:

```python
from pyvider.cty.conversion import infer_cty_type_from_raw

# Infer from primitive
inferred = infer_cty_type_from_raw("hello")
print(inferred)  # string

# Infer from list
inferred = infer_cty_type_from_raw([1, 2, 3])
print(inferred)  # list(number)

# Infer from dict
inferred = infer_cty_type_from_raw({"name": "Alice", "age": 30})
print(inferred)  # object with attributes "name" and "age"
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
from pyvider.cty.conversion import inference_cache_context

with inference_cache_context():
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

### 4. Handle `unify()` Returning `None`

`unify()` returns `None` when the inputs share no common type, and `None`
does not have a `.validate()` method — check for it before using the result:

```python
unified = unify([CtyNumber(), CtyBool()])
if unified is None:
    raise ValueError("no common type for these inputs")

# Where a common type does exist, it's usually string -- every primitive
# converts to string, so mixing a string into the input all but guarantees it:
unified = unify([CtyString(), CtyNumber(), CtyBool()])
# Result: string
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
