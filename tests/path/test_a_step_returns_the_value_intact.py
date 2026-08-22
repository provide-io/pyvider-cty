#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A path step hands back the value it selected, whole.

Two defects met here. A step out of a marked container dropped the container's
marks, the same way a subscript did -- see
`tests/values/test_marks_survive_selection.py` for the go-cty citation.

And a step *through* a `dynamic` wrapper rebuilt its answer as
`CtyValue(result.type, result.value)`, which keeps two of the five fields a
`CtyValue` has. A null came back as `is_null=False, value=None`; an unknown as
`is_unknown=False, value=UNREFINED_UNKNOWN`; a refined unknown as a known value
whose payload was a `RefinedUnknownValue`. None of those three is a value this
library can represent, so the check is internal consistency rather than
go-cty parity: go-cty has no known-dynamic value to compare against, because
`Index` and `GetAttr` on a `DynamicPseudoType` receiver return `DynamicVal`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import AttributePathError
from pyvider.cty.marks import CtyMark
from pyvider.cty.path import CtyPath
from pyvider.cty.refinement import refine
from pyvider.cty.values.markers import RefinedUnknownValue

S, N = CtyString(), CtyNumber()
SENSITIVE = CtyMark("sensitive")
OTHER = CtyMark("other")

LIST = CtyList(element_type=S)
MAP = CtyMap(element_type=S)
OBJECT = CtyObject({"a": S})
TUPLE = CtyTuple((S, N))
SET = CtySet(element_type=S)


def _marked_traversals() -> list[tuple[str, CtyValue[object], CtyPath]]:
    return [
        ("list", LIST.validate(["x"]).mark(SENSITIVE), CtyPath.index(0)),
        ("tuple", TUPLE.validate(("x", 1)).mark(SENSITIVE), CtyPath.index(0)),
        ("map", MAP.validate({"k": "x"}).mark(SENSITIVE), CtyPath.key("k")),
        ("object", OBJECT.validate({"a": "x"}).mark(SENSITIVE), CtyPath.get_attr("a")),
        ("set", SET.validate(["x"]).mark(SENSITIVE), CtyPath.key(S.validate("x"))),
    ]


@pytest.mark.parametrize(
    ("kind", "container", "path"), _marked_traversals(), ids=lambda p: p if isinstance(p, str) else ""
)
class TestAStepCarriesTheContainersMarks:
    def test_the_selected_value_is_marked(self, kind: str, container: CtyValue[object], path: CtyPath) -> None:
        assert path.apply_path(container).marks == frozenset({SENSITIVE})

    def test_the_selected_value_is_otherwise_unchanged(
        self, kind: str, container: CtyValue[object], path: CtyPath
    ) -> None:
        assert path.apply_path(container).value == "x"


class TestMarksAccumulate:
    def test_an_elements_own_mark_survives_alongside_the_containers(self) -> None:
        marked = LIST.validate([S.validate("x").mark(OTHER)]).mark(SENSITIVE)
        assert CtyPath.index(0).apply_path(marked).marks == frozenset({SENSITIVE, OTHER})

    def test_a_two_step_path_unions_both_levels(self) -> None:
        inner = OBJECT.validate({"a": "x"}).mark(OTHER)
        outer = CtyList(element_type=OBJECT).validate([inner]).mark(SENSITIVE)
        selected = CtyPath.index(0).child("a").apply_path(outer)
        assert selected.marks == frozenset({SENSITIVE, OTHER})


class TestAnUnknownContainerHandsBackAMarkedUnknown:
    def test_index_into_an_unknown_list(self) -> None:
        selected = CtyPath.index(0).apply_path(CtyValue.unknown(LIST).mark(SENSITIVE))
        assert selected.is_unknown and selected.marks == frozenset({SENSITIVE})

    def test_key_into_an_unknown_map(self) -> None:
        selected = CtyPath.key("k").apply_path(CtyValue.unknown(MAP).mark(SENSITIVE))
        assert selected.is_unknown and selected.marks == frozenset({SENSITIVE})


class TestThroughADynamicWrapper:
    """The receiver is `dynamic` and the payload is a concrete value."""

    def test_a_null_element_stays_null(self) -> None:
        wrapped = CtyDynamic().validate(LIST.validate([CtyValue.null(S)]))
        selected = CtyPath.index(0).apply_path(wrapped)
        assert selected.is_null
        assert selected.value is None

    def test_an_unknown_element_stays_unknown(self) -> None:
        wrapped = CtyDynamic().validate(LIST.validate([CtyValue.unknown(S)]))
        selected = CtyPath.index(0).apply_path(wrapped)
        assert selected.is_unknown

    def test_a_refined_unknown_keeps_its_refinement(self) -> None:
        refined = refine(CtyValue.unknown(S)).string_prefix("sec").new_value()
        wrapped = CtyDynamic().validate(LIST.validate([refined]))
        selected = CtyPath.index(0).apply_path(wrapped)
        assert selected.is_unknown
        assert isinstance(selected.value, RefinedUnknownValue)
        # Compared against the refinement that went in rather than the literal
        # "sec": `string_prefix` trims a trailing grapheme that could still be
        # extended, so what survives is what was stored, not what was asked for.
        assert selected.value == refined.value

    def test_a_marked_element_keeps_its_mark(self) -> None:
        wrapped = CtyDynamic().validate(LIST.validate([S.validate("x").mark(OTHER)]))
        assert CtyPath.index(0).apply_path(wrapped).marks == frozenset({OTHER})

    def test_a_marked_wrapper_marks_what_it_hands_back(self) -> None:
        wrapped = CtyDynamic().validate(LIST.validate(["x"])).mark(SENSITIVE)
        assert CtyPath.index(0).apply_path(wrapped).marks == frozenset({SENSITIVE})

    def test_a_null_map_element_stays_null(self) -> None:
        wrapped = CtyDynamic().validate(MAP.validate({"k": CtyValue.null(S)}))
        selected = CtyPath.key("k").apply_path(wrapped)
        assert selected.is_null
        assert selected.value is None

    def test_an_unknown_map_element_stays_unknown(self) -> None:
        wrapped = CtyDynamic().validate(MAP.validate({"k": CtyValue.unknown(S)}))
        assert CtyPath.key("k").apply_path(wrapped).is_unknown

    def test_a_known_element_comes_through_unharmed(self) -> None:
        wrapped = CtyDynamic().validate(LIST.validate(["x"]))
        selected = CtyPath.index(0).apply_path(wrapped)
        assert selected.type.equal(S)
        assert selected.value == "x"
        assert not selected.is_null and not selected.is_unknown


class TestASetIsKeyedByCtyIdentity:
    """A set element keys itself, so the lookup has to use the set's own identity.

    `set_order.identity_key` -- `makeSetHashBytes` plus the canonical key -- is
    what `CtySet.validate` de-duplicates on. Python equality is not the same
    relation, and the gap is a signed zero: `Decimal("-0") == Decimal("0")`,
    while go-cty hashes them to `-0` and `0` and keeps both. Confirmed against
    the oracle, which visits two elements and gives them two paths::

        soup-go cty walk --type '["set","number"]' '[-0,0]'
        "visits":[..., {"path":[{"index":-0}],...}, {"path":[{"index":0}],...}]
    """

    NUMBERS = CtySet(element_type=N)

    def test_go_cty_keeps_both_zeros_and_so_does_this(self) -> None:
        both = self.NUMBERS.validate([Decimal("-0"), Decimal("0")])
        assert len(cast("tuple[CtyValue[object], ...]", both.value)) == 2

    def test_the_negative_zero_is_found_by_the_negative_zero(self) -> None:
        both = self.NUMBERS.validate([Decimal("-0"), Decimal("0")])
        selected = CtyPath.key(N.validate(Decimal("-0"))).apply_path(both)
        assert cast(Decimal, selected.value).is_signed()

    def test_the_positive_zero_is_found_by_the_positive_zero(self) -> None:
        both = self.NUMBERS.validate([Decimal("-0"), Decimal("0")])
        selected = CtyPath.key(N.validate(Decimal("0"))).apply_path(both)
        assert not cast(Decimal, selected.value).is_signed()

    def test_a_positive_zero_is_absent_from_a_set_holding_only_a_negative_one(self) -> None:
        only_negative = self.NUMBERS.validate([Decimal("-0")])
        with pytest.raises(AttributePathError):
            CtyPath.key(N.validate(Decimal("0"))).apply_path(only_negative)

    def test_a_marked_key_still_finds_its_element(self) -> None:
        """`identity_key` strips marks, as go-cty's hashing does, so a marked
        key asks after the same element. It used to find nothing at all."""
        selected = CtyPath.key(S.validate("x").mark(SENSITIVE)).apply_path(SET.validate(["x"]))
        assert selected.value == "x"

    def test_a_marked_key_marks_what_it_finds(self) -> None:
        selected = CtyPath.key(S.validate("x").mark(SENSITIVE)).apply_path(SET.validate(["x"]))
        assert selected.marks == frozenset({SENSITIVE})

    def test_a_marked_unknown_key_marks_the_unknown_it_gets_back(self) -> None:
        selected = CtyPath.key(CtyValue.unknown(S).mark(SENSITIVE)).apply_path(SET.validate(["x"]))
        assert selected.is_unknown
        assert selected.marks == frozenset({SENSITIVE})

    def test_the_key_and_the_receiver_both_contribute(self) -> None:
        marked_set = SET.validate(["x"]).mark(OTHER)
        selected = CtyPath.key(S.validate("x").mark(SENSITIVE)).apply_path(marked_set)
        assert selected.marks == frozenset({SENSITIVE, OTHER})

    def test_an_unmarked_key_leaves_the_element_alone(self) -> None:
        assert CtyPath.key(S.validate("x")).apply_path(SET.validate(["x"])).marks == frozenset()

    def test_an_unfound_key_is_unknown_when_the_set_holds_an_unknown(self) -> None:
        """One of the unknowns could still turn out to be the element asked for,
        so "absent" would assert more than the data supports."""
        partly = SET.validate(["x", CtyValue.unknown(S)])
        assert CtyPath.key(S.validate("absent")).apply_path(partly).is_unknown

    def test_that_unknown_carries_the_keys_marks_too(self) -> None:
        partly = SET.validate(["x", CtyValue.unknown(S)])
        selected = CtyPath.key(S.validate("absent").mark(SENSITIVE)).apply_path(partly)
        assert selected.is_unknown
        assert selected.marks == frozenset({SENSITIVE})

    def test_the_step_types_a_set_as_its_element_type(self) -> None:
        assert CtyPath.key(S.validate("x")).apply_path_type(SET).equal(S)

    def test_a_key_that_is_not_a_cty_value_matches_nothing(self) -> None:
        """As before: `CtyValue.__eq__` returns `NotImplemented` against a raw
        operand, so a bare `"x"` never matched an element either."""
        with pytest.raises(AttributePathError):
            CtyPath.key("x").apply_path(SET.validate(["x"]))


class TestAWhollyUnknownDynamicAttribute:
    """`GetAttrStep` had no answer for an unknown `dynamic`, where the other two steps did."""

    def test_an_unknown_dynamic_yields_an_unknown(self) -> None:
        selected = CtyPath.get_attr("a").apply_path(CtyValue.unknown(CtyDynamic()))
        assert selected.is_unknown

    def test_it_agrees_with_what_apply_path_type_promises(self) -> None:
        assert CtyPath.get_attr("a").apply_path_type(CtyDynamic()).equal(CtyDynamic())
        assert CtyPath.get_attr("a").apply_path(CtyValue.unknown(CtyDynamic())).type.equal(CtyDynamic())

    def test_it_agrees_with_the_other_two_steps(self) -> None:
        unknown_dynamic = CtyValue.unknown(CtyDynamic())
        assert CtyPath.index(0).apply_path(unknown_dynamic).is_unknown
        assert CtyPath.key("k").apply_path(unknown_dynamic).is_unknown

    def test_a_marked_unknown_dynamic_keeps_its_mark(self) -> None:
        selected = CtyPath.get_attr("a").apply_path(CtyValue.unknown(CtyDynamic()).mark(SENSITIVE))
        assert selected.marks == frozenset({SENSITIVE})

    def test_an_unknown_object_still_answers_with_the_attributes_own_type(self) -> None:
        """The `CtyObject` branch is checked first on purpose: an unknown object
        already knows what type the attribute has, and a blanket unknown
        short-circuit would flatten that to `dynamic`."""
        selected = CtyPath.get_attr("a").apply_path(CtyValue.unknown(OBJECT))
        assert selected.is_unknown
        assert selected.type.equal(S)


class TestGetAttrTraversesADynamicWrapperToo:
    """`IndexStep` and `KeyStep` both step through a wrapper; `GetAttrStep` did not."""

    def test_an_attribute_is_reachable_through_a_wrapper(self) -> None:
        wrapped = CtyDynamic().validate(OBJECT.validate({"a": "x"}))
        assert CtyPath.get_attr("a").apply_path(wrapped).value == "x"

    def test_a_null_attribute_stays_null(self) -> None:
        wrapped = CtyDynamic().validate(CtyObject({"a": S}).validate({"a": CtyValue.null(S)}))
        selected = CtyPath.get_attr("a").apply_path(wrapped)
        assert selected.is_null
        assert selected.value is None

    def test_a_marked_wrapper_marks_the_attribute(self) -> None:
        wrapped = CtyDynamic().validate(OBJECT.validate({"a": "x"})).mark(SENSITIVE)
        assert CtyPath.get_attr("a").apply_path(wrapped).marks == frozenset({SENSITIVE})


# 🌊🪢🔚
