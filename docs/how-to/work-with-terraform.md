# How to Work with Terraform Types

This guide shows you how to use pyvider.cty with Terraform, including parsing Terraform type strings and working with Terraform data structures.

## Parsing Terraform Type Strings

Terraform uses type strings like `list(string)` or `object({name=string,age=number})`. pyvider.cty can parse these:

```python
from pyvider.cty.parser import parse_tf_type_to_ctytype

# Parse simple types
string_type = parse_tf_type_to_ctytype("string")
number_type = parse_tf_type_to_ctytype("number")
bool_type = parse_tf_type_to_ctytype("bool")

# Parse collection types
list_type = parse_tf_type_to_ctytype("list(string)")
map_type = parse_tf_type_to_ctytype("map(number)")
set_type = parse_tf_type_to_ctytype("set(string)")

# Parse complex object types
object_type = parse_tf_type_to_ctytype(
    "object({name=string,age=number,active=bool})"
)

# Use the parsed type
data = {"name": "Alice", "age": 30, "active": True}
value = object_type.validate(data)
```

## Common Terraform Patterns

### Variable Validation

```python
from pyvider.cty.parser import parse_tf_type_to_ctytype

def validate_terraform_variable(var_type_string, var_value):
    """Validate a Terraform variable against its type."""
    try:
        var_type = parse_tf_type_to_ctytype(var_type_string)
        return var_type.validate(var_value)
    except Exception as e:
        raise ValueError(f"Variable validation failed: {e}")

# Example
vpc_config_type = "object({cidr=string,subnets=list(string)})"
vpc_config_data = {
    "cidr": "10.0.0.0/16",
    "subnets": ["10.0.1.0/24", "10.0.2.0/24"]
}

validated = validate_terraform_variable(vpc_config_type, vpc_config_data)
```

### Resource Schema

```python
# Define a resource schema matching Terraform
resource_schema = parse_tf_type_to_ctytype("""
object({
  name = string,
  instance_type = string,
  ami = string,
  tags = map(string)
})
""")

# Validate resource configuration
resource_config = {
    "name": "web-server",
    "instance_type": "t2.micro",
    "ami": "ami-12345",
    "tags": {
        "Environment": "prod",
        "Owner": "ops-team"
    }
}

resource_value = resource_schema.validate(resource_config)
```

## Working with Terraform Modules

### Module Input Variables

```python
from pyvider.cty.parser import parse_tf_type_to_ctytype

# Parse module variable types
module_vars = {
    "vpc_cidr": parse_tf_type_to_ctytype("string"),
    "availability_zones": parse_tf_type_to_ctytype("list(string)"),
    "enable_nat": parse_tf_type_to_ctytype("bool"),
    "tags": parse_tf_type_to_ctytype("map(string)")
}

# Validate module inputs
module_inputs = {
    "vpc_cidr": "10.0.0.0/16",
    "availability_zones": ["us-east-1a", "us-east-1b"],
    "enable_nat": True,
    "tags": {"Project": "demo"}
}

validated_inputs = {}
for var_name, var_type in module_vars.items():
    validated_inputs[var_name] = var_type.validate(module_inputs[var_name])
```

### Module Outputs

```python
# Define output types
output_schema = parse_tf_type_to_ctytype("""
object({
  vpc_id = string,
  subnet_ids = list(string),
  nat_gateway_id = string
})
""")

# Validate module outputs
module_outputs = {
    "vpc_id": "vpc-12345",
    "subnet_ids": ["subnet-111", "subnet-222"],
    "nat_gateway_id": "nat-99999"
}

validated_outputs = output_schema.validate(module_outputs)
```

## Complex Terraform Types

### Nested Objects

```python
# Parse complex nested structure
nested_type = parse_tf_type_to_ctytype("""
object({
  network = object({
    vpc_id = string,
    subnets = list(object({
      id = string,
      cidr = string,
      az = string
    }))
  }),
  compute = object({
    instance_type = string,
    count = number
  })
})
""")

# Validate nested data
infrastructure = {
    "network": {
        "vpc_id": "vpc-12345",
        "subnets": [
            {"id": "subnet-1", "cidr": "10.0.1.0/24", "az": "us-east-1a"},
            {"id": "subnet-2", "cidr": "10.0.2.0/24", "az": "us-east-1b"}
        ]
    },
    "compute": {
        "instance_type": "t2.micro",
        "count": 3
    }
}

infra_value = nested_type.validate(infrastructure)
```

### Optional Attributes

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyBool

# Define type with optional fields (Terraform style)
instance_type = CtyObject(
    attribute_types={
        "ami": CtyString(),
        "instance_type": CtyString(),
        "key_name": CtyString(),
        "monitoring": CtyBool(),
        "user_data": CtyString()
    },
    optional_attributes={"key_name", "monitoring", "user_data"}
)

# Valid with only required fields
minimal_instance = instance_type.validate({
    "ami": "ami-12345",
    "instance_type": "t2.micro"
})

# Optional fields are null
assert minimal_instance['key_name'].is_null
```

## Provider Development

### Resource State

```python
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

# Define resource state schema
state_schema = parse_tf_type_to_ctytype("""
object({
  id = string,
  name = string,
  status = string,
  created_at = string
})
""")

# Create and serialize state
state_data = {
    "id": "resource-123",
    "name": "my-resource",
    "status": "active",
    "created_at": "2025-01-24T10:00:00Z"
}

state_value = state_schema.validate(state_data)

# Serialize for Terraform
state_msgpack = cty_to_msgpack(state_value, state_schema)

# Later, deserialize
restored_state = cty_from_msgpack(state_msgpack, state_schema)
```

### Schema Definition

```python
# Define provider schema
provider_schema = {
    "resources": {
        "example_instance": parse_tf_type_to_ctytype("""
            object({
              name = string,
              size = string,
              region = string,
              tags = map(string)
            })
        """),
        "example_network": parse_tf_type_to_ctytype("""
            object({
              cidr = string,
              name = string
            })
        """)
    }
}

def validate_resource(resource_type, config):
    """Validate resource configuration."""
    if resource_type not in provider_schema["resources"]:
        raise ValueError(f"Unknown resource type: {resource_type}")

    schema = provider_schema["resources"][resource_type]
    return schema.validate(config)
```

## Handling Terraform Data

### Reading terraform.tfstate

```python
import json

def load_terraform_state(state_file):
    """Load and validate Terraform state file."""
    with open(state_file) as f:
        state = json.load(f)

    # Extract resources
    resources = []
    for resource in state.get("resources", []):
        # Parse resource schema from type
        resource_type = resource["type"]
        instances = resource.get("instances", [])

        for instance in instances:
            # Validate instance attributes
            attributes = instance.get("attributes", {})
            resources.append({
                "type": resource_type,
                "attributes": attributes
            })

    return resources
```

### Working with HCL

```python
# While pyvider.cty doesn't parse HCL directly,
# you can work with the parsed structures

# After parsing HCL to Python dict (using python-hcl2 or similar):
hcl_data = {
    "resource": {
        "aws_instance": {
            "web": {
                "ami": "ami-12345",
                "instance_type": "t2.micro",
                "tags": {"Name": "web-server"}
            }
        }
    }
}

# Extract and validate resource config
resource_config = hcl_data["resource"]["aws_instance"]["web"]
instance_schema = parse_tf_type_to_ctytype("""
    object({
      ami = string,
      instance_type = string,
      tags = map(string)
    })
""")

validated = instance_schema.validate(resource_config)
```

## Best Practices

1. **Parse type strings once**: Cache parsed type schemas
2. **Validate early**: Check types before Terraform execution
3. **Use MessagePack**: For Terraform provider communication
4. **Handle optional fields**: Many Terraform attributes are optional
5. **Test with real data**: Use actual Terraform configs for testing
6. **Document schemas**: Keep schema documentation up to date

## Common Patterns

### Configuration Validator

```python
class TerraformConfigValidator:
    """Validate Terraform configurations."""

    def __init__(self):
        self.schemas = {}

    def register_schema(self, name, type_string):
        """Register a schema for validation."""
        self.schemas[name] = parse_tf_type_to_ctytype(type_string)

    def validate(self, schema_name, data):
        """Validate data against a registered schema."""
        if schema_name not in self.schemas:
            raise ValueError(f"Unknown schema: {schema_name}")

        schema = self.schemas[schema_name]
        return schema.validate(data)

# Usage
validator = TerraformConfigValidator()
validator.register_schema("vpc", "object({cidr=string,name=string})")
validator.register_schema("subnet", "object({cidr=string,vpc_id=string})")

vpc_config = validator.validate("vpc", {
    "cidr": "10.0.0.0/16",
    "name": "main-vpc"
})
```

### Type Introspection

```python
def describe_terraform_type(type_string):
    """Describe a Terraform type in detail."""
    cty_type = parse_tf_type_to_ctytype(type_string)

    # Get type information
    info = {
        "type_name": type(cty_type).__name__,
        "is_collection": hasattr(cty_type, 'element_type'),
        "is_structural": hasattr(cty_type, 'attribute_types')
    }

    if info["is_structural"]:
        info["attributes"] = list(cty_type.attribute_types.keys())

    return info

# Usage
type_info = describe_terraform_type("object({name=string,count=number})")
print(type_info)
```

## Next Steps

- [Validate complex data](validate-data.md)
- [Serialize values](serialize-values.md)
- [Learn about advanced features](../user-guide/advanced/terraform-interop.md)
- [Migrate from go-cty](migrate-from-go-cty.md)
