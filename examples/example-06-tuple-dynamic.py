#!/usr/bin/env python3
# docs/examples/example-06-tuple-dynamic.py

from pyvider.cty import CtyDynamic, CtyNumber, CtyObject, CtyString, CtyTuple

# 1. Define a tuple type with mixed element types, including a dynamic one.
coordinate_type = CtyTuple(
    element_types=(CtyString(), CtyNumber(), CtyNumber(), CtyDynamic())
)

# 2. Create raw data that matches the tuple's structure.
point_data = ("GPS", 37.7749, -122.4194, {"accuracy": 10, "timestamp": 1635721123})

# 3. Validate the data.
validated_tuple = coordinate_type.validate(point_data)

# 4. Access elements by index.
print(f"Point system: {validated_tuple[0].raw_value}")
print(f"Latitude: {validated_tuple[1].raw_value}")
print(f"Longitude: {validated_tuple[2].raw_value}")

# The dynamic value preserves its inferred type structure.
# CtyDynamic.validate infers the most specific type, which is CtyObject here.
metadata_val = validated_tuple[3]
print(f"\nMetadata Type (inferred): {metadata_val.type}")
print(f"Metadata is an object: {isinstance(metadata_val.type, CtyObject)}")
print(f"Metadata accuracy: {metadata_val['accuracy'].raw_value}")
