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
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack  # noqa: E402

configure_for_example()

# 1. Define a type and a CtyValue
user_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
user_value = user_type.validate({"name": "Alice", "age": 30})

# 2. Serialize to Msgpack
msgpack_bytes = cty_to_msgpack(user_value, user_type)
print(f"Serialized Msgpack (bytes): {msgpack_bytes!r}")


# 3. Deserialize from Msgpack
reconstructed_value = cty_from_msgpack(msgpack_bytes, user_type)
assert reconstructed_value == user_value
print("\nSuccessfully reconstructed value from Msgpack.")

# 🌊🪢🔚
