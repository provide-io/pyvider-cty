#!/usr/bin/env python3
# example-tfstate-handler.py
"""
Example demonstrating how to parse and work with Terraform state files using pyvider.cty.
This shows proper type annotation and handling of complex nested structures.
"""

import json
from pathlib import Path
from typing import Any

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValue,
)
from pyvider.cty.conversion import WireFormatType, marshal, unmarshal
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.path import CtyPath


# Define Terraform state schema types
resource_instance_type = CtyObject(
    attribute_types={
        "schema_version": CtyNumber(),
        "attributes": CtyMap(key_type=CtyString(), value_type=CtyDynamic()),
        "sensitive_attributes": CtyList(element_type=CtyDynamic()),
        "private": CtyString(),
        "dependencies": CtyList(element_type=CtyString()),
    },
    optional_attributes=frozenset(["sensitive_attributes", "private", "dependencies"]),
)

resource_type = CtyObject(
    attribute_types={
        "mode": CtyString(),
        "type": CtyString(),
        "name": CtyString(),
        "provider": CtyString(),
        "instances": CtyList(element_type=resource_instance_type),
    }
)

output_type = CtyObject(
    attribute_types={
        "value": CtyDynamic(),
        "type": CtyString(),
        "sensitive": CtyBool(),
    },
    optional_attributes=frozenset(["sensitive"]),
)

terraform_state_type = CtyObject(
    attribute_types={
        "version": CtyNumber(),
        "terraform_version": CtyString(),
        "serial": CtyNumber(),
        "lineage": CtyString(),
        "outputs": CtyMap(key_type=CtyString(), value_type=output_type),
        "resources": CtyList(element_type=resource_type),
        "check_results": CtyDynamic(),  # Optional, complex structure
    },
    optional_attributes=frozenset(["outputs", "check_results"]),
)


def load_tfstate(file_path: Path) -> dict[str, Any]:
    """Load a Terraform state file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def analyze_tfstate(tfstate_data: dict[str, Any]) -> None:
    """Analyze and display information from a Terraform state file."""
    try:
        # Validate the state file against our schema
        print("🔍 Validating Terraform state file...")
        tfstate_val = terraform_state_type.validate(tfstate_data)
        print("✅ State file is valid!")
        
        # Basic information
        print(f"\n📊 State File Information:")
        print(f"  Version: {tfstate_val['version'].value}")
        print(f"  Terraform Version: {tfstate_val['terraform_version'].value}")
        print(f"  Serial: {tfstate_val['serial'].value}")
        print(f"  Lineage: {tfstate_val['lineage'].value}")
        
        # Count resources
        resources = tfstate_val['resources']
        if not resources.is_null:
            print(f"  Total Resources: {len(resources.value)}")
        
        # List outputs if any
        outputs = tfstate_val['outputs']
        if not outputs.is_null and len(outputs.value) > 0:
            print(f"\n📤 Outputs ({len(outputs.value)}):")
            for name, output in outputs.value.items():
                sensitive = output['sensitive'].value if not output['sensitive'].is_null else False
                if sensitive:
                    print(f"  - {name}: <sensitive>")
                else:
                    print(f"  - {name}: {output['value'].value}")
        
        # Analyze resources
        if not resources.is_null and len(resources.value) > 0:
            print(f"\n🔧 Resources:")
            
            # Group resources by type
            resource_types: dict[str, list[CtyValue]] = {}
            for resource in resources.value:
                res_type = resource['type'].value
                if res_type not in resource_types:
                    resource_types[res_type] = []
                resource_types[res_type].append(resource)
            
            # Display resource summary
            for res_type, res_list in resource_types.items():
                print(f"\n  {res_type} ({len(res_list)}):")
                for resource in res_list:
                    mode = resource['mode'].value
                    name = resource['name'].value
                    provider = resource['provider'].value
                    instances = resource['instances']
                    instance_count = len(instances.value) if not instances.is_null else 0
                    
                    print(f"    - {mode}.{res_type}.{name}")
                    print(f"      Provider: {provider}")
                    print(f"      Instances: {instance_count}")
                    
                    # Show first instance attributes sample
                    if instance_count > 0:
                        first_instance = instances.value[0]
                        attrs = first_instance['attributes']
                        if not attrs.is_null and len(attrs.value) > 0:
                            print(f"      Sample attributes: {list(attrs.value.keys())[:5]}...")
        
        # Demonstrate path navigation
        print("\n🗺️ Path Navigation Examples:")
        
        # Get Terraform version using path
        tf_version_path = CtyPath.get_attr("terraform_version")
        tf_version = tf_version_path.apply_path(tfstate_val)
        print(f"  Terraform version via path: {tf_version.value}")
        
        # Get first resource name if exists
        if not resources.is_null and len(resources.value) > 0:
            first_res_name_path = (
                CtyPath.get_attr("resources")
                .index_step(0)
                .child("name")
            )
            first_res_name = first_res_name_path.apply_path(tfstate_val)
            print(f"  First resource name: {first_res_name.value}")
        
        # Serialize and check round-trip
        print("\n🔄 Testing serialization round-trip...")
        serialized = marshal(tfstate_val, format_kind=WireFormatType.JSON)
        deserialized = unmarshal(serialized, format_kind=WireFormatType.JSON, expected_type=terraform_state_type)
        
        # Verify round-trip
        if deserialized['serial'].value == tfstate_val['serial'].value:
            print("✅ Round-trip serialization successful!")
        else:
            print("❌ Round-trip serialization failed!")
            
    except CtyValidationError as e:
        print(f"❌ Validation error: {e}")
        print("   This might indicate the state file has unexpected structure.")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def create_sample_tfstate() -> dict[str, Any]:
    """Create a sample Terraform state for testing."""
    return {
        "version": 4,
        "terraform_version": "1.5.0",
        "serial": 42,
        "lineage": "12345678-1234-5678-1234-567812345678",
        "outputs": {
            "instance_ip": {
                "value": "10.0.1.100",
                "type": "string",
                "sensitive": False
            },
            "database_password": {
                "value": "super-secret",
                "type": "string", 
                "sensitive": True
            }
        },
        "resources": [
            {
                "mode": "managed",
                "type": "aws_instance",
                "name": "web",
                "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
                "instances": [
                    {
                        "schema_version": 1,
                        "attributes": {
                            "id": "i-1234567890abcdef0",
                            "instance_type": "t3.micro",
                            "public_ip": "54.123.45.67",
                            "private_ip": "10.0.1.100",
                            "tags": {
                                "Name": "WebServer",
                                "Environment": "Production"
                            }
                        },
                        "dependencies": [
                            "aws_security_group.web",
                            "aws_subnet.public"
                        ]
                    }
                ]
            },
            {
                "mode": "managed",
                "type": "aws_security_group",
                "name": "web",
                "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
                "instances": [
                    {
                        "schema_version": 1,
                        "attributes": {
                            "id": "sg-1234567890abcdef0",
                            "name": "web-security-group",
                            "description": "Security group for web servers",
                            "ingress": [
                                {
                                    "from_port": 80,
                                    "to_port": 80,
                                    "protocol": "tcp",
                                    "cidr_blocks": ["0.0.0.0/0"]
                                },
                                {
                                    "from_port": 443,
                                    "to_port": 443,
                                    "protocol": "tcp",
                                    "cidr_blocks": ["0.0.0.0/0"]
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


def main():
    """Main function to demonstrate tfstate handling."""
    print("🌟 Terraform State File Handler Example\n")
    
    # Option 1: Use a real tfstate file
    # tfstate_path = Path("terraform.tfstate")
    # if tfstate_path.exists():
    #     print(f"Loading state file: {tfstate_path}")
    #     tfstate_data = load_tfstate(tfstate_path)
    # else:
    #     print("No terraform.tfstate found, using sample data")
    #     tfstate_data = create_sample_tfstate()
    
    # Option 2: Use sample data for demonstration
    print("Using sample Terraform state data for demonstration...")
    tfstate_data = create_sample_tfstate()
    
    # Analyze the state
    analyze_tfstate(tfstate_data)
    
    print("\n✨ Example completed!")


if __name__ == "__main__":
    main()
