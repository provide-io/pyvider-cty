#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A unified type never carries optional attributes.

Optionality describes a type used as a *constraint* -- "you need not supply
this" -- and `unify` answers with a type for *values*, which either have an
attribute or have null for it. go-cty is careful never to let one reach a
value's type; `_without_optional` already exists here as its
`WithoutOptionalAttributesDeep`, and `convert` already applies it.

`unify` did not, on two paths, and both were the ones that hand back an
*argument* rather than building a result: a single type, and several types that
are all equal. Every other path constructs from unified children and so was
already stripped -- which is why unifying an optional object with a required one
agreed with go-cty, and unifying it with *itself* did not.

It reaches the wire. The optional set is part of what a type serializes as
(`["object", {"a": "string"}, ["a"]]` against `["object", {"a": "string"}]`), and
unification decides the element type of `concat`, `flatten` and every set
operation -- so an element type carrying an optional set is a different type in
Terraform's state, not a different opinion.

Found on 2026-08-20 by `tests/compatibility/test_type_relation_properties.py`,
on its first run, from a type no hand-written table had used. Every expectation
below was read from `soup-go cty unify` against go-cty v1.19.0; these run
without a Go toolchain.
"""

from __future__ import annotations

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
from pyvider.cty.conversion import unify

S, N = CtyString(), CtyNumber()
OPTIONAL = CtyObject(attribute_types={"a": S}, optional_attributes=frozenset({"a"}))
REQUIRED = CtyObject(attribute_types={"a": S})


def optionals_anywhere(cty_type: CtyType[Any]) -> bool:
    """Whether any object in a type still declares an optional attribute."""
    pending: list[CtyType[Any]] = [cty_type]
    while pending:
        current = pending.pop()
        match current:
            case CtyObject():
                if current.optional_attributes:
                    return True
                pending.extend(current.attribute_types.values())
            case CtyList() | CtySet() | CtyMap():
                pending.append(current.element_type)
            case CtyTuple():
                pending.extend(current.element_types)
    return False


class TestTheTwoPathsThatHandBackAnArgument:
    def test_a_single_type_is_stripped(self) -> None:
        """go-cty strips even for one argument, where there is nothing to unify."""
        assert unify([OPTIONAL]) == REQUIRED

    def test_two_equal_types_are_stripped(self) -> None:
        """The all-equal shortcut, which returned the first argument untouched."""
        assert unify([OPTIONAL, OPTIONAL]) == REQUIRED

    @pytest.mark.parametrize(
        ("label", "wrapper"),
        [
            ("a list", lambda inner: CtyList(element_type=inner)),
            ("a set", lambda inner: CtySet(element_type=inner)),
            ("a map", lambda inner: CtyMap(element_type=inner)),
            ("a tuple", lambda inner: CtyTuple(element_types=(inner,))),
            ("an object", lambda inner: CtyObject(attribute_types={"outer": inner})),
        ],
    )
    def test_the_strip_reaches_a_nested_object(self, label: str, wrapper: Any) -> None:
        """`WithoutOptionalAttributesDeep` -- the name says deep, and the
        divergence was first seen through a `map`, not at the top level."""
        nested = wrapper(OPTIONAL)

        unified = unify([nested, nested])

        assert unified == wrapper(REQUIRED), label
        assert not optionals_anywhere(unified), label


class TestWhatAlreadyAgreed:
    """The paths that build a result were right, and must stay right."""

    def test_an_optional_and_a_required_object_unify_to_the_required_one(self) -> None:
        assert unify([OPTIONAL, REQUIRED]) == REQUIRED

    def test_two_objects_with_different_attributes_still_fall_back_to_a_map(self) -> None:
        unified = unify(
            [
                CtyObject(attribute_types={"a": S}, optional_attributes=frozenset({"a"})),
                CtyObject(attribute_types={"b": S}),
            ]
        )

        assert unified == CtyMap(element_type=S)

    @pytest.mark.parametrize(
        ("label", "candidates", "expected"),
        [
            ("two identical primitives", [S, S], S),
            ("a number and a string", [N, S], S),
            (
                "two identical lists",
                [CtyList(element_type=S), CtyList(element_type=S)],
                CtyList(element_type=S),
            ),
            ("a list and a set", [CtyList(element_type=S), CtySet(element_type=S)], CtyList(element_type=S)),
        ],
    )
    def test_an_ordinary_unification_is_unchanged(
        self, label: str, candidates: list[CtyType[Any]], expected: CtyType[Any]
    ) -> None:
        assert unify(candidates) == expected, label

    def test_no_common_type_is_still_none(self) -> None:
        assert unify([CtyList(element_type=S), REQUIRED]) is None


def test_the_invariant_over_every_shape_this_module_builds() -> None:
    """Stated once, as a rule rather than a list of cases."""
    shapes: list[list[CtyType[Any]]] = [
        [OPTIONAL],
        [OPTIONAL, OPTIONAL],
        [OPTIONAL, REQUIRED],
        [CtyList(element_type=OPTIONAL), CtyList(element_type=OPTIONAL)],
        [CtyMap(element_type=OPTIONAL), CtyMap(element_type=OPTIONAL)],
        [CtyTuple(element_types=(OPTIONAL,)), CtyTuple(element_types=(OPTIONAL,))],
        [CtyObject(attribute_types={"x": OPTIONAL}), CtyObject(attribute_types={"x": OPTIONAL})],
    ]

    for candidates in shapes:
        unified = unify(candidates)
        assert unified is not None
        assert not optionals_anywhere(unified), candidates


# 🌊🪢🔚
