#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.example_utils import configure_for_example  # noqa: E402
from pyvider.cty import CtyBool, CtyNumber, CtyObject, CtyString, CtyTuple  # noqa: E402

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

# 🌊🪢🔚
