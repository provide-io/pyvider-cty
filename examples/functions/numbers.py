#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Arithmetic, comparison, and the three places a `Decimal` answers differently.

A `CtyNumber` has no arithmetic *operators* -- `a + b` on two values is not
defined -- because the answer has to be go-cty's, and go-cty computes in a
512-bit `big.Float`. The stdlib functions are where that happens.
"""

from decimal import Decimal, getcontext
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.example_utils import configure_for_example, stdlib_call as call  # noqa: E402

configure_for_example()

# --------------------------------------------------------------------------- #
# Arithmetic
# --------------------------------------------------------------------------- #

assert call("add", 2, 3) == Decimal(5)
assert call("subtract", 5, 3) == Decimal(2)
assert call("multiply", 3, 4) == Decimal(12)
assert call("divide", 1, 8) == Decimal("0.125")
assert call("modulo", 7, 3) == Decimal(1)
assert call("negate", 5) == Decimal(-5)
assert call("abs", -5) == Decimal(5)

# Dividing by zero is an infinity rather than an error, as it is in a float.
assert call("divide", 1, 0) == Decimal("Infinity")

# --------------------------------------------------------------------------- #
# Rounding and sign
# --------------------------------------------------------------------------- #

assert call("ceil", Decimal("1.2")) == Decimal(2)
assert call("floor", Decimal("1.8")) == Decimal(1)
assert call("int", Decimal("1.9")) == Decimal(1)  # truncates toward zero
assert call("int", Decimal("-1.9")) == Decimal(-1)
assert call("signum", -7) == Decimal(-1)
assert call("signum", 0) == Decimal(0)

# --------------------------------------------------------------------------- #
# Comparison, min and max
# --------------------------------------------------------------------------- #

assert call("greaterthan", 3, 2) is True
assert call("lessthanorequalto", 2, 2) is True
assert call("max", 1, 9, 5) == Decimal(9)
assert call("min", 1, 9, 5) == Decimal(1)
assert call("equal", 1, 1) is True
assert call("notequal", 1, 2) is True

# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

assert call("parseint", "ff", 16) == Decimal(255)
assert call("tonumber", "42") == Decimal(42)
assert call("tostring", 42) == "42"

# --------------------------------------------------------------------------- #
# Where a Python instinct is wrong
# --------------------------------------------------------------------------- #

# 1. Arithmetic is not computed in your ambient `Decimal` context. Python's
#    default carries 28 significant digits and rounds silently past them; these
#    compute at the width go-cty's 512-bit `big.Float` spells, so a wide integer
#    keeps every digit.
assert getcontext().prec == 28
assert format(call("add", 2**100, 1), "f") == "1267650600228229401496703205377"

# 2. The sign of a zero is a real distinction -- it reaches the wire -- and
#    Python's operators throw it away. `-Decimal(0)` is the *arithmetic* 0 - 0,
#    which the decimal specification defines as +0; go-cty's negate flips the
#    sign bit of a float.
assert not (-Decimal(0)).is_signed()
negated = call("negate", 0)
assert negated.is_zero() and negated.is_signed()

# Five functions have five different rules for it, all transcribed from go-cty.
assert not call("int", Decimal("-0.5")).is_signed()  # truncation goes through a big.Int
assert call("int", Decimal("-0.0")).is_signed()  # already whole: returned untouched
assert not call("ceil", Decimal("-0.0")).is_signed()  # ceil has no untouched path
assert not call("modulo", -1, 1).is_signed()  # a - b*trunc(a/b), and x - x is +0
assert call("modulo", Decimal("-0.0"), 1).is_signed()  # a zero dividend takes the divisor's sign

# 3. `Decimal` accepts input Terraform rejects: its constructor strips
#    surrounding whitespace, and Go's `big.ParseFloat` grammar has no room for a
#    space.
assert Decimal(" 1") == 1
try:
    call("tonumber", " 1")
    raise AssertionError("go-cty refuses a leading space")
except Exception as exc:
    assert "cannot convert string to number" in str(exc)

print("Number function examples ran successfully.")

# 🌊🪢🔚
