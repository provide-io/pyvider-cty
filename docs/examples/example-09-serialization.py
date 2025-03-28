#!/usr/bin/env python3
# docs/examples/example-09-serialization.py

from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyList, CtyValue
from pyvider.cty.encoding import (
    serialize, deserialize, serialize_with_type, deserialize_with_type
)

# Define a complex type
cluster_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "instance_count": CtyNumber(),
        "regions": CtyList(element_type=CtyString())
    }
)

# Create a value
cluster_data = {
    "name": "production-cluster",
    "instance_count": 5,
    "regions": ["us-west-1", "eu-west-1", "ap-southeast-1"]
}

validated = cluster_type.validate(cluster_data)
cluster_val = CtyValue(type_=cluster_type, value=validated)

# Serialize to different formats
json_data = serialize(cluster_val, format_name="json")
msgpack_data = serialize(cluster_val, format_name="msgpack")

# Serialize with type preservation
typed_data = serialize_with_type(cluster_val)

print(f"JSON size: {len(json_data)} bytes")
print(f"MessagePack size: {len(msgpack_data)} bytes")
print(f"Typed data size: {len(typed_data)} bytes")

# Deserialize with type information
recovered = deserialize_with_type(typed_data)
print(f"Recovered type: {recovered.type.__class__.__name__}")
print(f"Recovered name: {recovered.value['name'].value}")
print(f"Recovered regions: {[r.value for r in recovered.value['regions'].value]}")
