#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Rendering a number to text must not round it.

`_number_to_string` is the one renderer behind `convert(number, string)`,
`tostring`, `format("%s", n)`, `jsonencode` and the `cty/json` codec. It called
`Decimal.normalize()`, which honours the active decimal context -- default
precision 28 -- and therefore *rounds*: `2**100` came out as
`1267650600228229401496703205000` against go-cty's
`1267650600228229401496703205376`.

The value itself was never lossy. `validate` and the msgpack codec both carried
every digit, so the two codecs in this package disagreed about the same number,
and the one that lost digits was JSON -- which is what Terraform state and
`terraform show -json` are written in.

Distinct from the accepted `divide` divergence, which is about a result
*computed* at 28 digits. Nothing is computed here; digits already held were
discarded on the way out.

**Parity has a ceiling, and it is 154 significant digits.** A go-cty number is a
512-bit `big.Float` rendered with `Text('f', -1)` -- the shortest decimal that
reads back as the same float -- so it can spell `floor(512 * log10 2) = 154`
significant digits and writes zeros past them, where a `Decimal` spells every
digit it holds. Measured against the live oracle on 2026-08-19: `5**220` is 154
digits and agrees, `5**221` is 155 and is the first that cannot. That boundary
is the `tostring(5**221)` entry in the sweep's `KNOWN_DIVERGENCES`, and it is
the width half of the same closed decision as `divide` -- matching it means
holding numbers as a binary float rather than a `Decimal`.

So the cases below are in two groups: the ones inside the parity range, whose
expectations are go-cty's own answers, and the ones past it, which record what
this package does and are marked as divergences rather than as agreement.

The differential suite pins the parity range against real go-cty, but only under
`--run-compat`. These run in the ordinary suite so the guard is not conditional
on a Go toolchain.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from pyvider.cty import CtyNumber, CtyString
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.conversion import convert
from pyvider.cty.functions import STDLIB
from pyvider.cty.json_codec import cty_to_json

# Inside the parity range: 154 significant digits or fewer, so each expectation
# is what go-cty's own `big.Float.Text('f', -1)` produces, checked against the
# live harness.
CASES = [
    ("an integer past the 28-digit context", 2**100, "1267650600228229401496703205376"),
    ("max int64", 2**63 - 1, "9223372036854775807"),
    ("min int64", -(2**63), "-9223372036854775808"),
    ("a 29-digit decimal", Decimal("1.2345678901234567890123456789"), "1.2345678901234567890123456789"),
    ("154 significant digits, the last that agrees", 5**220, str(5**220)),
    # Magnitude is not what decides it. This is 501 digits and one of them
    # significant, and go-cty spells it out in full.
    ("a huge magnitude with one significant digit", 10**500, str(10**500)),
    # The cases that were already right, kept so a fix cannot trade one for the
    # other: no exponent form, and no trailing zeros a big.Float never had.
    ("a trailing zero", Decimal("1.50"), "1.5"),
    ("an exponent", Decimal("1E+2"), "100"),
    ("a tiny exponent", Decimal("1.23E-10"), "0.000000000123"),
    ("a negative zero", Decimal("-0.0"), "-0"),
    ("zero", Decimal("0"), "0"),
]

# Past the parity range. These record what this package does, which is to spell
# every digit; go-cty stops at 154 and writes zeros. Held here rather than left
# implicit so that adopting a binary-float payload later turns them red.
PAST_GO_CTYS_WIDTH = [
    ("155 significant digits, the first that cannot agree", 5**221),
    ("a 302-digit integer", 2**1000),
]


@pytest.mark.parametrize(("label", "raw", "expected"), CASES, ids=[case[0] for case in CASES])
def test_every_text_route_renders_all_of_the_digits(label: str, raw: object, expected: str) -> None:
    """One renderer, four public routes to it, and they must all agree."""
    value = CtyNumber().validate(raw)

    assert convert(value, CtyString()).value == expected
    assert STDLIB["tostring"](value).value == expected
    assert STDLIB["format"](CtyString().validate("%s"), value).value == expected
    assert STDLIB["jsonencode"](value).value == expected


@pytest.mark.parametrize(("label", "raw", "expected"), CASES, ids=[case[0] for case in CASES])
def test_the_two_codecs_agree_about_the_same_number(label: str, raw: object, expected: str) -> None:
    """The JSON codec must not lose a digit the msgpack codec keeps."""
    number = CtyNumber()
    value = number.validate(raw)

    assert cty_to_json(value, number) == expected.encode()
    assert cty_from_msgpack(cty_to_msgpack(value, number), number).value == value.value


@pytest.mark.parametrize(("label", "raw"), PAST_GO_CTYS_WIDTH, ids=[case[0] for case in PAST_GO_CTYS_WIDTH])
def test_past_go_ctys_width_this_package_spells_every_digit(label: str, raw: int) -> None:
    """A recorded divergence, not an agreement.

    go-cty rounds these to 154 significant digits. Asserting the exact spelling
    here would read as parity; the point is the opposite -- that this package
    answers something go-cty does not, and that the answer is at least the exact
    one rather than a differently-rounded one.
    """
    value = CtyNumber().validate(raw)
    rendered = convert(value, CtyString()).value

    assert rendered == str(raw)
    assert len(str(raw).rstrip("0")) > 154, "this case no longer sits past go-cty's width"


# 🌊🪢🔚
