#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Comparing two deeply nested types costs a bounded number of Python frames.

`CtyTuple.equal` and `CtyObject.equal` recursed, at two frames a level, and
`equal` is on the construction path -- `validate` compares an element's type
against the one the container declares -- so a 400-deep tuple could not even be
*built*, let alone compared. It raised `RecursionError` on Python 3.11 and
passed on 3.13, on the strength of nothing but where each interpreter happens to
put its frames: 800 frames against a limit of 1000. `requires-python` is 3.11,
and CI runs it, so this was red on every platform.

The collection types had already met this and half-fixed it, flattening the
linear chain of same-kind containers and recording in a comment that branching
shapes were "bounded by the schema's own breadth". A single-element tuple nested
400 deep is not bounded by breadth at all, which is the case that came back.

These tests do not depend on which interpreter runs them. They lower the
recursion limit to just above the stack the test itself is standing on, so a
recursive implementation cannot pass by having room to spare.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import sys
from typing import Any

import pytest

from pyvider.cty import (
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)

DEPTH = 400
HEADROOM = 60


def _stack_depth() -> int:
    depth, frame = 0, sys._getframe()
    while frame is not None:
        depth += 1
        frame = frame.f_back
    return depth


@contextmanager
def no_room_to_recurse() -> Iterator[None]:
    """A limit that leaves this test its own stack and nothing else.

    A recursive comparison needs two frames per level of nesting; this leaves it
    `HEADROOM`, so it fails on any interpreter rather than on the unlucky one.
    """
    original = sys.getrecursionlimit()
    sys.setrecursionlimit(_stack_depth() + HEADROOM)
    try:
        yield
    finally:
        sys.setrecursionlimit(original)


def nested_tuple(depth: int = DEPTH) -> CtyType[Any]:
    cty_type: CtyType[Any] = CtyString()
    for _ in range(depth):
        cty_type = CtyTuple(element_types=(cty_type,))
    return cty_type


def nested_object(depth: int = DEPTH) -> CtyType[Any]:
    cty_type: CtyType[Any] = CtyString()
    for _ in range(depth):
        cty_type = CtyObject(attribute_types={"a": cty_type})
    return cty_type


def nested_list(depth: int = DEPTH) -> CtyType[Any]:
    cty_type: CtyType[Any] = CtyString()
    for _ in range(depth):
        cty_type = CtyList(element_type=cty_type)
    return cty_type


def nested_mixture(depth: int = DEPTH) -> CtyType[Any]:
    """Alternating kinds, so no single flattening rule can shortcut the walk."""
    cty_type: CtyType[Any] = CtyString()
    for level in range(depth):
        match level % 4:
            case 0:
                cty_type = CtyList(element_type=cty_type)
            case 1:
                cty_type = CtyTuple(element_types=(cty_type,))
            case 2:
                cty_type = CtyMap(element_type=cty_type)
            case _:
                cty_type = CtyObject(attribute_types={"a": cty_type})
    return cty_type


BUILDERS = [
    ("tuple", nested_tuple),
    ("object", nested_object),
    ("list", nested_list),
    ("alternating kinds", nested_mixture),
]


@pytest.mark.parametrize(("label", "builder"), BUILDERS, ids=[case[0] for case in BUILDERS])
def test_two_equal_deep_types_compare_without_the_stack(label: str, builder: Any) -> None:
    left, right = builder(), builder()

    with no_room_to_recurse():
        assert left.equal(right), label


@pytest.mark.parametrize(("label", "builder"), BUILDERS, ids=[case[0] for case in BUILDERS])
def test_a_difference_at_the_bottom_is_still_found(label: str, builder: Any) -> None:
    """Iterating must not turn "unequal" into "equal" by giving up early."""
    left, right = builder(), builder()
    deeper = builder(DEPTH + 1)

    with no_room_to_recurse():
        assert not left.equal(deeper), label
        assert left.equal(right), label


def test_a_difference_in_the_leaf_type_is_found() -> None:
    """The leaves are the last thing the walk reaches, so they are the easiest
    thing for a broken traversal to skip."""
    tail: CtyType[Any] = CtyNumber()
    for _ in range(DEPTH):
        tail = CtyTuple(element_types=(tail,))

    with no_room_to_recurse():
        assert not nested_tuple().equal(tail)


def test_a_difference_in_one_branch_of_many_is_found() -> None:
    """Branching, not only depth: one attribute of ten differs at the bottom."""

    def wide(bottom: CtyType[Any]) -> CtyType[Any]:
        attributes: dict[str, CtyType[Any]] = {f"a{index}": CtyString() for index in range(10)}
        attributes["a7"] = bottom
        return CtyObject(attribute_types=attributes)

    with no_room_to_recurse():
        assert wide(nested_tuple()).equal(wide(nested_tuple()))
        assert not wide(nested_tuple()).equal(wide(nested_list()))


def test_optionality_still_decides_before_any_child_is_compared() -> None:
    """A rule of `CtyObject.equal` that has nothing to do with the children."""
    attributes: dict[str, CtyType[Any]] = {"a": CtyString()}

    with no_room_to_recurse():
        assert not CtyObject(attribute_types=attributes).equal(
            CtyObject(attribute_types=attributes, optional_attributes=frozenset({"a"}))
        )


def test_a_mismatched_arity_decides_before_any_child_is_compared() -> None:
    with no_room_to_recurse():
        assert not CtyTuple(element_types=(CtyString(),)).equal(
            CtyTuple(element_types=(CtyString(), CtyString()))
        )


@pytest.mark.parametrize(
    ("label", "left", "right"),
    [
        ("list against set", CtyList(element_type=CtyString()), CtySet(element_type=CtyString())),
        ("map against object", CtyMap(element_type=CtyString()), CtyObject(attribute_types={})),
        ("tuple against list", CtyTuple(element_types=()), CtyList(element_type=CtyString())),
        ("container against a primitive", CtyList(element_type=CtyString()), CtyString()),
    ],
)
def test_a_different_kind_is_never_equal(label: str, left: CtyType[Any], right: CtyType[Any]) -> None:
    assert not left.equal(right), label
    assert not right.equal(left), label


def test_a_deep_value_can_still_be_built() -> None:
    """The reason this was a build failure and not only a comparison one.

    `validate` compares the element's type against the container's, so the
    recursion was reached by constructing the value at all.
    """
    from pyvider.cty import CtyValue

    value: CtyValue[Any] = CtyString().validate("bottom")
    for _ in range(DEPTH):
        value = CtyTuple(element_types=(value.type,)).validate((value,))

    assert value.type.equal(nested_tuple())


# 🌊🪢🔚
