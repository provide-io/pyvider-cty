#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`CtyValue.equals` must be able to decline to decide.

`==` answers with a plain bool, which forces a verdict even when the values do
not support one: an object whose attribute is unknown compared against one
whose attribute is `"z"` is neither equal nor unequal, because that attribute
could still resolve to `"z"`.

Mirrors go-cty's `Value.Equals`. The break these tests catch: any comparison
that returns a definite answer where the data does not support one, or an
undecided answer where it does.
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
    CtyValue,
)
from pyvider.cty.marks import CtyMark

SENSITIVE = CtyMark("sensitive")


def s(v: str) -> CtyValue[Any]:
    return CtyString().validate(v)


def verdict(result: CtyValue[Any]) -> object:
    return "unknown" if result.is_unknown else result.value


OBJ = CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})


class TestScalars:
    def test_equal_and_unequal_scalars_are_decided(self) -> None:
        assert verdict(s("a").equals(s("a"))) is True
        assert verdict(s("a").equals(s("b"))) is False

    def test_nulls_are_equal_regardless_of_type(self) -> None:
        """go-cty: 'Nulls are always equal, regardless of type'."""
        assert verdict(CtyValue.null(CtyString()).equals(CtyValue.null(CtyNumber()))) is True

    def test_null_against_a_known_value_is_false(self) -> None:
        assert verdict(CtyValue.null(CtyString()).equals(s("a"))) is False

    def test_two_unknowns_are_undecided(self) -> None:
        unknown = CtyValue.unknown(CtyString())
        assert verdict(unknown.equals(unknown)) == "unknown"

    def test_an_unknown_against_a_known_value_is_undecided(self) -> None:
        assert verdict(CtyValue.unknown(CtyString()).equals(s("a"))) == "unknown"

    def test_an_unknown_against_a_null_is_undecided(self) -> None:
        """The unknown may yet resolve to null, and nulls are equal."""
        assert verdict(CtyValue.unknown(CtyString()).equals(CtyValue.null(CtyString()))) == "unknown"

    def test_an_unknown_of_a_different_type_is_definitely_unequal(self) -> None:
        """No null is in play, so no resolution of the unknown can make these equal."""
        assert verdict(CtyValue.unknown(CtyString()).equals(CtyNumber().validate(1))) is False

    def test_different_types_are_unequal(self) -> None:
        assert verdict(s("1").equals(CtyNumber().validate(1))) is False
        assert verdict(CtyBool().validate(True).equals(s("true"))) is False


class TestNestedUnknowns:
    """The reason this exists: `is_unknown` answers only for the top level."""

    def test_an_object_with_an_unknown_attribute_is_undecided(self) -> None:
        lhs = OBJ.validate({"a": CtyValue.unknown(CtyString()), "b": s("x")})
        rhs = OBJ.validate({"a": s("z"), "b": s("x")})

        assert not lhs.is_unknown, "the object itself is known; only an attribute is not"
        assert verdict(lhs.equals(rhs)) == "unknown"

    def test_a_known_attribute_that_differs_still_rules_the_value_out(self) -> None:
        """The precision this buys over 'anything containing an unknown is undecided'.

        The unknown attribute cannot rescue a comparison that a *known*
        attribute has already settled.
        """
        lhs = OBJ.validate({"a": CtyValue.unknown(CtyString()), "b": s("x")})
        rhs = OBJ.validate({"a": s("z"), "b": s("DIFFERENT")})

        assert verdict(lhs.equals(rhs)) is False

    def test_all_attributes_known_and_equal_is_decided(self) -> None:
        lhs = OBJ.validate({"a": s("z"), "b": s("x")})
        rhs = OBJ.validate({"a": s("z"), "b": s("x")})

        assert verdict(lhs.equals(rhs)) is True


class TestContainers:
    def test_lists_of_different_length_are_unequal(self) -> None:
        lst = CtyList(element_type=CtyString())
        assert verdict(lst.validate(["a"]).equals(lst.validate(["a", "b"]))) is False

    def test_lists_compare_elementwise(self) -> None:
        lst = CtyList(element_type=CtyString())
        assert verdict(lst.validate(["a", "b"]).equals(lst.validate(["a", "b"]))) is True
        assert verdict(lst.validate(["a", "b"]).equals(lst.validate(["a", "c"]))) is False

    def test_a_list_with_an_unknown_element_is_undecided(self) -> None:
        lst = CtyList(element_type=CtyString())
        partial = CtyValue(vtype=lst, value=(s("a"), CtyValue.unknown(CtyString())))

        assert verdict(partial.equals(lst.validate(["a", "b"]))) == "unknown"

    def test_a_list_with_an_unknown_element_is_still_ruled_out_by_a_known_one(self) -> None:
        lst = CtyList(element_type=CtyString())
        partial = CtyValue(vtype=lst, value=(s("a"), CtyValue.unknown(CtyString())))

        assert verdict(partial.equals(lst.validate(["DIFFERENT", "b"]))) is False

    def test_maps_compare_by_key(self) -> None:
        m = CtyMap(element_type=CtyString())
        assert verdict(m.validate({"k": "v"}).equals(m.validate({"k": "v"}))) is True
        assert verdict(m.validate({"k": "v"}).equals(m.validate({"k": "w"}))) is False
        assert verdict(m.validate({"k": "v"}).equals(m.validate({"other": "v"}))) is False

    def test_tuples_compare_elementwise(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyNumber()))
        assert verdict(t.validate(["a", 1]).equals(t.validate(["a", 1]))) is True
        assert verdict(t.validate(["a", 1]).equals(t.validate(["a", 2]))) is False

    def test_sets_compare_by_membership_not_order(self) -> None:
        st = CtySet(element_type=CtyString())
        assert verdict(st.validate(["a", "b"]).equals(st.validate(["b", "a"]))) is True
        assert verdict(st.validate(["a"]).equals(st.validate(["b"]))) is False

    def test_a_set_containing_an_unknown_is_undecided(self) -> None:
        """An unknown element changes how many distinct members a set has."""
        st = CtySet(element_type=CtyString())
        partial = CtyValue(vtype=st, value=frozenset({s("a"), CtyValue.unknown(CtyString())}))

        assert verdict(partial.equals(st.validate(["a", "b"]))) == "unknown"

    def test_nested_containers_compare_at_depth(self) -> None:
        inner = CtyList(element_type=CtyString())
        outer = CtyList(element_type=inner)
        assert verdict(outer.validate([["a"]]).equals(outer.validate([["a"]]))) is True
        assert verdict(outer.validate([["a"]]).equals(outer.validate([["b"]]))) is False


class TestDynamic:
    def test_a_dynamic_wrapper_compares_as_what_it_wraps(self) -> None:
        assert verdict(CtyDynamic().validate("a").equals(CtyDynamic().validate("a"))) is True
        assert verdict(CtyDynamic().validate("a").equals(CtyDynamic().validate("b"))) is False


class TestMarks:
    """Asking whether a sensitive value equals something yields a sensitive answer."""

    def test_the_result_carries_both_operands_marks(self) -> None:
        result = s("a").mark(SENSITIVE).equals(s("a"))

        assert verdict(result) is True
        assert SENSITIVE in result.marks

    def test_marks_do_not_change_the_verdict(self) -> None:
        """The comparison runs on unmarked copies, as go-cty's does."""
        assert verdict(s("a").mark(SENSITIVE).equals(s("a"))) is True
        assert verdict(s("a").mark(SENSITIVE).equals(s("b"))) is False

    def test_a_nested_mark_reaches_the_result(self) -> None:
        lst = CtyList(element_type=CtyString())
        marked = lst.validate([s("a").mark(SENSITIVE)])

        result = marked.equals(lst.validate(["a"]))

        assert verdict(result) is True
        assert SENSITIVE in result.marks


@pytest.mark.parametrize(
    ("lhs", "rhs"),
    [
        (CtyValue.null(CtyString()), CtyValue.null(CtyString())),
        (CtyValue.unknown(CtyString()), CtyValue.unknown(CtyString())),
    ],
)
def test_equals_never_raises_on_degenerate_operands(lhs: CtyValue[Any], rhs: CtyValue[Any]) -> None:
    assert isinstance(lhs.equals(rhs), CtyValue)
