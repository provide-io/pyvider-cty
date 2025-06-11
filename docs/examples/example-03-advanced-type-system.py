#!/usr/bin/env python3
# docs/examples/example-03-advanced-type-system.py
#

from pyvider.cty import CtyList, CtyNumber, CtyObject, CtyString

# Define a complex nested type
server_type = CtyObject(
    attribute_types={
        "hostname": CtyString(),
        "port": CtyNumber(),
        "tags": CtyList(element_type=CtyString()),
    }
)

# Create and validate complex data
server_data = {"hostname": "example.com", "port": 8080, "tags": ["web", "production"]}

validated = server_type.validate(server_data)
