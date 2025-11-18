# Terraform Interoperability

`pyvider.cty` is designed for seamless interoperability with HashiCorp's Terraform ecosystem. This enables Python-based Terraform providers, state manipulation tools, and configuration validators that work natively with Terraform's type system.

## Overview

Terraform uses the `go-cty` type system internally for all type checking and value handling. `pyvider.cty` implements the same type system in Python with full cross-language compatibility, allowing you to:

- **Build Terraform Providers in Python**: Create custom providers using the Terraform Plugin Framework
- **Parse Terraform Type Strings**: Convert Terraform type syntax to pyvider.cty types
- **Exchange Data with Terraform**: Use MessagePack for binary-compatible serialization
- **Validate Terraform Configurations**: Type-check variables, resources, and modules
- **Manipulate Terraform State**: Read and modify state files safely

## Type String Parsing

Terraform represents types as strings like `list(string)` or `object({name=string})`. The `parse_tf_type_to_ctytype` function converts these to pyvider.cty types.

### Basic Type Parsing

```python
from pyvider.cty.parser import parse_tf_type_to_ctytype

# Primitive types
string_type = parse_tf_type_to_ctytype("string")
number_type = parse_tf_type_to_ctytype("number")
bool_type = parse_tf_type_to_ctytype("bool")

# Collection types
list_type = parse_tf_type_to_ctytype("list(string)")
map_type = parse_tf_type_to_ctytype("map(number)")
set_type = parse_tf_type_to_ctytype("set(string)")
```

### Complex Type Parsing

```python
# Object types
person_type = parse_tf_type_to_ctytype("""
    object({
        name = string,
        age = number,
        active = bool
    })
""")

# Nested collections
nested_type = parse_tf_type_to_ctytype("""
    list(object({
        id = string,
        tags = map(string)
    }))
""")

# Tuple types
tuple_type = parse_tf_type_to_ctytype("tuple([string, number, bool])")
```

### Alternative Format: JSON Arrays

Terraform also represents types as JSON arrays:

```python
# ["list", "string"] format
list_type = parse_tf_type_to_ctytype(["list", "string"])

# ["object", {...}] format
object_type = parse_tf_type_to_ctytype([
    "object",
    {
        "name": "string",
        "age": "number"
    }
])

# Verify equivalence
from pyvider.cty import CtyList, CtyString

assert list_type == CtyList(element_type=CtyString())
```

## MessagePack Serialization

Terraform uses MessagePack for efficient binary serialization of cty values. `pyvider.cty` provides full compatibility.

### Cross-Language Exchange

```python
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack
from pyvider.cty import CtyObject, CtyString, CtyNumber

# Define schema
schema = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    }
)

# Create value
value = schema.validate({"name": "Alice", "age": 30})

# Serialize to MessagePack (Terraform-compatible)
msgpack_bytes = cty_to_msgpack(value, schema)

# This binary data can be:
# - Sent to a Terraform provider written in Go
# - Stored in Terraform state files
# - Exchanged with any go-cty application

# Deserialize back
restored = cty_from_msgpack(msgpack_bytes, schema)
assert restored['name'].raw_value == "Alice"
```

### Interop with Go Providers

```python
# Python provider sends data to Terraform
def create_resource(config):
    """Create resource and return state as MessagePack."""
    # Validate configuration
    validated_config = resource_schema.validate(config)

    # Perform resource creation...
    resource_state = {
        "id": "res-12345",
        "name": validated_config['name'].raw_value,
        "status": "active"
    }

    # Serialize state for Terraform
    state_value = state_schema.validate(resource_state)
    return cty_to_msgpack(state_value, state_schema)

# Terraform/Go can deserialize this directly:
# state, err := msgpack.Unmarshal(pythonBytes, stateSchema)
```

## Terraform Provider Development

### Provider Schema Definition

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyBool, CtyMap

# Define provider configuration schema
provider_config_schema = CtyObject(
    attribute_types={
        "api_token": CtyString(),
        "endpoint": CtyString(),
        "timeout": CtyNumber()
    },
    optional_attributes={"timeout"}
)

# Define resource schemas
resource_schemas = {
    "example_server": CtyObject(
        attribute_types={
            "name": CtyString(),
            "instance_type": CtyString(),
            "region": CtyString(),
            "enabled": CtyBool(),
            "tags": CtyMap(element_type=CtyString())
        },
        optional_attributes={"enabled", "tags"}
    ),

    "example_network": CtyObject(
        attribute_types={
            "cidr": CtyString(),
            "name": CtyString(),
            "subnet_count": CtyNumber()
        }
    )
}
```

### Resource CRUD Operations

```python
class ExampleServerResource:
    """Example Terraform resource implementation."""

    def __init__(self, schema):
        self.schema = schema

    def create(self, config_msgpack):
        """Create resource from Terraform config."""
        # Deserialize config from Terraform
        config = cty_from_msgpack(config_msgpack, self.schema)

        # Extract values
        name = config['name'].raw_value
        instance_type = config['instance_type'].raw_value
        region = config['region'].raw_value

        # Create resource (API calls, etc.)
        resource_id = self._api_create(name, instance_type, region)

        # Build state
        state_data = {
            "name": name,
            "instance_type": instance_type,
            "region": region,
            "enabled": config['enabled'].raw_value if not config['enabled'].is_null else True,
            "tags": config['tags'].raw_value if not config['tags'].is_null else {}
        }

        # Return state as MessagePack
        state_value = self.schema.validate(state_data)
        return cty_to_msgpack(state_value, self.schema)

    def read(self, state_msgpack):
        """Read current resource state."""
        # Deserialize current state
        state = cty_from_msgpack(state_msgpack, self.schema)

        # Fetch current state from API
        current_data = self._api_read(state['name'].raw_value)

        # Validate and serialize
        current_value = self.schema.validate(current_data)
        return cty_to_msgpack(current_value, self.schema)

    def update(self, state_msgpack, config_msgpack):
        """Update resource."""
        state = cty_from_msgpack(state_msgpack, self.schema)
        config = cty_from_msgpack(config_msgpack, self.schema)

        # Determine what changed and update
        # ...

        return self._build_state()

    def delete(self, state_msgpack):
        """Delete resource."""
        state = cty_from_msgpack(state_msgpack, self.schema)
        resource_id = state['name'].raw_value
        self._api_delete(resource_id)
```

### Validation Functions

```python
def validate_cidr_block(value):
    """Custom validation function for CIDR blocks."""
    import ipaddress

    if value.is_null or value.is_unknown:
        return  # Allow null/unknown values

    cidr_string = value.raw_value
    try:
        ipaddress.ip_network(cidr_string)
    except ValueError as e:
        from pyvider.cty.exceptions import CtyValidationError
        raise CtyValidationError(f"Invalid CIDR block: {e}")

# Use in resource validation
def validate_network_config(config):
    """Validate network resource configuration."""
    validated = network_schema.validate(config)

    # Additional custom validation
    validate_cidr_block(validated['cidr'])

    return validated
```

## Working with Terraform State

### Reading State Files

```python
import json
from pyvider.cty.codec import cty_from_msgpack

def read_terraform_state(state_file_path):
    """Read and parse Terraform state file."""
    with open(state_file_path) as f:
        state = json.load(f)

    resources = []
    for resource in state.get("resources", []):
        resource_type = resource["type"]
        resource_mode = resource["mode"]

        for instance in resource.get("instances", []):
            # State is stored as attributes dict
            attributes = instance.get("attributes", {})

            # If you have the schema, validate
            if resource_type in resource_schemas:
                schema = resource_schemas[resource_type]
                validated = schema.validate(attributes)
                resources.append({
                    "type": resource_type,
                    "mode": resource_mode,
                    "value": validated
                })
            else:
                resources.append({
                    "type": resource_type,
                    "mode": resource_mode,
                    "attributes": attributes
                })

    return resources
```

### Modifying State

```python
def update_resource_state(state_file, resource_address, new_attributes):
    """Update a specific resource in state file."""
    with open(state_file) as f:
        state = json.load(f)

    # Find resource
    for resource in state.get("resources", []):
        if resource["type"] == resource_address:
            for instance in resource.get("instances", []):
                # Validate new attributes
                schema = resource_schemas[resource["type"]]
                validated = schema.validate(new_attributes)

                # Update attributes
                instance["attributes"] = new_attributes

    # Write back
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
```

## Variable Validation

### Input Variable Types

```python
# Terraform variable definition:
# variable "vpc_config" {
#   type = object({
#     cidr = string
#     name = string
#     enable_dns = bool
#   })
# }

vpc_var_type = parse_tf_type_to_ctytype("""
    object({
        cidr = string,
        name = string,
        enable_dns = bool
    })
""")

# Validate variable value
vpc_value = vpc_var_type.validate({
    "cidr": "10.0.0.0/16",
    "name": "main-vpc",
    "enable_dns": True
})

# Access validated values
print(vpc_value['cidr'].raw_value)  # "10.0.0.0/16"
```

### Default Values and Null

```python
# Variable with optional attributes
config_type = CtyObject(
    attribute_types={
        "required_field": CtyString(),
        "optional_field": CtyString(),
        "with_default": CtyNumber()
    },
    optional_attributes={"optional_field", "with_default"}
)

# Minimal config
minimal = config_type.validate({"required_field": "value"})

# Optional fields are null
assert minimal['optional_field'].is_null
assert minimal['with_default'].is_null

# Apply defaults
def apply_defaults(value, defaults):
    """Apply default values to null attributes."""
    result = {}
    for attr_name in value.type.attribute_types.keys():
        attr_value = value[attr_name]
        if attr_value.is_null and attr_name in defaults:
            result[attr_name] = defaults[attr_name]
        else:
            result[attr_name] = attr_value.raw_value if not attr_value.is_null else None
    return result

defaults = {"with_default": 42}
final_config = apply_defaults(minimal, defaults)
# {"required_field": "value", "optional_field": None, "with_default": 42}
```

## Module Integration

### Module Input Validation

```python
# Define module interface
module_inputs = {
    "network": parse_tf_type_to_ctytype("""
        object({
            vpc_cidr = string,
            availability_zones = list(string)
        })
    """),
    "compute": parse_tf_type_to_ctytype("""
        object({
            instance_count = number,
            instance_type = string
        })
    """)
}

def validate_module_inputs(inputs):
    """Validate all module inputs."""
    validated = {}
    for input_name, input_schema in module_inputs.items():
        if input_name not in inputs:
            raise ValueError(f"Missing required input: {input_name}")
        validated[input_name] = input_schema.validate(inputs[input_name])
    return validated

# Usage
user_inputs = {
    "network": {
        "vpc_cidr": "10.0.0.0/16",
        "availability_zones": ["us-east-1a", "us-east-1b"]
    },
    "compute": {
        "instance_count": 3,
        "instance_type": "t2.micro"
    }
}

validated_inputs = validate_module_inputs(user_inputs)
```

### Module Output Types

```python
# Define output schema
module_outputs = {
    "vpc_id": CtyString(),
    "subnet_ids": CtyList(element_type=CtyString()),
    "instance_ips": CtyList(element_type=CtyString())
}

def validate_module_outputs(outputs):
    """Validate module outputs match expected types."""
    validated = {}
    for output_name, output_type in module_outputs.items():
        if output_name in outputs:
            validated[output_name] = output_type.validate(outputs[output_name])
    return validated
```

## Unknown and Null Values

Terraform uses special "unknown" values during planning when values aren't computed yet.

### Handling Unknown Values

```python
from pyvider.cty.values import CtyValue

# Create unknown value
unknown_string = CtyValue.unknown(CtyString())

# Check for unknown
if unknown_string.is_unknown:
    print("Value will be computed during apply")

# Validate data with unknown values
config_with_unknown = {
    "name": "server-1",
    "ip_address": None  # Will be unknown
}

# Create schema allowing unknowns
schema = CtyObject(
    attribute_types={
        "name": CtyString(),
        "ip_address": CtyString()
    }
)

# For unknowns, use CtyValue.unknown
from pyvider.cty import CtyObject, CtyString

validated = CtyObject(
    attribute_types={
        "name": CtyString(),
        "ip_address": CtyString()
    }
).validate({
    "name": "server-1",
    "ip_address": None  # Becomes null
})

# To create actual unknowns:
unknown_val = CtyValue.unknown(schema)
```

### Null vs Unknown

```python
# Null: value is explicitly absent
null_value = CtyValue.null(CtyString())
assert null_value.is_null

# Unknown: value exists but isn't computed yet
unknown_value = CtyValue.unknown(CtyString())
assert unknown_value.is_unknown

# Different semantics in Terraform:
# - Null means "no value provided"
# - Unknown means "value not yet computed"
```

## Marks and Sensitive Data

Terraform uses marks to track sensitive data.

### Sensitive Value Handling

```python
from pyvider.cty.marks import CtyMark

# Create sensitive mark
sensitive = CtyMark("sensitive")

# Mark a value as sensitive
password = CtyString().validate("super-secret")
marked_password = password.with_marks({sensitive})

# Check if sensitive
if sensitive in marked_password.marks:
    print("This value is sensitive - do not log!")

# Remove all marks (when safe, returns tuple)
unmarked, removed_marks = marked_password.unmark()
```

### Provider Mark Handling

```python
def handle_sensitive_config(config_value):
    """Process configuration with sensitive values."""
    sensitive_mark = CtyMark("sensitive")

    # Identify sensitive fields
    for attr_name in config_value.type.attribute_types.keys():
        attr_value = config_value[attr_name]

        if sensitive_mark in attr_value.marks:
            # Handle sensitive value - don't log
            print(f"{attr_name}: <sensitive>")
        else:
            # Safe to log
            print(f"{attr_name}: {attr_value.raw_value}")
```

## Best Practices

### 1. Cache Parsed Schemas

```python
# Bad: Parse on every validation
for config in configs:
    schema = parse_tf_type_to_ctytype("object({...})")
    schema.validate(config)

# Good: Parse once, reuse
schema = parse_tf_type_to_ctytype("object({...})")
for config in configs:
    schema.validate(config)
```

### 2. Handle Optional Attributes

```python
# Always specify optional attributes
schema = CtyObject(
    attribute_types={
        "required": CtyString(),
        "optional": CtyString()
    },
    optional_attributes={"optional"}  # Explicit!
)

# Check for null before accessing
value = schema.validate({"required": "value"})
if not value['optional'].is_null:
    print(value['optional'].raw_value)
```

### 3. Validate Early

```python
# Validate at provider boundaries
def create_resource(config_dict):
    # Validate immediately
    config = resource_schema.validate(config_dict)

    # Now work with type-safe values
    name = config['name'].raw_value
    # ...
```

### 4. Use MessagePack for Interop

```python
# Use MessagePack for all Terraform communication
def send_to_terraform(value, schema):
    return cty_to_msgpack(value, schema)

def receive_from_terraform(msgpack_data, schema):
    return cty_from_msgpack(msgpack_data, schema)
```

### 5. Test with Real Terraform Data

```python
# Test your provider with actual Terraform
def test_resource_creation():
    # Load actual Terraform config
    with open("terraform.tfvars.json") as f:
        config = json.load(f)

    # Validate
    validated = resource_schema.validate(config["resource_config"])

    # Test CRUD operations
    state = create_resource(validated)
    # ...
```

## Common Patterns

### Configuration Validator

```python
class TerraformValidator:
    """Validate Terraform configurations."""

    def __init__(self):
        self.schemas = {}

    def register(self, name, type_string):
        """Register a schema."""
        self.schemas[name] = parse_tf_type_to_ctytype(type_string)

    def validate(self, name, data):
        """Validate data against schema."""
        return self.schemas[name].validate(data)

# Usage
validator = TerraformValidator()
validator.register("vpc", "object({cidr=string,name=string})")
vpc = validator.validate("vpc", {"cidr": "10.0.0.0/16", "name": "main"})
```

### Type-Safe State Manager

```python
class StateManager:
    """Manage Terraform state with type safety."""

    def __init__(self, state_file, schemas):
        self.state_file = state_file
        self.schemas = schemas
        self.state = self._load_state()

    def _load_state(self):
        with open(self.state_file) as f:
            return json.load(f)

    def get_resource(self, resource_type, index=0):
        """Get typed resource from state."""
        for resource in self.state.get("resources", []):
            if resource["type"] == resource_type:
                attrs = resource["instances"][index]["attributes"]
                schema = self.schemas[resource_type]
                return schema.validate(attrs)
        return None

    def update_resource(self, resource_type, new_attrs, index=0):
        """Update resource with validation."""
        schema = self.schemas[resource_type]
        validated = schema.validate(new_attrs)

        for resource in self.state.get("resources", []):
            if resource["type"] == resource_type:
                resource["instances"][index]["attributes"] = new_attrs

        self._save_state()

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
```

## Further Reading

- **[How to Work with Terraform](../../how-to/work-with-terraform.md)** - Practical examples and patterns
- **[go-cty Comparison](../../reference/go-cty-comparison.md)** - Detailed comparison with Go implementation
- **[Serialization](serialization.md)** - MessagePack encoding/decoding details
- **[Migrate from go-cty](../../how-to/migrate-from-go-cty.md)** - Migration guide for Go developers
