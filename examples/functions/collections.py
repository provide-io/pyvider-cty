#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The collection functions: building, querying and reshaping.

The ones a provider reaches for most, and the two places the answer is not what
a Python instinct expects -- set ordering, and what a set's length means while
anything inside it is unknown.
"""

from decimal import Decimal
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.example_utils import configure_for_example, stdlib_call as call  # noqa: E402
from pyvider.cty import (  # noqa: E402
    CtyList,
    CtyMap,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.functions import STDLIB  # noqa: E402

configure_for_example()

S, N = CtyString(), CtyNumber()
STRINGS = CtyList(element_type=S)
NUMBERS = CtyList(element_type=N)

# --------------------------------------------------------------------------- #
# Building
# --------------------------------------------------------------------------- #

assert call("concat", STRINGS.validate(["a"]), STRINGS.validate(["b", "c"])) == ["a", "b", "c"]
assert call("range", 0, 5, 1) == [Decimal(n) for n in range(5)]
assert call("zipmap", STRINGS.validate(["a", "b"]), NUMBERS.validate([1, 2])) == {
    "a": Decimal(1),
    "b": Decimal(2),
}

# --------------------------------------------------------------------------- #
# Querying
# --------------------------------------------------------------------------- #

names = STRINGS.validate(["alice", "bob"])

assert call("length", names) == Decimal(2)
assert call("contains", names, S.validate("bob")) is True
assert call("element", names, 0) == "alice"

settings = CtyMap(element_type=S).validate({"region": "us-east-1", "tier": "gold"})
assert call("keys", settings) == ["region", "tier"]
assert call("values", settings) == ["us-east-1", "gold"]
assert call("lookup", settings, "region", "unset") == "us-east-1"
assert call("lookup", settings, "missing", "unset") == "unset"

# --------------------------------------------------------------------------- #
# Reshaping
# --------------------------------------------------------------------------- #

assert call("reverselist", names) == ["bob", "alice"]
assert call("strrev", "abc") == "cba"
assert call("sort", STRINGS.validate(["c", "a", "b"])) == ["a", "b", "c"]
assert call("distinct", STRINGS.validate(["a", "b", "a"])) == ["a", "b"]
assert call("compact", STRINGS.validate(["a", "", "b"])) == ["a", "b"]
assert call("slice", STRINGS.validate(["a", "b", "c", "d"]), 1, 3) == ["b", "c"]
assert call("chunklist", STRINGS.validate(["a", "b", "c"]), 2) == [["a", "b"], ["c"]]

# `flatten` recurses through nested sequences and returns a *tuple*, keeping null
# elements and passing non-sequences straight through.
nested = CtyTuple(element_types=(STRINGS, STRINGS)).validate([["a"], ["b", "c"]])
assert call("flatten", nested) == ["a", "b", "c"]

# --------------------------------------------------------------------------- #
# Set algebra
# --------------------------------------------------------------------------- #

left = CtySet(element_type=S).validate(["a", "b"])
right = CtySet(element_type=S).validate(["b", "c"])

assert sorted(call("setunion", left, right)) == ["a", "b", "c"]
assert call("setintersection", left, right) == ["b"]
assert call("sethaselement", left, S.validate("a")) is True
assert call("setsubtract", left, right) == ["a"]
assert sorted(call("setsymmetricdifference", left, right)) == ["a", "c"]

# --------------------------------------------------------------------------- #
# The two surprises
# --------------------------------------------------------------------------- #

# A set of *primitives* is ordered by value, as you would expect. Iterating a
# set gives its elements in the order they will serialize in.
by_value = [element.value for element in CtySet(element_type=N).validate([3, 1, 12]).value]
assert by_value == [Decimal(1), Decimal(3), Decimal(12)]

# A set of anything else is ordered by the bytes of go-cty's element hash, which
# renders numbers as text -- so `[12]` sorts before `[1]`, because "2" sorts
# before the ";" that terminates the field. This order reaches the wire, and
# Terraform compares serialized state, so it is not cosmetic.
pairs = CtySet(element_type=CtyTuple(element_types=(N,)))
by_hash = [row.value[0].value for row in pairs.validate([[1], [12], [2]]).value]
assert by_hash == [Decimal(12), Decimal(1), Decimal(2)]

# A set's length is a *bound*, not an answer, while anything inside it is
# unknown at any depth: an unknown element may still turn out to equal another
# member and coalesce with it.
holder = CtySet(element_type=STRINGS).validate([["a"], [CtyValue.unknown(S)]])
assert STDLIB["length"](holder).is_unknown

# The exception go-cty makes for itself: one element has nothing to coalesce
# with, so the length is known even though the element is not.
alone = CtySet(element_type=S).validate([CtyValue.unknown(S)])
assert STDLIB["length"](alone).value == Decimal(1)

print("Collection function examples ran successfully.")

# 🌊🪢🔚
