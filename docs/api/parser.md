# Type Parsing

The `pyvider.cty.parser` module provides functions for parsing Terraform type strings and JSON type specifications into `pyvider.cty` type objects.

## Parser Functions

### `parse_tf_type_to_ctytype()`

Parses a Terraform type constraint (as a Python object or string) into a `CtyType` instance.

**Signature:**
```python
def parse_tf_type_to_ctytype(tf_type: Any) -> CtyType[Any]
```

**Parameters:**
- `tf_type`: A Terraform type specification, which can be:
  - A string for primitive types: `"string"`, `"number"`, `"bool"`, `"dynamic"`
  - A list with two elements `[type_kind, type_spec]` for collections and structural types
  - A nested structure for complex types

**Returns:**
- A `CtyType` instance corresponding to the Terraform type

**Raises:**
- `CtyValidationError`: If the type specification is invalid

**Examples:**

```python
from pyvider.cty.parser import parse_tf_type_to_ctytype

# Primitive types
string_type = parse_tf_type_to_ctytype("string")
number_type = parse_tf_type_to_ctytype("number")
bool_type = parse_tf_type_to_ctytype("bool")
dynamic_type = parse_tf_type_to_ctytype("dynamic")

# Collection types (JSON array format)
list_type = parse_tf_type_to_ctytype(["list", "string"])
map_type = parse_tf_type_to_ctytype(["map", "number"])
set_type = parse_tf_type_to_ctytype(["set", "bool"])

# Object type
object_type = parse_tf_type_to_ctytype([
    "object",
    {
        "name": "string",
        "age": "number",
        "active": "bool"
    }
])

# Tuple type
tuple_type = parse_tf_type_to_ctytype([
    "tuple",
    ["string", "number", "bool"]
])

# Nested types
nested_type = parse_tf_type_to_ctytype([
    "list",
    ["object", {"id": "string", "value": "number"}]
])
```

### `parse_type_string_to_ctytype()`

**Alias for `parse_tf_type_to_ctytype()`**

This function is an alias to `parse_tf_type_to_ctytype()` and provides identical functionality. Both names are available for backward compatibility and user preference.

```python
from pyvider.cty.parser import parse_type_string_to_ctytype

# Same as parse_tf_type_to_ctytype()
string_type = parse_type_string_to_ctytype("string")
```

**Note**: Use `parse_tf_type_to_ctytype()` for clarity, as it explicitly indicates the function parses Terraform type specifications.

## Type Specification Format

Terraform uses a JSON-based format to represent types:

### Primitive Types

Represented as strings:
- `"string"` → `CtyString()`
- `"number"` → `CtyNumber()`
- `"bool"` → `CtyBool()`
- `"dynamic"` → `CtyDynamic()`

### Collection Types

Represented as `[kind, element_type]`:
- `["list", "string"]` → `CtyList(element_type=CtyString())`
- `["set", "number"]` → `CtySet(element_type=CtyNumber())`
- `["map", "bool"]` → `CtyMap(element_type=CtyBool())`

### Structural Types

**Object**: `["object", {...}]`
```python
["object", {
    "attr1": "string",
    "attr2": "number"
}]
```

**Tuple**: `["tuple", [...]]`
```python
["tuple", ["string", "number", "bool"]]
```

## Integration with Terraform

These parser functions are essential for working with Terraform:

### Parsing Variable Types

```python
from pyvider.cty.parser import parse_tf_type_to_ctytype

# Terraform variable block:
# variable "vpc_config" {
#   type = object({
#     cidr = string
#     region = string
#   })
# }

# Parse the type
vpc_type = parse_tf_type_to_ctytype([
    "object",
    {
        "cidr": "string",
        "region": "string"
    }
])

# Validate data
vpc_data = {
    "cidr": "10.0.0.0/16",
    "region": "us-east-1"
}

vpc_value = vpc_type.validate(vpc_data)
```

### Parsing Resource Schemas

```python
# Terraform resource schema
resource_schema_json = [
    "object",
    {
        "name": "string",
        "instance_type": "string",
        "tags": ["map", "string"]
    }
]

resource_type = parse_tf_type_to_ctytype(resource_schema_json)

# Use for validation
resource_config = {
    "name": "web-server",
    "instance_type": "t2.micro",
    "tags": {"Environment": "production"}
}

validated_config = resource_type.validate(resource_config)
```

## Error Handling

The parser raises `CtyValidationError` for invalid type specifications:

```python
from pyvider.cty.parser import parse_tf_type_to_ctytype
from pyvider.cty.exceptions import CtyValidationError

try:
    # Invalid: unknown primitive type
    invalid_type = parse_tf_type_to_ctytype("invalid_type")
except CtyValidationError as e:
    print(f"Parse error: {e}")

try:
    # Invalid: object spec must be a dict
    invalid_object = parse_tf_type_to_ctytype(["object", "not_a_dict"])
except CtyValidationError as e:
    print(f"Parse error: {e}")
```

## Common Patterns

### Parsing from JSON Configuration

```python
import json
from pyvider.cty.parser import parse_tf_type_to_ctytype

# Load type specification from JSON file
with open("schema.json") as f:
    type_spec = json.load(f)

# Parse to CtyType
schema = parse_tf_type_to_ctytype(type_spec)
```

### Dynamic Schema Loading

```python
def load_schema(schema_name: str) -> CtyType:
    """Load a schema by name from configuration."""
    schemas = {
        "user": ["object", {"name": "string", "email": "string"}],
        "post": ["object", {"title": "string", "content": "string"}],
    }

    if schema_name not in schemas:
        raise ValueError(f"Unknown schema: {schema_name}")

    return parse_tf_type_to_ctytype(schemas[schema_name])

# Use it
user_type = load_schema("user")
post_type = load_schema("post")
```

## See Also

- **[Terraform Interoperability](../user-guide/advanced/terraform-interop.md)** - Working with Terraform types
- **[How to Work with Terraform](../how-to/work-with-terraform.md)** - Practical Terraform integration
- **[Types API](types/index.md)** - Type system reference

---

::: pyvider.cty.parser
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
