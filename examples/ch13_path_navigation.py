#!/usr/bin/env python3
from examples.example_utils import configure_for_example
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyList
from pyvider.cty.path import CtyPath

configure_for_example()

# 1. Define a complex nested type.
server_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "specs": CtyObject(
            attribute_types={
                "cpu": CtyNumber(),
                "memory": CtyNumber(),
                "disks": CtyList(
                    element_type=CtyObject(
                        attribute_types={"size": CtyNumber(), "type": CtyString()}
                    )
                ),
            }
        ),
    }
)

# 2. Create and validate a CtyValue.
server_data = {
    "name": "web-server-01",
    "specs": {
        "cpu": 8,
        "memory": 32,
        "disks": [{"size": 500, "type": "ssd"}, {"size": 2000, "type": "hdd"}],
    },
}
server_val = server_type.validate(server_data)

# 3. Create different paths to navigate the data.
# Paths are built by chaining steps.
name_path = CtyPath.get_attr("name")
cpu_path = CtyPath.get_attr("specs").child("cpu")
first_disk_path = CtyPath.get_attr("specs").child("disks").index_step(0)
disk_type_path = first_disk_path.child("type")

# 4. Apply paths to the CtyValue to get the nested values.
name = name_path.apply_path(server_val)
cpu = cpu_path.apply_path(server_val)
first_disk = first_disk_path.apply_path(server_val)
disk_type = disk_type_path.apply_path(server_val)

print(f"Server name: {name.raw_value}")
print(f"CPU cores: {cpu.raw_value}")
# `first_disk` is a CtyValue(CtyObject), so we can index it.
print(f"First disk size: {first_disk['size'].raw_value} GB")
print(f"First disk type: {disk_type.raw_value}")

# 🐍🎯📄🪄
