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
        "regions": CtyList(element_type=CtyString()),
    }
)

# Create a value
cluster_data = {
    "name": "production-cluster",
    "instance_count": 5,
    "regions": ["us-west-1", "eu-west-1", "ap-southeast-1"],
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
        format_kind=WireFormatType.JSON,  # Specify format if not auto-detectable
        expected_type=cluster_type,  # Reverted to original cluster_type
    )

    print(f"\nRecovered type: {recovered.type.__class__.__name__}")
    if not recovered.is_null and not recovered.is_unknown:
        # Assuming deserialization might wrap values due to dynamic fallback behavior
        name_details = recovered["name"]
        if not name_details.is_null and not name_details.is_unknown and hasattr(name_details, 'value') and isinstance(name_details.value, dict):
            print(f"Recovered name: {name_details.value['value']}")
        else:
            # Fallback or direct access if structure is simpler than expected
            print(f"Recovered name (raw/unexpected structure): {name_details.value}")


        regions_value_container = recovered["regions"]
        if not regions_value_container.is_null and not regions_value_container.is_unknown and hasattr(regions_value_container, 'value') and isinstance(regions_value_container.value, dict):
            regions_list_value = regions_value_container.value['value']
            # The previous diagnostic showed regions_list_value itself can be a CtyValue (CtyList)
            # So, if it's a CtyValue, we need its .value attribute to get the Python list
            if hasattr(regions_list_value, 'value') and isinstance(regions_list_value.value, list):
                 actual_list = regions_list_value.value
                 # And elements of this list are also CtyValues
                 print(f"Recovered regions: {[r.value for r in actual_list]}")
            elif isinstance(regions_list_value, list): # If it's already a list of raw values (less likely given logs)
                 print(f"Recovered regions: {regions_list_value}")
            else:
                print(f"Recovered regions list (raw/unexpected structure): {regions_list_value}")
        else:
            print(f"Recovered regions container: <null, unknown, or not structured as expected: {regions_value_container.value}>")
    else:
        print("Recovered value is null or unknown.")

except Exception as e:
    print(f"Serialization/Deserialization Error: {e}")
