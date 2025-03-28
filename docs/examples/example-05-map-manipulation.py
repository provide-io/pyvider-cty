#!/usr/bin/env python3
# docs/examples/example-05-map-manipulation.py

from pyvider.cty import CtyMap, CtyString, CtyNumber, CtyValue

# Define a map type with string keys and number values
config_type = CtyMap(
    key_type=CtyString(),
    value_type=CtyNumber()
)

# Create and validate map data
config_data = {
    "max_connections": 100,
    "timeout": 30,
    "retry_limit": 5
}

validated = config_type.validate(config_data)
config_val = CtyValue(config_type, validated)

# Access map values
for key, value in validated.items():
    print(f"Key: {key.value}, Value: {value.value}")

# Set a new value
new_config = config_type.set("batch_size", 1000)
print(f"Added batch_size: {new_config.get('batch_size').value}")

# Delete a value
modified_config = new_config.delete("timeout")
print(f"Keys after deletion: {[k.value for k in modified_config.value.keys()]}")
