# examples/ch10_marks.py
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.example_utils import configure_for_example  # noqa: E402
from pyvider.cty import CtyString  # noqa: E402

configure_for_example()

cty_string = CtyString().validate("hello")

sensitive_string = cty_string.with_marks(("sensitive",))

private_sensitive_string = cty_string.with_marks(("sensitive", "private"))

assert sensitive_string.has_mark("sensitive") is True
assert sensitive_string.has_mark("private") is False

assert sensitive_string.marks == {"sensitive"}

print("Marks examples ran successfully.")

# 🐍⛓️📁🪄
