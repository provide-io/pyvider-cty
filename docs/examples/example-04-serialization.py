#!/usr/bin/env python3
# docs/examples/example-04-serialization.py

from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyValue
from pyvider.cty.encoding.json_serializer import JsonSerializer

# Create a value to serialize
config_type = CtyObject(
    attribute_types={
        "api_url": CtyString(),
        "timeout": CtyNumber()
    }
)

config_data = {
    "api_url": "https://api.example.com",
    "timeout": 30
}

validated = config_type.validate(config_data)
config_val = CtyValue(config_type, validated)

# Serialize to JSON
serializer = JsonSerializer()
json_bytes = serializer.serialize(config_val)
print(f"Serialized: {json_bytes.decode('utf-8')}")

# Deserialize
deserialized = serializer.deserialize(json_bytes)
print(f"Deserialized: {deserialized}")
