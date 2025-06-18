#!/usr/bin/env python3
# docs/examples/example-09-serialization.py

# Corrected imports and usage for serialization
from pyvider.cty import CtyList, CtyNumber, CtyObject, CtyString

# Use the actual conversion API
from pyvider.cty.conversion import WireFormatType, marshal, unmarshal

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

# Validate returns a CtyValue
cluster_val = cluster_type.validate(cluster_data)

# --- Corrected Serialization/Deserialization ---
try:
    # Use marshal/unmarshal functions
    json_data = marshal(cluster_val, format_kind=WireFormatType.JSON)
    msgpack_data = marshal(cluster_val, format_kind=WireFormatType.MSGPACK)

    # "Serialize with type" implies ensuring type info is included,
    # which marshal should do. We'll use JSON as the example typed data.
    typed_data = json_data

    print(f"JSON size: {len(json_data)} bytes")
    print(f"MessagePack size: {len(msgpack_data)} bytes")
    print(f"Typed data size (JSON): {len(typed_data)} bytes")

    # Deserialize with type information by providing expected_type
    recovered = unmarshal(
        typed_data,
        format_kind=WireFormatType.JSON, # Specify format if not auto-detectable
        expected_type=cluster_type
    )

    print(f"\nRecovered type: {recovered.type.__class__.__name__}")
    if not recovered.is_null and not recovered.is_unknown:
        print(f"Recovered name: {recovered['name'].value}")
        regions_list = recovered['regions']
        if not regions_list.is_null and not regions_list.is_unknown:
             print(f"Recovered regions: {[r.value for r in regions_list.value]}")
        else:
             print("Recovered regions: <null or unknown>")
    else:
        print("Recovered value is null or unknown.")

except Exception as e:
    print(f"Serialization/Deserialization Error: {e}")
