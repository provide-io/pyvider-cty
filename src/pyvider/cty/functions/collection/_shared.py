#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Helpers more than one module of `pyvider.cty.functions.collection` needs.

See the package docstring for what the collection functions are and the two
deliberate departures from go-cty they carry.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from pyvider.cty import (
    CtyValue,
)
from pyvider.cty.values.set_order import order_key as set_order_key

# The lowest number of stored elements at which a set's count can be in doubt.
_AMBIGUOUS_SET_SIZE = 2


Args = Sequence[CtyValue[Any]]


def _sequence_elements(seq: CtyValue[Any]) -> list[CtyValue[Any]]:
    """A sequence's elements in a stable order.

    A set has no order of its own, so it is given the same one that was used to
    de-duplicate it, rather than whatever the frozenset happens to iterate in.
    """
    if isinstance(seq.value, frozenset):
        return sorted(seq.value, key=set_order_key)
    return list(cast("tuple[CtyValue[Any], ...]", seq.value))


def _set_length_is_known(collection: CtyValue[Any], stored: int) -> bool:
    """When a set knows how many elements it has. go-cty's `Value.Length()`.

    Two conditions, and go-cty checks them in this order (`value_ops.go:1126`):
    a store of one element knows its length whatever that element is, because
    there is nothing for it to coalesce with; otherwise the set has to be
    **wholly** known.

    Wholly, which is the half that was wrong here until 2026-08-19: this asked
    whether any element `is_unknown`, which is one level deep, so a set of lists
    holding an unknown *inside* a list counted itself as known and answered a
    length go-cty leaves undecided. Found by the stdlib fuzz.
    """
    return stored < _AMBIGUOUS_SET_SIZE or collection.is_wholly_known()


# 🌊🪢🔚
