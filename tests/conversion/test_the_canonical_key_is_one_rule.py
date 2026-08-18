#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The canonical order has one fallback for a member `validate` did not normalise.

There were two, and they were not comparable with each other:

    _member_key(m)         -> (0, -1, repr(m))      # hashing, de-duplication
    canonical_sort_key(m)  -> (0, str(m))           # sorting, in conversion

A real value's key is `(0, <type rank>, ...)`. The first fallback keeps that
arity and puts an int where the rank goes, so it orders against every real key.
The second is a two-tuple whose second element is a string, so sorting a
container holding both kinds compared an `int` against a `str` and raised a bare
`TypeError` -- from inside `cty_to_native`, and outside the error taxonomy.

Only a hand-built value can hold such a member; `validate` normalises them. That
makes this rare, not unreachable, and `CtyValue` is a public constructor.
"""

from __future__ import annotations

import pytest

from pyvider.cty import CtyNumber, CtySet, CtyString, CtyValue
from pyvider.cty.conversion import cty_to_native
from pyvider.cty.conversion._utils import canonical_sort_key
from pyvider.cty.values.base import _member_key

RAW_MEMBERS = [
    pytest.param(42, id="int"),
    pytest.param("a", id="str"),
    pytest.param(None, id="none"),
    pytest.param((1, 2), id="tuple"),
]


@pytest.mark.parametrize("member", RAW_MEMBERS)
def test_the_two_fallbacks_are_the_same_rule(member: object) -> None:
    """Not "compatible" -- identical. Two spellings is how they drifted apart."""
    assert canonical_sort_key(member) == _member_key(member)


@pytest.mark.parametrize("member", RAW_MEMBERS)
def test_a_raw_member_orders_against_a_real_one(member: object) -> None:
    """The comparison that raised: a raw member's key against a validated one's."""
    real = CtyString().validate("z")._canonical_sort_key()
    raw = canonical_sort_key(member)

    assert (raw < real) or (real < raw) or raw == real


def test_converting_a_hand_built_mixed_set_does_not_raise() -> None:
    """`cty_to_native` raised `TypeError` here, which is not a `CtyError`."""
    payload = frozenset([CtyString().validate("a"), "b"])
    value = CtyValue(CtySet(element_type=CtyString()), payload)

    assert len(cty_to_native(value)) == 2


def test_a_raw_member_sorts_ahead_of_every_real_one() -> None:
    """Rank -1, so raw members group rather than interleave with real types."""
    members = [CtyString().validate("a"), CtyNumber().validate(1), "raw"]

    assert sorted(members, key=canonical_sort_key)[0] == "raw"


# 🐍🏗️🔚
