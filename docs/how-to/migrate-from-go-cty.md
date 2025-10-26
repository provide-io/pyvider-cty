# How to Migrate from go-cty

This guide helps you migrate from HashiCorp's go-cty (Go) to pyvider.cty (Python) with step-by-step instructions and practical examples.

> **Want a detailed feature comparison?** See the **[go-cty Comparison](../reference/go-cty-comparison.md)** reference for comprehensive API differences, feature parity matrix, and performance considerations. This guide focuses on the practical migration process.

## Key Differences

### Language Differences

| Aspect | go-cty (Go) | pyvider.cty (Python) |
|--------|-------------|----------------------|
| **Language** | Go | Python 3.11+ |
| **Type System** | Go interfaces | Python classes with type hints |
| **Null Safety** | Built-in | `is_null` property |
| **Immutability** | By design | By design (attrs frozen) |
| **Error Handling** | `error` return values | Python exceptions |

### API Differences

#### Creating Types

**go-cty (Go):**
```go
import "github.com/zclconf/go-cty/cty"

stringType := cty.String
numberType := cty.Number
boolType := cty.Bool

listType := cty.List(cty.String)
objectType := cty.Object(map[string]cty.Type{
    "name": cty.String,
    "age":  cty.Number,
})
```

**pyvider.cty (Python):**
```python
from pyvider.cty import CtyString, CtyNumber, CtyBool, CtyList, CtyObject

string_type = CtyString()
number_type = CtyNumber()
bool_type = CtyBool()

list_type = CtyList(element_type=CtyString())
object_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    }
)
```

#### Creating Values

**go-cty (Go):**
```go
strVal := cty.StringVal("hello")
numVal := cty.NumberIntVal(42)
boolVal := cty.BoolVal(true)

objVal := cty.ObjectVal(map[string]cty.Value{
    "name": cty.StringVal("Alice"),
    "age":  cty.NumberIntVal(30),
})
```

**pyvider.cty (Python):**
```python
# pyvider.cty validates raw Python data
object_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    }
)

obj_val = object_type.validate({
    "name": "Alice",
    "age": 30
})
```

#### Accessing Values

**go-cty (Go):**
```go
// Type assertion required
name := objVal.GetAttr("name").AsString()
age := objVal.GetAttr("age").AsBigFloat()

// Check if null
if objVal.IsNull() {
    // handle null
}
```

**pyvider.cty (Python):**
```python
# Dictionary-style access
name = obj_val['name'].raw_value  # "Alice"
age = obj_val['age'].raw_value    # 30

# Check if null
if obj_val.is_null:
    # handle null
```

## Serialization

### MessagePack

Both go-cty and pyvider.cty use MessagePack for serialization, and they're compatible!

**go-cty (Go):**
```go
import "github.com/zclconf/go-cty/cty/msgpack"

// Serialize
encoded, err := msgpack.Marshal(val, valType)
if err != nil {
    // handle error
}

// Deserialize
decoded, err := msgpack.Unmarshal(encoded, valType)
if err != nil {
    // handle error
}
```

**pyvider.cty (Python):**
```python
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

# Serialize
encoded = cty_to_msgpack(val, val_type)

# Deserialize
decoded = cty_from_msgpack(encoded, val_type)
```

**Cross-language compatibility:**
```python
# Python can read Go's msgpack
go_encoded = load_from_go_service()
py_value = cty_from_msgpack(go_encoded, schema)

# Go can read Python's msgpack
py_encoded = cty_to_msgpack(py_value, schema)
send_to_go_service(py_encoded)
```

## Type Parsing

### Terraform Type Strings

**go-cty (Go):**
```go
import "github.com/hashicorp/hcl/v2/hclsyntax"

// Parse type string
expr, diags := hclsyntax.ParseExpression([]byte("list(string)"), "", hcl.Pos{})
valType, diags := convert.GetType(expr, nil)
```

**pyvider.cty (Python):**
```python
from pyvider.cty.parser import parse_tf_type_to_ctytype

# Parse type string
val_type = parse_tf_type_to_ctytype("list(string)")
```

## Common Patterns

### Validation

**go-cty (Go):**
```go
// Explicit conversion/validation
val, err := convert.Convert(unknownVal, targetType)
if err != nil {
    // validation failed
}
```

**pyvider.cty (Python):**
```python
# Validation via validate method
try:
    val = target_type.validate(raw_data)
except CtyValidationError as e:
    # validation failed
```

### Iterating Collections

**go-cty (Go):**
```go
// List iteration
for it := listVal.ElementIterator(); it.Next(); {
    _, val := it.Element()
    // process val
}

// Object iteration
for it := objVal.ElementIterator(); it.Next(); {
    key, val := it.Element()
    // process key, val
}
```

**pyvider.cty (Python):**
```python
# List iteration (Pythonic)
for val in list_val:
    # process val

# Object iteration
for key in obj_val.attribute_names():
    val = obj_val[key]
    # process key, val

# Or use raw_value
for key, val in obj_val.raw_value.items():
    # process as Python dict
```

### Marks

**go-cty (Go):**
```go
import "github.com/zclconf/go-cty/cty"

// Add mark
marked := val.Mark("sensitive")

// Check for mark
if val.HasMark("sensitive") {
    // handle sensitive data
}

// Remove mark
unmarked := val.Unmark()
```

**pyvider.cty (Python):**
```python
from pyvider.cty.marks import CtyMark

# Create mark
sensitive_mark = CtyMark("sensitive")

# Add mark
marked = val.with_marks({sensitive_mark})

# Check for mark
if sensitive_mark in val.marks:
    # handle sensitive data

# Remove all marks (returns tuple)
unmarked, removed_marks = val.unmark()
```

## Migration Checklist

### Step 1: Install pyvider.cty

```bash
uv add pyvider-cty
# or
pip install pyvider-cty
```

### Step 2: Update Type Definitions

Replace Go type definitions:

```python
# Before (Go):
# myType := cty.Object(map[string]cty.Type{...})

# After (Python):
from pyvider.cty import CtyObject, CtyString, CtyNumber

my_type = CtyObject(
    attribute_types={
        "field1": CtyString(),
        "field2": CtyNumber()
    }
)
```

### Step 3: Update Value Creation

Replace Go value creation:

```python
# Before (Go):
# val := cty.ObjectVal(map[string]cty.Value{...})

# After (Python):
val = my_type.validate({
    "field1": "value",
    "field2": 42
})
```

### Step 4: Update Value Access

Replace Go value access:

```python
# Before (Go):
# str := val.GetAttr("field1").AsString()

# After (Python):
str_val = val['field1'].raw_value
```

### Step 5: Update Error Handling

Replace Go error handling:

```python
# Before (Go):
# val, err := something()
# if err != nil { return err }

# After (Python):
from pyvider.cty.exceptions import CtyValidationError

try:
    val = something()
except CtyValidationError as e:
    # handle error
```

### Step 6: Test Serialization

Verify MessagePack compatibility:

```python
# Test round-trip
encoded = cty_to_msgpack(val, schema)
decoded = cty_from_msgpack(encoded, schema)
assert decoded == val

# Test with Go-produced data
go_data = load_from_go()
py_value = cty_from_msgpack(go_data, schema)
```

## Common Gotchas

### 1. Value Construction

**Go allows direct value construction:**
```go
val := cty.ObjectVal(...)
```

**Python requires validation:**
```python
val = obj_type.validate(...)
```

### 2. Type vs Value

**In Go, types and values are more distinct:**
```go
valType := val.Type()
```

**In Python, use the property:**
```python
val_type = val.type
```

### 3. Null Handling

**Go uses IsNull():**
```go
if val.IsNull() { ... }
```

**Python uses is_null:**
```python
if val.is_null: ...
```

### 4. Unknown Values

**Both support unknown values, but creation differs:**

```python
# pyvider.cty
from pyvider.cty.values import UnknownValue

unknown_val = UnknownValue(CtyString())
```

## Example Migration

### Go Code

```go
package main

import (
    "github.com/zclconf/go-cty/cty"
    "github.com/zclconf/go-cty/cty/msgpack"
)

func validateUser(data map[string]interface{}) (cty.Value, error) {
    userType := cty.Object(map[string]cty.Type{
        "name": cty.String,
        "age":  cty.Number,
    })

    // Convert to cty value
    val := cty.ObjectVal(map[string]cty.Value{
        "name": cty.StringVal(data["name"].(string)),
        "age":  cty.NumberIntVal(int64(data["age"].(int))),
    })

    return val, nil
}
```

### Python Code

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber
from pyvider.cty.exceptions import CtyValidationError

def validate_user(data):
    user_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        }
    )

    try:
        return user_type.validate(data)
    except CtyValidationError as e:
        raise ValueError(f"Invalid user data: {e}")
```

## Next Steps

- [Validate data](validate-data.md)
- [Serialize values](serialize-values.md)
- [Work with Terraform](work-with-terraform.md)
- [Compare with go-cty](../reference/go-cty-comparison.md)
