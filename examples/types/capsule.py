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
from pyvider.cty.types import CtyCapsule  # noqa: E402

configure_for_example()


class FileHandle:
    def __init__(self, path: str) -> None:
        self.path = path


file_handle_type = CtyCapsule("FileHandle", FileHandle)

file_handle = FileHandle("/path/to/file")

cty_file_handle = file_handle_type.validate(file_handle)

encapsulated_handle = cty_file_handle.raw_value
assert encapsulated_handle.path == "/path/to/file"

try:
    file_handle_type.validate("not a file handle")
except Exception as e:
    print(f"Capsule validation failed as expected: {e}")

print("Capsule type examples ran successfully.")

# 🌊🪢🔚
