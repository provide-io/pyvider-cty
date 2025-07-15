#!/usr/bin/env python3
# docs/examples/example-03-advanced-type-system.py

from pyvider.cty import CtyList, CtyNumber, CtyObject, CtyString
from pyvider.cty.exceptions import CtyValidationError

# 1. Define a complex nested type for a server configuration.
server_type = CtyObject(
    attribute_types={
        "hostname": CtyString(),
        "port": CtyNumber(),
        "tags": CtyList(element_type=CtyString()),
    }
)

# 2. Create raw Python data that matches the schema.
server_data = {
    "hostname": "example.com", 
    "port": 8080, 
    "tags": ["web", "production"]
}

# 3. Validate the data.
try:
    validated_server = server_type.validate(server_data)
    print("Validation successful!")
    print(f"Validated Hostname: {validated_server['hostname'].raw_value}")
    
    # Access nested list
    tags_list_value = validated_server['tags']
    print(f"Tag list type: {tags_list_value.type}")
    print(f"Raw tags: {[tag.raw_value for tag in tags_list_value.raw_value]}")

except CtyValidationError as e:
    print(f"Validation failed: {e}")
