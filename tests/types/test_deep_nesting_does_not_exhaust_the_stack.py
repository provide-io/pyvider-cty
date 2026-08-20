#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Nothing a deeply nested type or value can be asked costs a frame per level.

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

`equal` was the one that reached CI, because it sits on the construction path.
Five more surfaces had the same shape and were found by measuring rather than
by reading: `__eq__` on a type (attrs-generated, so it never routed through
`equal`), `__hash__`, `usable_as`, `__str__`, and `CtyValue.__eq__`. All six
walk now, off one decomposition -- `_structure`, which each container answers
once and which equality, hashing and rendering all read.

`__repr__` is deliberately still recursive. It is a debugger surface and reaches
no error path: a refusal spells its type with `str()`, which is why that one is
here and `repr` is not.

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
    CtyValue,
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

    value: CtyValue[Any] = CtyString().validate("bottom")
    for _ in range(DEPTH):
        value = CtyTuple(element_types=(value.type,)).validate((value,))

    assert value.type.equal(nested_tuple())


class TestEverythingElseADeepTypeIsAsked:
    """The five surfaces `equal` was hiding, each measured at depth 400 on 3.11.

    None was failing CI, because none is on the construction path. Two of them
    are hot -- `usable_as` runs in conversion, and a type's `__eq__` runs on
    every `lru_cache` lookup in `can_convert_unsafe` -- and one of them can turn
    a refusal into a panic, because an error message spells the type it refused.
    """

    @pytest.mark.parametrize(("label", "builder"), BUILDERS, ids=[case[0] for case in BUILDERS])
    def test_two_deep_types_compare_with_the_equality_operator(self, label: str, builder: Any) -> None:
        """`==` is attrs-generated per subclass, so it never went through `equal`
        and had to be fixed in its own right."""
        left, right = builder(), builder()

        with no_room_to_recurse():
            assert left == right, label
            assert (left != right) is False, label

    @pytest.mark.parametrize(("label", "builder"), BUILDERS, ids=[case[0] for case in BUILDERS])
    def test_a_deep_type_can_be_hashed(self, label: str, builder: Any) -> None:
        with no_room_to_recurse():
            assert hash(builder()) == hash(builder()), label

    @pytest.mark.parametrize(("label", "builder"), BUILDERS, ids=[case[0] for case in BUILDERS])
    def test_a_deep_type_is_usable_as_itself(self, label: str, builder: Any) -> None:
        with no_room_to_recurse():
            assert builder().usable_as(builder()), label

    def test_a_deep_type_can_be_spelled(self) -> None:
        """The one that can turn a refusal into a panic: `CtyConversionError`
        formats the type it refused into its message."""
        with no_room_to_recurse():
            spelled = str(nested_list())

        assert spelled.startswith("list(list(")
        assert spelled.endswith("string" + ")" * DEPTH)

    def test_a_deep_value_compares_with_the_equality_operator(self) -> None:
        """One layer up, and the hotter of the two: a container's payload is a
        tuple of `CtyValue`s, so comparing payloads came straight back."""
        deep: CtyValue[Any] = CtyString().validate("bottom")
        for _ in range(DEPTH):
            deep = CtyTuple(element_types=(deep.type,)).validate((deep,))

        other: CtyValue[Any] = CtyString().validate("bottom")
        for _ in range(DEPTH):
            other = CtyTuple(element_types=(other.type,)).validate((other,))

        with no_room_to_recurse():
            assert deep == other
            assert hash(deep) == hash(other)


class TestTheHashStillAgreesWithEquality:
    """Python requires `a == b` to imply `hash(a) == hash(b)`.

    `CtyObject.__hash__` used to break the *spirit* of that on purpose -- a
    comment reading "for nested objects, use a simpler hash to avoid recursion",
    which put two objects differing only in a nested attribute's type into one
    bucket. Legal, and a workaround for exactly the defect this file is about.
    It is gone; the hash descends as far as equality does.
    """

    @pytest.mark.parametrize(("label", "builder"), BUILDERS, ids=[case[0] for case in BUILDERS])
    def test_equal_types_hash_alike(self, label: str, builder: Any) -> None:
        assert hash(builder(4)) == hash(builder(4)), label

    def test_two_objects_differing_only_deep_inside_now_hash_apart(self) -> None:
        """The case the old shallow hash could not see."""
        one = CtyObject(attribute_types={"a": CtyObject(attribute_types={"b": CtyString()})})
        two = CtyObject(attribute_types={"a": CtyObject(attribute_types={"b": CtyNumber()})})

        assert one != two
        assert hash(one) != hash(two)

    @pytest.mark.parametrize(
        ("label", "left", "right"),
        [
            ("element type", CtyList(element_type=CtyString()), CtyList(element_type=CtyNumber())),
            ("arity", CtyTuple(element_types=(CtyString(),)), CtyTuple(element_types=())),
            (
                "optionality",
                CtyObject(attribute_types={"a": CtyString()}),
                CtyObject(attribute_types={"a": CtyString()}, optional_attributes=frozenset({"a"})),
            ),
            ("kind", CtyList(element_type=CtyString()), CtySet(element_type=CtyString())),
        ],
    )
    def test_a_difference_reaches_the_hash(self, label: str, left: CtyType[Any], right: CtyType[Any]) -> None:
        assert left != right, label
        assert hash(left) != hash(right), label

    def test_a_type_is_still_usable_as_a_dictionary_key(self) -> None:
        """`can_convert_unsafe` is `lru_cache`d on two types, so this is a hot
        path and not a curiosity."""
        table = {CtyList(element_type=CtyString()): "a", CtyList(element_type=CtyNumber()): "b"}

        assert table[CtyList(element_type=CtyString())] == "a"
        assert table[CtyList(element_type=CtyNumber())] == "b"


class TestWhatIsStillRecursive:
    def test_repr_is_left_alone_on_purpose(self) -> None:
        """A debugger surface that reaches no error path -- a refusal spells its
        type with `str()`. Asserted so that the decision is visible rather than
        an oversight, and so that fixing it later is a deliberate change.
        """
        shallow = CtyList(element_type=CtyString())

        assert repr(shallow) == "CtyList(element_type=CtyString())"


# 🌊🪢🔚
