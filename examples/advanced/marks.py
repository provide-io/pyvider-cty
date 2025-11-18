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
from pyvider.cty import CtyString  # noqa: E402
from pyvider.cty.marks import CtyMark  # noqa: E402

configure_for_example()

cty_string = CtyString().validate("hello")

# Create marks
sensitive_mark = CtyMark("sensitive")
private_mark = CtyMark("private")

# Mark with single mark
sensitive_string = cty_string.mark(sensitive_mark)

# Mark with multiple marks
private_sensitive_string = cty_string.with_marks({sensitive_mark, private_mark})

# Check for marks
assert sensitive_mark in sensitive_string.marks
assert sensitive_string.has_mark(sensitive_mark)
assert private_mark not in sensitive_string.marks

# Unmark
unmarked_value, removed_marks = sensitive_string.unmark()
assert len(unmarked_value.marks) == 0
assert sensitive_mark in removed_marks

print("Marks examples ran successfully.")

# 🌊🪢🔚
