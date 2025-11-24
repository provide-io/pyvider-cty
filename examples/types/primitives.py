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
from pyvider.cty import CtyBool, CtyNumber, CtyString  # noqa: E402

configure_for_example()

# CtyString
string_type = CtyString()
cty_string = string_type.validate("hello")
assert cty_string.raw_value == "hello"
try:
    string_type.validate(123)
except Exception as e:
    print(f"String validation failed as expected: {e}")

# CtyNumber
number_type = CtyNumber()
cty_int = number_type.validate(123)
assert cty_int.raw_value == 123
cty_float = number_type.validate(3.14)
assert cty_float.raw_value == 3.14
try:
    number_type.validate("hello")
except Exception as e:
    print(f"Number validation failed as expected: {e}")

# CtyBool
bool_type = CtyBool()
cty_true = bool_type.validate(True)
assert cty_true.raw_value is True
try:
    bool_type.validate(1)
except Exception as e:
    print(f"Bool validation failed as expected: {e}")

print("Primitive type examples ran successfully.")

# 🌊🪢🔚
