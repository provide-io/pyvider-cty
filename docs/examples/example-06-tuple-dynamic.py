#!/usr/bin/env python3
# docs/examples/example-06-tuple-dynamic.py

from pyvider.cty import CtyTuple, CtyString, CtyNumber, CtyBool, CtyDynamic, CtyValue

# Define a tuple type with mixed element types
coordinate_type = CtyTuple(
    element_types=(CtyString(), CtyNumber(), CtyNumber(), CtyDynamic())
)

# Create and validate tuple data
point_data = ("GPS", 37.7749, -122.4194, {"accuracy": 10, "timestamp": 1635721123})

validated = coordinate_type.validate(point_data)
point_val = CtyValue(coordinate_type, validated)

# Access elements by index
print(f"Point system: {validated[0].value}")
print(f"Latitude: {validated[1].value}")
print(f"Longitude: {validated[2].value}")

# The dynamic value preserves its type structure
metadata = validated[3]
print(f"Metadata type: {type(metadata).__name__}")
print(f"Metadata accuracy: {metadata.value.get('accuracy')}")
