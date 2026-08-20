#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Unknown values and refinements: the model Terraform plans with.

The single most important cty concept for a provider author, and the one with no
Python analogue. During `terraform plan` a value that will only exist after apply
is *unknown*: not absent, not null, just not decided yet. Computing with it has
to produce another unknown rather than an answer, and a refinement is what is
already known about it before it is known.
"""

from decimal import Decimal
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.example_utils import configure_for_example  # noqa: E402
from pyvider.cty import (  # noqa: E402
    CtyList,
    CtyNumber,
    CtyString,
    CtyValue,
)
from pyvider.cty.functions import STDLIB  # noqa: E402
from pyvider.cty.refinement import refine  # noqa: E402
from pyvider.cty.unknown import unknown_as_null  # noqa: E402

configure_for_example()

string_type = CtyString()
number_type = CtyNumber()

# --------------------------------------------------------------------------- #
# An unknown is not a null
# --------------------------------------------------------------------------- #

# A null is a value that is definitely absent. An unknown is one nobody knows
# yet. Confusing them is the most common cty mistake, and they behave nothing
# alike: most stdlib parameters refuse a null outright and propagate an unknown.
unknown_name = CtyValue.unknown(string_type)
null_name = CtyValue.null(string_type)

assert unknown_name.is_unknown
assert not unknown_name.is_null
assert null_name.is_null
assert not null_name.is_unknown

# Computing with an unknown gives back an unknown -- of the *right type*, so the
# rest of the plan can still be type-checked.
shouted = STDLIB["upper"](unknown_name)
assert shouted.is_unknown
assert str(shouted.type) == "string"

# Computing with a null is refused. There is no answer to invent.
try:
    STDLIB["upper"](null_name)
    raise AssertionError("a null argument should have been refused")
except Exception as exc:
    assert "null" in str(exc)

# --------------------------------------------------------------------------- #
# Refinements: what is known before the value is
# --------------------------------------------------------------------------- #

# Terraform can often say something about a value it cannot yet produce: that it
# will not be null, that a string starts with a known prefix, that a collection
# has at least one element. Those facts are refinements, they travel on the wire,
# and Terraform plans with them.
url = refine(CtyValue.unknown(string_type)).string_prefix("https://").not_null().new_value()

assert url.is_unknown
assert url.value.string_prefix == "https://"
assert url.value.is_known_null is False

# `not_null` is the one that changes an *answer* rather than a display: equality
# against null is decided rather than undecided, because the value has already
# promised not to be one.
decided = STDLIB["equal"](url, CtyValue.null(string_type))
assert decided.value is False

# Without the refinement there is nothing to decide on, so the answer is itself
# unknown -- three-valued logic, not two.
undecided = STDLIB["equal"](CtyValue.unknown(string_type), CtyValue.null(string_type))
assert undecided.is_unknown

# Numbers refine to a range, and collections to a length range.
port = refine(CtyValue.unknown(number_type)).number_range_lower_bound(1024, inclusive=True).new_value()
assert port.value.number_lower_bound == (Decimal(1024), True)

names = (
    refine(CtyValue.unknown(CtyList(element_type=string_type))).collection_length_lower_bound(1).new_value()
)
assert names.value.collection_length_lower_bound == 1

# --------------------------------------------------------------------------- #
# Unknowns inside containers
# --------------------------------------------------------------------------- #

# The interesting cases are never at the top level. A list with one unknown
# element is the ordinary plan-time shape: the list is known, its length is
# known, and one element is not.
partly = CtyList(element_type=string_type).validate(["known", CtyValue.unknown(string_type)])

assert not partly.is_unknown
assert STDLIB["length"](partly).value == 2
assert partly.value[1].is_unknown

# `unknown_as_null` rewrites every unknown at every depth, which is how a
# plan-time value is turned into something that can be stored or displayed.
settled = unknown_as_null(partly)
assert settled.value[0].value == "known"
assert settled.value[1].is_null

print("Unknowns and refinements examples ran successfully.")

# 🌊🪢🔚
