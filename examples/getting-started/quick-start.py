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
from pyvider.cty import CtyNumber, CtyObject, CtyString  # noqa: E402

configure_for_example()

user_type = CtyObject(
    {
        "name": CtyString(),
        "age": CtyNumber(),
    }
)

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

# 🌊🪢🔚
