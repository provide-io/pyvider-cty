#!/usr/bin/env python3
from pyvider.cty import CtyObject, CtyString, CtyNumber
from examples.example_utils import configure_for_example

configure_for_example()

user_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
})

user_data = {
    "name": "Alice",
    "age": 30,
}

try:
    cty_user = user_type.validate(user_data)
    print("Validation successful!")
    print(f"cty_user: {cty_user}")
except Exception as e:
    print(f"Validation failed: {e}")
