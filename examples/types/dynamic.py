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
from pyvider.cty import CtyDynamic, CtyList, CtyNumber, CtyString  # noqa: E402

configure_for_example()

dynamic_type = CtyDynamic()

cty_string = dynamic_type.validate("hello")
# The .value attribute holds the inner CtyValue with the inferred type.
assert isinstance(cty_string.value.type, CtyString)

cty_number = dynamic_type.validate(123)
assert isinstance(cty_number.value.type, CtyNumber)

dynamic_list_type = CtyList(element_type=CtyDynamic())
cty_list = dynamic_list_type.validate(["hello", 123, True])

print("Dynamic type examples ran successfully.")

# 🌊🪢🔚
