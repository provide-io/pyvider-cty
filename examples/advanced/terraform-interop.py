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
from pyvider.cty import CtyList, CtyString  # noqa: E402
from pyvider.cty.parser import parse_tf_type_to_ctytype  # noqa: E402

configure_for_example()

tf_type_string = ["list", "string"]
cty_type = parse_tf_type_to_ctytype(tf_type_string)

assert cty_type == CtyList(element_type=CtyString())

print("Terraform interop examples ran successfully.")

# 🌊🪢🔚
