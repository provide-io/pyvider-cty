#!/usr/bin/env python3
# docs/examples/example-08-path-navigation.py

import asyncio
from pyvider.cty import CtyObject, CtyList, CtyString, CtyNumber, CtyValue
from pyvider.cty.path import CtyPath

# Define a complex nested type
server_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "specs": CtyObject(
            attribute_types={
                "cpu": CtyNumber(),
                "memory": CtyNumber(),
                "disks": CtyList(
                    element_type=CtyObject(
                        attribute_types={
                            "size": CtyNumber(),
                            "type": CtyString()
                        }
                    )
                )
            }
        )
    }
)

# Create a value
server_data = {
    "name": "web-server-01",
    "specs": {
        "cpu": 8,
        "memory": 32,
        "disks": [
            {"size": 500, "type": "ssd"},
            {"size": 2000, "type": "hdd"}
        ]
    }
}

validated = server_type.validate(server_data)
server_val = CtyValue(vtype=server_type, value=validated)

async def navigate_paths():
    # Create different paths to navigate the data
    name_path = CtyPath.get_attr("name")
    cpu_path = CtyPath.get_attr("specs").child("cpu")
    first_disk_path = CtyPath.get_attr("specs").child("disks").index_step(0)
    disk_type_path = CtyPath.get_attr("specs").child("disks").index_step(0).child("type")
    
    # Apply paths to get values
    name = name_path.apply_path(server_val.value)
    cpu = cpu_path.apply_path(server_val.value)
    first_disk = first_disk_path.apply_path(server_val.value)
    disk_type = disk_type_path.apply_path(server_val.value)
    
    print(f"Server name: {name.value}")
    print(f"CPU cores: {cpu.value}")
    print(f"First disk size: {first_disk.get('size').value} GB")
    print(f"First disk type: {disk_type.value}")

if __name__ == "__main__":
    asyncio.run(navigate_paths())
