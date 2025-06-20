#!/usr/bin/env python3
# example-11-complex-schema-fixed.py

from decimal import Decimal

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.conversion import WireFormatType, marshal, unmarshal
from pyvider.cty.exceptions import AttributePathError, CtyValidationError
from pyvider.cty.path import CtyPath

# Define a complex infrastructure schema
network_interface_type = CtyObject(
    attribute_types={
        "id": CtyString(),
        "type": CtyString(),
        "ip_addresses": CtyList(element_type=CtyString()),
        "security_groups": CtyList(element_type=CtyString()),
        "is_public": CtyBool(),
    }
)

volume_type = CtyObject(
    attribute_types={
        "id": CtyString(),
        "size": CtyNumber(),
        "type": CtyString(),
        "iops": CtyNumber(),
        "encrypted": CtyBool(),
        "kms_key_id": CtyString(),
    },
    optional_attributes=frozenset(["iops", "kms_key_id"]),
)

# FIXED: Replace nested CtyDynamic with specific structured types
performance_metrics_type = CtyObject(
    attribute_types={
        "cpu_utilization": CtyNumber(),
        "memory_usage": CtyNumber(),
        "disk_io": CtyList(element_type=CtyNumber()),
    }
)

metadata_type = CtyObject(
    attribute_types={
        "last_patched": CtyString(),
        "compliance_status": CtyBool(),
        "performance_metrics": performance_metrics_type,
    }
)

instance_type = CtyObject(
    attribute_types={
        "id": CtyString(),
        "name": CtyString(),
        "instance_type": CtyString(),
        "state": CtyString(),
        "launched_at": CtyString(),
        "network_interfaces": CtyList(element_type=network_interface_type),
        "volumes": CtyList(element_type=volume_type),
        "tags": CtyMap(key_type=CtyString(), value_type=CtyString()),
        "metadata": metadata_type,  # FIXED: Use structured type instead of CtyDynamic
        "coordinates": CtyTuple(element_types=(CtyNumber(), CtyNumber())),
    }
)

# Create a complex test value
try:
    instance_data = {
        "id": "i-0123456789abcdef0",
        "name": "prod-app-server-01",
        "instance_type": "m5.large",
        "state": "running",
        "launched_at": "2025-03-01T12:00:00Z",
        "network_interfaces": [
            {
                "id": "eni-0123456789abcdef0",
                "type": "primary",
                "ip_addresses": ["10.0.1.10", "10.0.1.11"],
                "security_groups": ["sg-web", "sg-app"],
                "is_public": True,
            },
            {
                "id": "eni-0123456789abcdef1",
                "type": "secondary",
                "ip_addresses": ["10.0.2.10"],
                "security_groups": ["sg-database"],
                "is_public": False,
            },
        ],
        "volumes": [
            {
                "id": "vol-0123456789abcdef0",
                "size": 100,
                "type": "gp3",
                "encrypted": True,
                "kms_key_id": "arn:aws:kms:us-west-2:111122223333:key/abcd1234",
            },
            {
                "id": "vol-0123456789abcdef1",
                "size": 500,
                "type": "io2",
                "iops": 5000,
                "encrypted": True,
            },
        ],
        "tags": {"Environment": "Production", "Owner": "DevOps", "Project": "MainApp"},
        "metadata": {
            "last_patched": "2025-02-15",
            "compliance_status": True,
            "performance_metrics": {
                "cpu_utilization": Decimal("35.7"),
                "memory_usage": Decimal("42.3"),
                "disk_io": [123.4, 456.7, 789.0],
            },
        },
        "coordinates": (37.7749, -122.4194),
    }

    # Validate the instance data
    print("Validating complex instance schema...")
    instance_val = instance_type.validate(instance_data)
    print("✅ Successfully validated complex instance schema")

    # Serialize using marshal function
    print("\nSerializing to JSON...")
    serialized = marshal(instance_val, format_kind=WireFormatType.JSON)
    print(f"✅ Serialized size: {len(serialized)} bytes")
    
    # Pretty print a portion of the JSON
    import json
    json_data = json.loads(serialized.decode())
    print(f"Sample JSON structure: {json.dumps(json_data, indent=2)[:500]}...")

    # Deserialize using unmarshal function
    print("\nDeserializing from JSON...")
    deserialized = unmarshal(
        serialized, format_kind=WireFormatType.JSON, expected_type=instance_type
    )
    if not deserialized.is_null and not deserialized.is_unknown:
        print(f"✅ Deserialized instance ID: {deserialized['id'].value}")
    else:
        print("❌ Deserialized value is null or unknown.")

    # Path Navigation
    print("\n--- Path Navigation Examples ---")
    
    # 1. Simple attribute access
    name_path = CtyPath.get_attr("name")
    name_val = name_path.apply_path(instance_val)
    print(f"Instance name: {name_val.value}")
    
    # 2. Nested object access
    cpu_path = (
        CtyPath.get_attr("metadata")
        .child("performance_metrics")
        .child("cpu_utilization")
    )
    cpu_val = cpu_path.apply_path(instance_val)
    print(f"CPU Utilization: {cpu_val.value}%")
    
    # 3. List element access
    first_nic_path = CtyPath.get_attr("network_interfaces").index_step(0)
    first_nic = first_nic_path.apply_path(instance_val)
    print(f"First NIC ID: {first_nic['id'].value}")
    
    # 4. Complex path through list to nested attribute
    primary_ip_path = (
        CtyPath.get_attr("network_interfaces")
        .index_step(0)
        .child("ip_addresses")
        .index_step(0)
    )
    primary_ip = primary_ip_path.apply_path(instance_val)
    print(f"Primary IP: {primary_ip.value}")
    
    # 5. Map access with key_step
    env_tag_path = CtyPath.get_attr("tags").key_step("Environment")
    env_tag = env_tag_path.apply_path(instance_val)
    print(f"Environment tag: {env_tag.value}")

    print("\n✅ All operations completed successfully!")

except CtyValidationError as e:
    print(f"❌ Validation error: {e}")
except AttributePathError as e:
    print(f"❌ Path navigation error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
