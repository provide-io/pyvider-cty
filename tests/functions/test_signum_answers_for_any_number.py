#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`signum` gives the sign of any number cty can represent.

go-cty v1.19.0's `SignumFunc` read its argument into a Go `int` first, so a
fraction or anything outside int64 was an error before its sign was looked at.
Upstream fixed that on `main` in `a918e11` (zclconf/go-cty#218, unreleased as
v1.19.1) by switching on `AsBigFloat().Sign()`, and this package follows the fix
rather than the release. Until the soup-go oracle is rebuilt against a go-cty
that carries it, the differential sweep records the disagreement as strict
xfails, so the rebuild forces them out.
"""

from decimal import Decimal

import pytest

from pyvider.cty import CtyNumber
from pyvider.cty.functions import signum_fn

N = CtyNumber()


@pytest.mark.parametrize(
    ("number", "sign"),
    [
        (Decimal("0.5"), 1),
        (Decimal("-0.5"), -1),
        (Decimal("9223372036854775808"), 1),
        (Decimal("-9223372036854775809"), -1),
        (Decimal("Infinity"), 1),
        (Decimal("-Infinity"), -1),
        # `big.Float.Sign` answers 0 for negative zero, not -1.
        (Decimal("-0"), 0),
        (Decimal("0.0"), 0),
    ],
)
def test_signum_answers_with_the_sign_of_any_number(number: Decimal, sign: int) -> None:
    result = signum_fn(N.validate(number))

    assert result.type == N
    assert result.value == Decimal(sign)
    assert not result.value.is_signed() or sign < 0
