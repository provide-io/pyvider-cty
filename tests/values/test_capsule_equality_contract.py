#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A capsule's equal_fn and hash_fn are written against its PAYLOAD.

A null or an unknown has no payload, so handing one to user code raised
AttributeError out of a callback that had no way to expect it -- and two nulls
of one type must compare equal in cty regardless of what the capsule thinks.
"""

from attrs import define

from pyvider.cty import CtyList, CtyValue
from pyvider.cty.types import CtyCapsuleWithOps


@define
class Boxed:
    n: int


class Bare:
    """No __repr__, so the default one embeds the object's address."""

    def __init__(self, n: int) -> None:
        self.n = n


def _capsule(name: str, cls: type) -> CtyCapsuleWithOps:
    return CtyCapsuleWithOps(name, cls, equal_fn=lambda a, b: a.n == b.n, hash_fn=lambda a: hash(a.n))


CAP = _capsule("Boxed", Boxed)


def test_two_nulls_of_a_capsule_type_are_equal() -> None:
    assert CtyValue.null(CAP) == CtyValue.null(CAP)


def test_a_null_capsule_is_hashable() -> None:
    hash(CtyValue.null(CAP))


def test_an_unknown_capsule_compares_without_reaching_the_payload() -> None:
    assert (CtyValue.unknown(CAP) == CtyValue(CAP, Boxed(1))) is False


def test_marks_still_separate_otherwise_equal_capsules() -> None:
    """__hash__ counts marks, so __eq__ ignoring them broke the hash contract."""
    marked = CtyValue(CAP, Boxed(1)).with_marks({"sensitive"})
    plain = CtyValue(CAP, Boxed(1))
    assert (marked == plain) is False
    # Their hashes may collide -- hash_fn wins outright for a capsule, and
    # unequal values sharing a hash is permitted. Only equal values hashing
    # differently would be a defect.


def test_containers_of_equal_capsules_hash_equally() -> None:
    """The container hash used to render the payload with repr().

    For a class without __repr__ that is a memory address, so two lists holding
    equal payloads compared equal and hashed differently -- and a set kept both.
    """
    cap = _capsule("Bare", Bare)
    list_type = CtyList(element_type=cap)
    left = list_type.validate([CtyValue(cap, Bare(1))])
    right = list_type.validate([CtyValue(cap, Bare(1))])

    assert left == right
    assert hash(left) == hash(right)
    assert len({left, right}) == 1
