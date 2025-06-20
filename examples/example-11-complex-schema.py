#!/usr/bin/env python3
# docs/examples/example-11-complex-schema.py

from decimal import Decimal

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
)

# Use the actual conversion API
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

instance_type = CtyObject(
    attribute_types={
        "id": CtyString(),
        "name": CtyString(),
        "instance_type": CtyString(),
        "state": CtyString(),
        "launched_at": CtyString(),  # Assuming string for simplicity
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
    instance_val = instance_type.validate(instance_data)
    print("Successfully validated complex instance schema")

    # --- Corrected Serialization ---
    # Serialize using marshal function
    serialized = marshal(instance_val, format_kind=WireFormatType.JSON)
    print(f"Full Serialized JSON:\n{serialized.decode()}")
    print(f"\nSerialized size: {len(serialized)} bytes")

    # Deserialize using unmarshal function
    deserialized = unmarshal(
        serialized, format_kind=WireFormatType.JSON, expected_type=instance_type
    )
    if not deserialized.is_null and not deserialized.is_unknown:
        print(f"Deserialized instance ID: {deserialized['id'].value}")
    else:
        print("Deserialized value is null or unknown.")

    # --- Corrected Path Navigation ---
    # Path navigation does not need to be async
    def path_navigation() -> None:
        try:
            # Get the CPU utilization metric using path navigation
            # Corrected: Use .key() instead of non-existent key_step
            metric_path = (
                CtyPath.get_attr("metadata")
                .key("performance_metrics")
                .key("cpu_utilization")
            )
            # apply_path is not async and operates on the CtyValue
            cpu_metric = metric_path.apply_path(deserialized)
            print(f"\nCPU Utilization: {cpu_metric.value}%")

            # Get the primary network interface IP
            primary_ip_val = None
            if not instance_val["network_interfaces"].is_null:
                for i, nic_val in enumerate(instance_val["network_interfaces"].value):
                    if not nic_val.is_null and nic_val["type"].value == "primary":
                        # Ensure ip_addresses is not null/unknown before indexing
                        ip_list_val = nic_val["ip_addresses"]
                        if (
                            not ip_list_val.is_null
                            and not ip_list_val.is_unknown
                            and len(ip_list_val.value) > 0
                        ):
                            ip_path = (
                                CtyPath.get_attr("network_interfaces")
                                .index_step(i)
                                .child("ip_addresses")
                                .index_step(0)
                            )
                            primary_ip_val = ip_path.apply_path(instance_val)
                            break  # Found primary

            if primary_ip_val:
                print(f"Primary IP: {primary_ip_val.value}")
            else:
                print("Primary IP not found or NIC/IP list was null/empty.")

        except AttributePathError as e:
            print(f"Path error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during path navigation: {e}")

    path_navigation()

except CtyValidationError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
