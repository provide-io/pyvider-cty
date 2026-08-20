#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Example module for pyvider-cty."""

from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.example_utils import configure_for_example  # noqa: E402
from pyvider.cty import CtyNumber, CtyString  # noqa: E402
from pyvider.cty.functions import SIGNATURES, STDLIB, abs_fn  # noqa: E402

configure_for_example()

# A CtyNumber has no arithmetic *operators* -- `a + b` on two values is not
# defined -- but every one of go-cty's 83 stdlib functions is here. Import the
# Python name, or look the go-cty name up in the STDLIB registry.
number_type = CtyNumber()
num1 = number_type.validate(-10)

abs_result = abs_fn(num1)
assert abs_result.raw_value == 10

# The registry is keyed by the name go-cty gives the function, which is what
# Terraform configuration writes. `and`, `or` and `not` are Python keywords and
# nine more would shadow builtins, so the registry is the surface that speaks
# Terraform and the module-level names stay Python-shaped.
assert len(STDLIB) == 83
total = STDLIB["add"](number_type.validate(2), number_type.validate(3))
assert total.raw_value == 5

# Every function declares what it accepts, so a return type can be predicted
# without a value in sight.
assert str(SIGNATURES["upper"].return_type([CtyString()])) == "string"

print("Functions examples ran successfully.")

# 🌊🪢🔚
