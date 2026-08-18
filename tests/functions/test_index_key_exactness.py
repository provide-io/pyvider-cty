#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`index` and `hasindex` on a key that is not an exact, in-range position.

go-cty reads the key with `big.Float.Int64()` and refuses anything the
conversion did not perform exactly (`cty/value_ops.go:994`):

    index, accuracy := key.v.(*big.Float).Int64()
    if accuracy != big.Exact || index < 0 {
        return False
    }

`Int64` truncates towards zero, so a fraction, a magnitude beyond int64 and an
infinity all come back inexact. Every one of those was a *usable* index here:
`index(list, 1.5)` returned the element at 1, and a non-finite key escaped as
`CtyFunctionPanicError` from `int(Decimal("Infinity"))`.

Verified against go-cty v1.19.0 through the soup-go oracle:

    hasindex(["a","b","c"], 1.5)  -> false
    hasindex(["a","b","c"], -1)   -> false
    hasindex(["a","b","c"], 1e30) -> false
    index(["a","b","c"], 1.5)     -> error "invalid index"
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from pyvider.cty import CtyList, CtyNumber, CtyString, CtyTuple
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import hasindex, index

# Keys that name no position, and the reason each one does not.
INEXACT_KEYS = [
    pytest.param(Decimal("1.5"), id="fraction"),
    pytest.param(Decimal("-0.5"), id="negative-fraction"),
    pytest.param(Decimal("1e30"), id="beyond-int64"),
    pytest.param(Decimal("-1e30"), id="below-int64"),
    pytest.param(Decimal("Infinity"), id="infinity"),
    pytest.param(Decimal("-Infinity"), id="negative-infinity"),
    pytest.param(Decimal("NaN"), id="nan"),
    pytest.param(Decimal("-1"), id="negative"),
]


def _list() -> object:
    return CtyList(element_type=CtyString()).validate(["a", "b", "c"])


def _tuple() -> object:
    return CtyTuple((CtyString(), CtyNumber())).validate(("a", 1))


@pytest.mark.parametrize("key", INEXACT_KEYS)
def test_hasindex_of_a_list_is_false(key: Decimal) -> None:
    """False, not True and not a panic: no such position exists."""
    assert hasindex(_list(), CtyNumber().validate(key)).value is False


@pytest.mark.parametrize("key", INEXACT_KEYS)
def test_hasindex_of_a_tuple_is_false(key: Decimal) -> None:
    """The tuple branch reads the key the same way the list branch does."""
    assert hasindex(_tuple(), CtyNumber().validate(key)).value is False


@pytest.mark.parametrize("key", INEXACT_KEYS)
def test_index_of_a_list_refuses(key: Decimal) -> None:
    """A refusal, and specifically not the element at the truncated position."""
    with pytest.raises(CtyFunctionError):
        index(_list(), CtyNumber().validate(key))


def test_a_whole_key_still_indexes() -> None:
    """The exactness check must not cost the ordinary case."""
    assert index(_list(), CtyNumber().validate(Decimal(1))).value == "b"
    assert hasindex(_list(), CtyNumber().validate(Decimal(2))).value is True
    assert hasindex(_list(), CtyNumber().validate(Decimal(3))).value is False


def test_a_key_spelled_as_a_fraction_of_itself_still_indexes() -> None:
    """`2.0` is the whole number 2, however it was written."""
    assert index(_list(), CtyNumber().validate(Decimal("2.0"))).value == "c"


# 🐍🏗️🔚
