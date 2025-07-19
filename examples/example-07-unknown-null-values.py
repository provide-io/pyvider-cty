#!/usr/bin/env python3
# docs/examples/example-07-unknown-null-values.py

from pyvider.cty import CtyBool, CtyNumber, CtyObject, CtyString, CtyValue

# 1. Define a user profile type.
profile_type = CtyObject(
    attribute_types={
        "username": CtyString(),
        "age": CtyNumber(),
        "verified": CtyBool(),
    },
)

# 2. Create a known, fully-populated value.
known_value = profile_type.validate({"username": "alice", "age": 30, "verified": True})

# 3. Create an unknown value of the profile type.
# This represents a value that will be known later (e.g., after an API call).
unknown_value = CtyValue.unknown(profile_type)

# 4. Create a null value of the profile type.
# This represents an explicit absence of a value.
null_value = CtyValue.null(profile_type)

# 5. Check the state of each value.
print(
    f"Known Value:   Is Unknown? {known_value.is_unknown}, Is Null? {known_value.is_null}"
)
print(
    f"Unknown Value: Is Unknown? {unknown_value.is_unknown}, Is Null? {unknown_value.is_null}"
)
print(
    f"Null Value:    Is Unknown? {null_value.is_unknown}, Is Null? {null_value.is_null}"
)

# 6. Safely access properties.
if not known_value.is_unknown and not known_value.is_null:
    username = known_value["username"]
    print(f"\nUsername from known value: {username.raw_value}")

# Accessing properties of a null or unknown value would raise an error.
try:
    _ = null_value["username"]
except TypeError as e:
    print(f"Attempting to access null value property failed as expected: {e}")
