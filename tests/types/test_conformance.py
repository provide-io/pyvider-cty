#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`conformance_errors` — go-cty's `Type.TestConformance`.

`usable_as` answers whether a type fits; this answers *why not* and *where*. The
distinction is the whole point: a provider telling a practitioner "object
required, but received object" has told them nothing, and that is what a boolean
leaves you able to say.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    conformance_errors,
)

S, N, B, D = CtyString(), CtyNumber(), CtyBool(), CtyDynamic()


def messages(given: CtyType[Any], want: CtyType[Any]) -> list[str]:
    return [str(error) for error in conformance_errors(given, want)]


class TestConformant:
    @pytest.mark.parametrize(
        ("given", "want"),
        [
            (S, S),
            (CtyList(element_type=S), CtyList(element_type=S)),
            (CtyObject({"a": S}), CtyObject({"a": S})),
            # `want` being dynamic admits anything, at any depth.
            (CtyList(element_type=S), D),
            (CtyObject({"a": S}), CtyObject({"a": D})),
            (D, D),
        ],
        ids=str,
    )
    def test_no_errors(self, given: CtyType[Any], want: CtyType[Any]) -> None:
        assert conformance_errors(given, want) == []

    def test_conformance_is_not_convertibility(self) -> None:
        """`convert` would manage this; conformance is about shape, not coercion."""
        assert messages(S, N) == ["number required, but received string"]

    def test_conformance_is_not_symmetric(self) -> None:
        """Dynamic accepts anything as `want` and satisfies nothing as `given`."""
        assert conformance_errors(S, D) == []
        assert messages(D, S) == ["string required, but received dynamic"]


class TestObjects:
    def test_both_directions_are_reported(self) -> None:
        """An extra attribute is as much a non-conformance as a missing one.

        Reporting only the missing ones leaves a caller adding attributes
        forever without being told the extras are also wrong.
        """
        assert messages(CtyObject({"a": S, "x": S}), CtyObject({"a": S, "b": N})) == [
            "unsupported attribute 'x'",
            "missing required attribute 'b'",
        ]

    def test_a_shared_attribute_is_compared_by_type(self) -> None:
        assert messages(CtyObject({"a": S}), CtyObject({"a": N})) == [
            "a: number required, but received string"
        ]

    def test_nesting_composes_the_path(self) -> None:
        given = CtyObject({"o": CtyObject({"i": S})})
        want = CtyObject({"o": CtyObject({"i": N})})

        assert messages(given, want) == ["o.i: number required, but received string"]

    def test_several_faults_are_all_reported(self) -> None:
        """One call, every problem -- that is what distinguishes it from `usable_as`."""
        given = CtyObject({"a": S, "b": S, "extra": B})
        want = CtyObject({"a": N, "b": B, "missing": S})

        assert len(messages(given, want)) == 4


class TestTuples:
    def test_a_length_mismatch_stops_at_the_length(self) -> None:
        """Comparing positions after the arity is wrong reports noise."""
        assert messages(CtyTuple(element_types=(S,)), CtyTuple(element_types=(S, N))) == [
            "2 elements are required, but got 1"
        ]

    def test_positions_are_compared_by_index(self) -> None:
        assert messages(CtyTuple(element_types=(S, S)), CtyTuple(element_types=(S, N))) == [
            "[1]: number required, but received string"
        ]


class TestCollections:
    @pytest.mark.parametrize("kind", [CtyList, CtySet, CtyMap], ids=lambda k: k.__name__)
    def test_the_element_type_is_compared(self, kind: type) -> None:
        assert messages(kind(element_type=S), kind(element_type=N)) == [
            "[*]: number required, but received string"
        ]

    def test_the_element_marker_is_not_an_index(self) -> None:
        """`[*]` rather than `[0]`, because go-cty's step holds an *unknown* key.

        A concrete index would point at an element that need not exist -- the
        complaint is about the element type, not about any element.
        """
        assert "[0]" not in messages(CtyList(element_type=S), CtyList(element_type=N))[0]

    def test_different_kinds_do_not_recurse(self) -> None:
        assert messages(CtyList(element_type=S), CtyMap(element_type=S)) == ["map required, but received list"]

    def test_nesting_composes_through_a_collection(self) -> None:
        given = CtyList(element_type=CtyObject({"a": S}))
        want = CtyList(element_type=CtyObject({"a": N}))

        assert messages(given, want) == ["[*].a: number required, but received string"]


# 🌊🪢🔚
