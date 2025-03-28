#!/usr/bin/env python3
# docs/examples/example-11-complex-schema.py

import asyncio
from decimal import Decimal
from typing import Dict, List, Any

from pyvider.cty import (
    CtyObject, CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtyDynamic, 
    CtyValue, CtyTuple
)
from pyvider.cty.encoding import serialize_with_type, deserialize_with_type
from pyvider.cty.path.path import Path
from pyvider.cty.exceptions import ValidationError, AttributePathError

# Define a complex infrastructure schema
network_interface_type = CtyObject(
    attribute_types={
        "id": CtyString(),
        "type": CtyString(),
        "ip_addresses": CtyList(element_type=CtyString()),
        "security_groups": CtyList(element_type=CtyString()),
        "is_public": CtyBool()
    }
)

volume_type = CtyObject(
    attribute_types={
        "id": CtyString(),
        "size": CtyNumber(),
        "type": CtyString(),
        "iops": CtyNumber(),
        "encrypted": CtyBool(),
        "kms_key_id": CtyString()
    },
    optional_attributes=frozenset(["iops", "kms_key_id"])
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
        "metadata": CtyMap(key_type=CtyString(), value_type=CtyDynamic()),
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
                "is_public": True
            },
            {
                "id": "eni-0123456789abcdef1",
                "type": "secondary",
                "ip_addresses": ["10.0.2.10"],
                "security_groups": ["sg-database"],
                "is_public": False
            }
        ],
        "volumes": [
            {
                "id": "vol-0123456789abcdef0",
                "size": 100,
                "type": "gp3",
                "encrypted": True,
                "kms_key_id": "arn:aws:kms:us-west-2:111122223333:key/abcd1234"
            },
            {
                "id": "vol-0123456789abcdef1",
                "size": 500,
                "type": "io2",
                "iops": 5000,
                "encrypted": True
            }
        ],
        "tags": {
            "Environment": "Production",
            "Owner": "DevOps",
            "Project": "MainApp"
        },
        "metadata": {
            "last_patched": "2025-02-15",
            "compliance_status": True,
            "performance_metrics": {
                "cpu_utilization": Decimal("35.7"),
                "memory_usage": Decimal("42.3"),
                "disk_io": [123.4, 456.7, 789.0]
            }
        },
        "coordinates": (37.7749, -122.4194)
    }

    # Validate the instance data
    validated = instance_type.validate(instance_data)
    instance_val = CtyValue(type_=instance_type, value=validated)
    print(f"Successfully validated complex instance schema")

    # Serialize and deserialize
    serialized = serialize_with_type(instance_val)
    print(f"Serialized size: {len(serialized)} bytes")
    
    deserialized = deserialize_with_type(serialized)
    print(f"Deserialized instance ID: {deserialized.value['id'].value}")

    # Navigate using path
    async def path_navigation():
        try:
            # Get the CPU utilization metric using path navigation
            metric_path = Path.get_attr("metadata").key_step("performance_metrics").key_step("cpu_utilization")
            cpu_metric = await metric_path.apply_path(instance_val.value)
            print(f"CPU Utilization: {cpu_metric.value}%")
            
            # Get the primary network interface
            for i, nic in enumerate(instance_val.value["network_interfaces"].value):
                if nic["type"].value == "primary":
                    ip_path = Path.get_attr("network_interfaces").index_step(i).child("ip_addresses").index_step(0)
                    primary_ip = await ip_path.apply_path(instance_val.value)
                    print(f"Primary IP: {primary_ip.value}")
                    break
                    
        except AttributePathError as e:
            print(f"Path error: {e}")

    asyncio.run(path_navigation())

except ValidationError as e:
    print(f"Validation error: {e}")
