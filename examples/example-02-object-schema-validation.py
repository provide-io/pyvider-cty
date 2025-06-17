#!/usr/bin/env python3
# docs/examples/example-02-object-schema-validation.py
#

from pyvider.cty import CtyBool, CtyNumber, CtyObject, CtyString

# Define a person schema
person_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool()
    },
    optional_attributes=frozenset(["active"])
)

# Validate data against the schema
person_data = {
    "name": "Alice",
    "age": 30
}

# Validate and handle errors properly
try:
    validated = person_type.validate(person_data)
    print(f"Validated person: {validated}")
except Exception as e:
    print(f"Validation error: {e}")
