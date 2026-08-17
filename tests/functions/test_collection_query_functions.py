#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for collection query functions (contains, keys, values, hasindex, index, etc.)."""

import pytest

from pyvider.cty import (
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import contains, hasindex, index, keys, values


class TestContains:
    def test_contains_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert contains(lst, CtyString().validate("a")).raw_value is True
        assert contains(lst, CtyString().validate("c")).raw_value is False

    def test_contains_set(self) -> None:
        s = CtySet(element_type=CtyString()).validate({"a", "b"})
        assert contains(s, CtyString().validate("a")).raw_value is True
        assert contains(s, CtyString().validate("c")).raw_value is False

    def test_contains_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString())).validate(("a", "b"))
        assert contains(t, CtyString().validate("a")).raw_value is True
        assert contains(t, CtyString().validate("c")).raw_value is False

    def test_contains_refuses_a_null_and_defers_an_unknown(self) -> None:
        CtyList(element_type=CtyString()).validate(["a", "b"])
        with pytest.raises(CtyFunctionError):
            contains(CtyValue.null(CtyList(element_type=CtyString())), CtyString().validate("a"))
        assert contains(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyString().validate("a"),
        ).is_unknown

    def test_contains_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            contains(CtyString().validate("a"), CtyString().validate("a"))


class TestKeysValues:
    def test_keys_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        assert keys(m).raw_value == ["a", "b"]

    def test_keys_object(self) -> None:
        """A tuple, not a list -- an object's attribute names are fixed by its
        type, so go-cty gives the result one entry per attribute. Ordering and
        the type itself are pinned in test_gocty_stdlib_parity.py."""
        o = CtyObject({"a": CtyString(), "b": CtyString()}).validate({"a": "x", "b": "y"})
        assert keys(o).raw_value == ("a", "b")

    def test_keys_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            keys(CtyValue.null(CtyMap(element_type=CtyString())))
        assert keys(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_keys_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            keys(CtyString().validate("hello"))

    def test_values_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        assert values(m).raw_value == ["x", "y"]

    def test_values_object(self) -> None:
        """Also a tuple: an object's attributes have differing types, and a list
        would have to widen them all to dynamic to hold them."""
        o = CtyObject({"a": CtyString(), "b": CtyString()}).validate({"a": "x", "b": "y"})
        assert values(o).raw_value == ("x", "y")

    def test_values_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            values(CtyValue.null(CtyMap(element_type=CtyString())))
        assert values(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_values_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            values(CtyString().validate("hello"))


class TestHasIndexIndex:
    def test_hasindex_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert hasindex(lst, CtyNumber().validate(0)).raw_value is True
        assert hasindex(lst, CtyNumber().validate(2)).raw_value is False
        assert hasindex(lst, CtyString().validate("a")).raw_value is False

    def test_hasindex_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        assert hasindex(m, CtyString().validate("a")).raw_value is True
        assert hasindex(m, CtyString().validate("b")).raw_value is False
        assert hasindex(m, CtyNumber().validate(0)).raw_value is False

    def test_hasindex_refuses_a_null_and_defers_an_unknown(self) -> None:
        """A null collection used to answer False, which claims it was looked in."""
        lst = CtyList(element_type=CtyString()).validate(["a"])
        zero = CtyNumber().validate(0)

        with pytest.raises(CtyFunctionError):
            hasindex(CtyValue.null(CtyList(element_type=CtyString())), zero)
        with pytest.raises(CtyFunctionError):
            hasindex(lst, CtyValue.null(CtyNumber()))

        assert hasindex(CtyValue.unknown(CtyList(element_type=CtyString())), zero).is_unknown
        assert hasindex(lst, CtyValue.unknown(CtyNumber())).is_unknown

    def test_index_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert index(lst, CtyNumber().validate(1)).raw_value == "b"

    def test_index_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        assert index(m, CtyString().validate("a")).raw_value == "x"

    def test_index_not_found(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a"])
        with pytest.raises(CtyFunctionError, match="key does not exist"):
            index(lst, CtyNumber().validate(1))


# 🌊🪢🔚


class TestContainsUnknownHandling:
    """`contains` must not claim certainty it does not have.

    go-cty tracks unknown elements while scanning: if no element matches
    exactly but some element is unknown, the answer is unknown rather than
    false, because that unknown could still turn out to be the value.

    The break these tests catch: returning a definite False for a collection
    whose contents are not fully known.
    """

    def test_unknown_element_makes_a_miss_unknown(self) -> None:
        """Built through `validate`, as a caller would.

        These cases used to hand-build the CtyValue, which hid something: a
        list reports itself unknown as soon as any element is unknown, and
        `contains` used to return on that flag before looking at the elements
        at all. So the behaviour asserted here was unreachable through the
        public API, and the real answer for every list was "unknown".
        """
        collection = CtyList(element_type=CtyString()).validate(["a", CtyValue.unknown(CtyString())])

        assert collection.is_unknown, "the container flags itself unknown"
        assert contains(collection, CtyString().validate("zzz")).is_unknown

    def test_exact_match_wins_over_an_unknown_element(self) -> None:
        """A definite hit is still definite, even alongside unknowns.

        go-cty's ContainsFunc answers `true` here, and so must this: whatever
        the unknown resolves to cannot un-match an element that already matched.
        """
        collection = CtyList(element_type=CtyString()).validate(["a", CtyValue.unknown(CtyString())])

        result = contains(collection, CtyString().validate("a"))

        assert not result.is_unknown
        assert result.value is True

    def test_a_wholly_unknown_collection_is_undecidable(self) -> None:
        """No elements to scan, so nothing can be concluded."""
        collection = CtyValue.unknown(CtyList(element_type=CtyString()))

        assert contains(collection, CtyString().validate("a")).is_unknown

    def test_fully_known_collection_still_answers_definitely(self) -> None:
        collection = CtyList(element_type=CtyString()).validate(["a", "b"])

        assert contains(collection, CtyString().validate("b")).value is True
        assert contains(collection, CtyString().validate("z")).value is False

    def test_element_that_is_known_but_holds_an_unknown_is_undecided(self) -> None:
        """`is_unknown` answers only for the top level.

        An object with an unknown attribute is itself known, so testing
        `element.is_unknown` lets it fall through to `==`, which answers with a
        plain bool and reports a definite miss. What that attribute resolves to
        could still make the element equal to the value being searched for.
        """
        obj = CtyObject(attribute_types={"a": CtyString()})
        collection = CtyList(element_type=obj).validate([obj.validate({"a": CtyValue.unknown(CtyString())})])

        result = contains(collection, obj.validate({"a": CtyString().validate("z")}))

        assert result.is_unknown

    def test_a_needle_holding_an_unknown_is_undecided(self) -> None:
        """The value searched for gets the same treatment as the elements."""
        obj = CtyObject(attribute_types={"a": CtyString()})
        collection = CtyList(element_type=obj).validate([obj.validate({"a": CtyString().validate("z")})])

        result = contains(collection, obj.validate({"a": CtyValue.unknown(CtyString())}))

        assert result.is_unknown


class TestIsWhollyKnown:
    """go-cty's `Value.IsWhollyKnown`: unknown anywhere inside counts."""

    def test_a_known_scalar_is_wholly_known(self) -> None:
        assert CtyString().validate("a").is_wholly_known()

    def test_an_unknown_is_not(self) -> None:
        assert not CtyValue.unknown(CtyString()).is_wholly_known()

    def test_a_null_is_wholly_known(self) -> None:
        """Null is a known absence, not an open question."""
        assert CtyValue.null(CtyString()).is_wholly_known()

    def test_a_nested_unknown_makes_the_whole_value_not_wholly_known(self) -> None:
        obj = CtyObject(attribute_types={"a": CtyString()})
        outer = CtyList(element_type=obj).validate([obj.validate({"a": CtyValue.unknown(CtyString())})])

        assert not outer.is_unknown
        assert not outer.is_wholly_known()

    def test_an_unknown_inside_a_set_counts(self) -> None:
        """The payload is a frozenset, the container type most walks forget."""
        collection = CtySet(element_type=CtyString()).validate(
            [CtyString().validate("a"), CtyValue.unknown(CtyString())]
        )

        assert not collection.is_wholly_known()

    def test_a_fully_known_nested_value_is_wholly_known(self) -> None:
        inner = CtyList(element_type=CtyString())
        assert CtyList(element_type=inner).validate([inner.validate(["a"])]).is_wholly_known()
