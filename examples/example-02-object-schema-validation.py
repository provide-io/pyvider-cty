#!/usr/bin/env python3
# docs/examples/example-02-object-schema-validation.py

from pyvider.cty import CtyBool, CtyNumber, CtyObject, CtyString
from pyvider.cty.exceptions import CtyValidationError

# 1. Define an object schema with required and optional attributes.
person_type = CtyObject(
    attribute_types={"name": CtyString(), "age": CtyNumber(), "active": CtyBool()},
    optional_attributes=frozenset(["active"]),
)

# 2. Define data that satisfies the schema.
# Note that the optional 'active' attribute is missing.
person_data = {"name": "Alice", "age": 30}

# 3. Validate the data against the schema.
try:
    validated_person = person_type.validate(person_data)

    print(f"Successfully validated data for type: {validated_person.type}")

    # Accessing attributes returns their respective CtyValue instances.
    name_val = validated_person["name"]
    age_val = validated_person["age"]
    active_val = validated_person["active"] # Accessing the optional attribute

    print(f"Name: {name_val.raw_value} (Type: {name_val.type})")
    print(f"Age: {age_val.raw_value} (Type: {age_val.type})")
    
    # The missing optional attribute 'active' is present but is a null CtyValue.
    print(f"Active: {active_val.raw_value} (Is Null: {active_val.is_null})")

except CtyValidationError as e:
    print(f"Validation error: {e}")
