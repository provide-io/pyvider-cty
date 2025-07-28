#!/usr/bin/env python3

from pyvider.cty import CtyDynamic, CtyString, CtyNumber, CtyObject, CtyTuple

# The CtyDynamic Type
dynamic_type = CtyDynamic()
cty_string = dynamic_type.validate("hello")
assert isinstance(cty_string.value.type, CtyString)
cty_number = dynamic_type.validate(123)
assert isinstance(cty_number.value.type, CtyNumber)
print("CtyDynamic examples successful.")

# CtyDynamic in Collections
coordinate_type = CtyTuple(
    element_types=(CtyString(), CtyNumber(), CtyNumber(), CtyDynamic())
)
point_data = ("GPS", 37.7749, -122.4194, {"accuracy": 10})
validated_tuple = coordinate_type.validate(point_data)
metadata_val = validated_tuple[3]
print(f"Metadata Type (inferred): {metadata_val.value.type}")
print(f"Metadata is an object: {isinstance(metadata_val.value.type, CtyObject)}")
print(f"Metadata accuracy: {metadata_val.value['accuracy'].raw_value}")
