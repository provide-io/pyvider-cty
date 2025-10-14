# examples/ch07_structural_types.py
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python3
from examples.example_utils import configure_for_example
from pyvider.cty import CtyBool, CtyNumber, CtyObject, CtyString, CtyTuple

configure_for_example()

# CtyObject
user_type = CtyObject(
    {
        "name": CtyString(),
        "age": CtyNumber(),
        "is_active": CtyBool(),
    }
)
user_data = {"name": "Alice", "age": 30, "is_active": True}
cty_user = user_type.validate(user_data)
assert cty_user.raw_value == user_data
try:
    user_type.validate({"name": "Bob", "age": 40})
except Exception as e:
    print(f"Object validation failed as expected (missing attribute): {e}")
try:
    user_type.validate({"name": "Charlie", "age": 50, "is_active": False, "extra": "attribute"})
except Exception as e:
    print(f"Object validation failed as expected (extra attribute): {e}")

# CtyTuple
tuple_type = CtyTuple((CtyString(), CtyNumber(), CtyBool()))
tuple_data = ("hello", 123, True)
cty_tuple = tuple_type.validate(tuple_data)
assert cty_tuple.raw_value == tuple_data
try:
    tuple_type.validate(["hello", 123])
except Exception as e:
    print(f"Tuple validation failed as expected (wrong length): {e}")
try:
    tuple_type.validate(["hello", "world", True])
except Exception as e:
    print(f"Tuple validation failed as expected (wrong element type): {e}")

print("Structural type examples ran successfully.")

# 🐍⛓️📁🪄
