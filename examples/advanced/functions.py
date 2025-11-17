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
from pyvider.cty import CtyNumber  # noqa: E402
from pyvider.cty.functions import abs_fn  # noqa: E402

configure_for_example()

# NOTE: As of this version, pyvider.cty does not support arithmetic
# operations like addition directly on CtyNumber values. The following
# is a demonstration of a function that is supported.

number_type = CtyNumber()
num1 = number_type.validate(-10)

# For available functions, you import them from the functions module
abs_result = abs_fn(num1)
assert abs_result.raw_value == 10

print("Functions examples ran successfully.")

# 🌊🪢🔚
