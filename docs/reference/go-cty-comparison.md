# Comparison with Go-Cty

`pyvider.cty` is a Python implementation of the `cty` type system, which was originally developed in Go as `go-cty` for use in HashiCorp's Terraform. While `pyvider.cty` aims to be a faithful implementation of the `cty` specification, there are some differences between the two libraries due to language differences and Python idioms.

> **Looking to migrate from go-cty?** See the **[How-To: Migrate from go-cty](../how-to/migrate-from-go-cty.md)** guide for step-by-step migration instructions and a complete checklist. This document focuses on feature comparison and API differences.

## Overview

Both libraries implement the same conceptual type system with:
- Primitive, collection, and structural types
- Null and unknown value semantics
- Mark system for metadata
- Type conversion and unification
- MessagePack serialization for cross-language compatibility

## Key Differences

| Feature | `go-cty` | `pyvider.cty` | Notes |
|---|---|---|---|
| **Language** | Go (compiled) | Python (interpreted) | Affects performance and idioms |
| **Type System** | Go interfaces & structs | Python classes with `@attrs` | Both provide strong typing |
| **API Style** | Idiomatic Go | Idiomatic Python | Different but equivalent patterns |
| **Performance** | Faster (compiled) | Slower (interpreted) | Python fast enough for typical use |
| **Null Handling** | `cty.NullVal(type)` | `CtyValue.null(type)` | Class method vs function |
| **Package Structure** | Multiple packages | Single `pyvider.cty` package | Python convention |

## API Translation Examples

### Creating Types

**Go (go-cty):**
```go
import "github.com/zclconf/go-cty/cty"

// Primitive type
stringType := cty.String

// Object type
personType := cty.Object(map[string]cty.Type{
    "name": cty.String,
    "age":  cty.Number,
})

// List type
listType := cty.List(cty.String)
```

**Python (pyvider.cty):**
```python
from pyvider.cty import CtyString, CtyNumber, CtyObject, CtyList

# Primitive type
string_type = CtyString()

# Object type
person_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
    }
)

# List type
list_type = CtyList(element_type=CtyString())
```

### Creating Values

**Go:**
```go
// String value
strVal := cty.StringVal("hello")

// Number value
numVal := cty.NumberIntVal(42)

// Object value
person := cty.ObjectVal(map[string]cty.Value{
    "name": cty.StringVal("Alice"),
    "age":  cty.NumberIntVal(30),
})

// Null value
nullVal := cty.NullVal(cty.String)

// Unknown value
unknownVal := cty.UnknownVal(cty.String)
```

**Python:**
```python
from pyvider.cty import CtyString, CtyNumber, CtyObject
from pyvider.cty.values import CtyValue

# Validate data (preferred approach)
str_val = CtyString().validate("hello")
num_val = CtyNumber().validate(42)

# Object value
person_type = CtyObject(
    attribute_types={"name": CtyString(), "age": CtyNumber()}
)
person = person_type.validate({"name": "Alice", "age": 30})

# Null value
null_val = CtyValue.null(CtyString())

# Unknown value
unknown_val = CtyValue.unknown(CtyString())
```

### Accessing Values

**Go:**
```go
// Access raw value
rawStr := strVal.AsString()
rawNum, _ := numVal.AsBigFloat().Int64()

// Access object attribute
nameVal := person.GetAttr("name")

// Check for null/unknown
if person.IsNull() {
    // handle null
}
```

**Python:**
```python
# Access raw value
raw_str = str_val.raw_value
raw_num = num_val.raw_value

# Access object attribute
name_val = person['name']

# Check for null/unknown
if person.is_null:
    # handle null
```

### Marks

**Go:**
```go
import "github.com/zclconf/go-cty/cty"

// Create marked value
sensitive := "sensitive"
marked := val.Mark(sensitive)

// Check for marks
if marked.HasMark(sensitive) {
    // handle sensitive data
}

// Remove marks
unmarked, marks := marked.Unmark()
```

**Python:**
```python
from pyvider.cty.marks import CtyMark

# Create marked value
sensitive = CtyMark("sensitive")
marked = val.mark(sensitive)  # Single mark
# Or: marked = val.with_marks({sensitive})  # Set of marks

# Check for marks
if sensitive in marked.marks:
    # handle sensitive data

# Remove all marks (returns tuple of unmarked value and marks)
unmarked_val, removed_marks = marked.unmark()
```

### Type Conversion

**Go:**
```go
import "github.com/zclconf/go-cty/cty/convert"

// Convert string to number
numVal, err := convert.Convert(strVal, cty.Number)
if err != nil {
    // handle conversion error
}

// Unify types
unified, _ := convert.UnifyUnsafe([]cty.Type{cty.String, cty.Number})
```

**Python:**
```python
from pyvider.cty import convert, unify, CtyNumber
from pyvider.cty.exceptions import CtyConversionError

# Convert string to number
try:
    num_val = convert(str_val, CtyNumber())
except CtyConversionError as e:
    # handle conversion error
    pass

# Unify types
unified = unify([CtyString(), CtyNumber()])
```

### Serialization

**Go:**
```go
import (
    "github.com/zclconf/go-cty/cty"
    "github.com/zclconf/go-cty/cty/msgpack"
)

// Serialize to MessagePack
bytes, err := msgpack.Marshal(val, valType)

// Deserialize from MessagePack
val, err = msgpack.Unmarshal(bytes, valType)
```

**Python:**
```python
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

# Serialize to MessagePack
msgpack_bytes = cty_to_msgpack(val, val_type)

# Deserialize from MessagePack
val = cty_from_msgpack(msgpack_bytes, val_type)
```

## Idiom Differences

### Error Handling

**Go:** Uses explicit error returns
```go
val, err := someFunction()
if err != nil {
    return err
}
```

**Python:** Uses exceptions
```python
try:
    val = some_function()
except CtyValidationError as e:
    # handle error
    pass
```

### Iteration

**Go:** Range-based for loops
```go
it := listVal.ElementIterator()
for it.Next() {
    _, elemVal := it.Element()
    // process elemVal
}
```

**Python:** Pythonic iteration
```python
for elem_val in list_val:
    # process elem_val
    pass
```

### Optional Attributes

**Go:** Uses `OptionalAttrs` in object definition
```go
objType := cty.ObjectWithOptionalAttrs(
    map[string]cty.Type{
        "name": cty.String,
        "age":  cty.Number,
    },
    []string{"age"}, // optional attributes
)
```

**Python:** Uses `optional_attributes` parameter
```python
obj_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    },
    optional_attributes={"age"}
)
```

## Serialization Compatibility

The MessagePack serialization format is **fully compatible** between go-cty and pyvider.cty:

```python
# Python serializes
python_bytes = cty_to_msgpack(value, schema)

# Go can deserialize the same bytes
# val, err := msgpack.Unmarshal(python_bytes, goSchema)

# And vice versa - Go serializes, Python deserializes
```

This enables true cross-language interoperability for:
- Terraform provider development
- Multi-language systems
- Configuration sharing

## Performance Considerations

**go-cty advantages:**
- Faster execution (compiled vs interpreted)
- Lower memory overhead
- Better for CPU-intensive operations

**pyvider.cty advantages:**
- Rapid development and prototyping
- Rich Python ecosystem integration
- Easier debugging and introspection
- Better for I/O-bound operations

**Performance tips for pyvider.cty:**
```python
# Cache schemas - don't recreate them
config_schema = CtyObject(
    attribute_types={...}
)  # Create once

# Reuse validated values
config = config_schema.validate(raw_data)  # Validate once
for _ in range(1000):
    process(config)  # Reuse many times

# Avoid repeated type construction in loops
# Bad: Creates new type each iteration
for data in large_dataset:
    schema = CtyObject(attribute_types={"field": CtyString()})
    value = schema.validate(data)

# Good: Create schema once
schema = CtyObject(attribute_types={"field": CtyString()})
for data in large_dataset:
    value = schema.validate(data)
```

## Migration Checklist

When migrating from go-cty to pyvider.cty:

- [ ] Replace `cty.StringVal()` with `.validate()` pattern
- [ ] Update `val.AsString()` to `val.raw_value`
- [ ] Change `val.GetAttr("key")` to `val['key']`
- [ ] Replace `cty.NullVal(type)` with `CtyValue.null(type)`
- [ ] Update error handling from `err` returns to exceptions
- [ ] Convert iterator loops to Python `for` loops
- [ ] Update package imports to `pyvider.cty`
- [ ] Review and update optional attribute syntax
- [ ] Test MessagePack serialization compatibility
- [ ] Verify mark handling with new API

## Feature Parity Matrix

| Feature | go-cty | pyvider.cty | Notes |
|---|---|---|---|
| **Primitive Types** | ✅ | ✅ | Full parity |
| **Collection Types** | ✅ | ✅ | Full parity |
| **Structural Types** | ✅ | ✅ | Full parity |
| **Dynamic Type** | ✅ | ✅ | Full parity |
| **Capsule Types** | ✅ | ✅ | Full parity |
| **Marks** | ✅ | ✅ | Full parity |
| **Null/Unknown Values** | ✅ | ✅ | Full parity |
| **Refined Unknowns** | ✅ | ✅ | Full parity |
| **Type Conversion** | ✅ | ✅ | Full parity |
| **Type Unification** | ✅ | ✅ | Full parity |
| **MessagePack Serialization** | ✅ | ✅ | Cross-compatible |
| **JSON Encoding Functions** | ✅ | ✅ | Via `jsonencode`/`jsondecode` functions |
| **Standard Library Functions** | ✅ | ✅ | Comparable coverage |
| **Path Navigation** | ✅ | ✅ | Full parity |
| **Terraform Type Parsing** | ✅ | ✅ | Full parity |

## Common Migration Patterns

### Pattern 1: Validation Function

**Go:**
```go
func ValidateConfig(raw map[string]interface{}) (cty.Value, error) {
    configType := cty.Object(map[string]cty.Type{
        "host": cty.String,
        "port": cty.Number,
    })

    val, err := gocty.ToCtyValue(raw, configType)
    return val, err
}
```

**Python:**
```python
def validate_config(raw: dict) -> CtyValue:
    config_type = CtyObject(
        attribute_types={
            "host": CtyString(),
            "port": CtyNumber(),
        }
    )

    try:
        return config_type.validate(raw)
    except CtyValidationError as e:
        # Handle or re-raise
        raise ValueError(f"Invalid config: {e}") from e
```

### Pattern 2: Iterating Collections

**Go:**
```go
func ProcessList(listVal cty.Value) {
    it := listVal.ElementIterator()
    for it.Next() {
        _, val := it.Element()
        process(val)
    }
}
```

**Python:**
```python
def process_list(list_val: CtyValue) -> None:
    for val in list_val:
        process(val)
```

### Pattern 3: Working with Marks

**Go:**
```go
func RedactSensitive(val cty.Value) cty.Value {
    val, marks := val.Unmark()
    for mark := range marks {
        if mark == "sensitive" {
            return cty.StringVal("[REDACTED]")
        }
    }
    return val
}
```

**Python:**
```python
from pyvider.cty.marks import CtyMark

def redact_sensitive(val: CtyValue) -> CtyValue:
    sensitive = CtyMark("sensitive")
    if sensitive in val.marks:
        return CtyString().validate("[REDACTED]")
    return val.without_all_marks()
```

## Getting Help

If you're migrating from go-cty and need assistance:

- Check the **[How-To: Migrate from go-cty](../how-to/migrate-from-go-cty.md)** guide
- Review the **[API Reference](../api/index.md)** for pyvider.cty equivalents
- Open an issue on [GitHub](https://github.com/provide-io/pyvider-cty/issues)
- Join discussions about migration challenges

## Further Reading

- **[go-cty Documentation](https://pkg.go.dev/github.com/zclconf/go-cty/cty)** - Official go-cty docs
- **[Terraform Type System](https://developer.hashicorp.com/terraform/language/expressions/types)** - Terraform's use of cty
- **[How-To: Work with Terraform](../how-to/work-with-terraform.md)** - Terraform integration guide
