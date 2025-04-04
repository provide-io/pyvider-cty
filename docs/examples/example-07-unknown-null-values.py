#!/usr/bin/env python3
# docs/examples/example-07-unknown-null-values.py

from pyvider.cty import CtyString, CtyNumber, CtyBool, CtyObject, CtyValue

# Define a user profile type
profile_type = CtyObject(
    attribute_types={
        "username": CtyString(),
        "age": CtyNumber(),
        "verified": CtyBool(),
        "bio": CtyString()
    },
    optional_attributes=frozenset(["bio"])
)

# Create values with different states
known_value = CtyValue(
    vtype=profile_type, 
    value={
        "username": CtyString(value="alice"),
        "age": CtyNumber(value=30),
        "verified": CtyBool(value=True)
    }
)

unknown_value = CtyValue.unknown(profile_type)
null_value = CtyValue.null(profile_type)

# Check state of values
print(f"Unknown: {known_value.is_unknown}, Null: {known_value.is_null}")
print(f"Unknown: {unknown_value.is_unknown}, Null: {unknown_value.is_null}")
print(f"Unknown: {null_value.is_unknown}, Null: {null_value.is_null}")

# Try to access properties (would raise an exception for unknown/null)
if not known_value.is_unknown and not known_value.is_null:
    username = known_value.value.get("username")
    print(f"Username: {username.value}")
