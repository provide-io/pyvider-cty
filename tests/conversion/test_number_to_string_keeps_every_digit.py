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

The differential suite pins this against real go-cty, but only under
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

# (label, input, the text go-cty's `big.Float.Text('f', -1)` produces)
CASES = [
    ("an integer past the 28-digit context", 2**100, "1267650600228229401496703205376"),
    ("a very large integer", 2**1000, str(2**1000)),
    ("max int64", 2**63 - 1, "9223372036854775807"),
    ("min int64", -(2**63), "-9223372036854775808"),
    ("a 29-digit decimal", Decimal("1.2345678901234567890123456789"), "1.2345678901234567890123456789"),
    # The cases that were already right, kept so a fix cannot trade one for the
    # other: no exponent form, and no trailing zeros a big.Float never had.
    ("a trailing zero", Decimal("1.50"), "1.5"),
    ("an exponent", Decimal("1E+2"), "100"),
    ("a tiny exponent", Decimal("1.23E-10"), "0.000000000123"),
    ("a negative zero", Decimal("-0.0"), "-0"),
    ("zero", Decimal("0"), "0"),
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


# 🌊🪢🔚
