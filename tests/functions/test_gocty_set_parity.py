#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The five set operations against go-cty's `cty/function/stdlib/set.go`.

The three the oracle exposes are pinned against it in the compatibility sweep.
Here are the parts the harness cannot reach: `setsymmetricdifference` and
`sethaselement`, which it does not expose at all, and the unknown handling,
which is the only place these five differ from one another in substance.
"""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtySet,
    CtyString,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    sethaselement,
    setintersection,
    setsubtract,
    setsymmetricdifference,
    setunion,
)

STRING_SET = CtySet(element_type=CtyString())
NUMBER_SET = CtySet(element_type=CtyNumber())


def S(*elements: str) -> CtyValue[frozenset[object]]:
    return STRING_SET.validate(list(elements))


def elements_of(value: CtyValue[object]) -> set[object]:
    return {element.value for element in value.value}


class TestSetOperations:
    def test_union(self) -> None:
        assert elements_of(setunion(S("a"), S("b"))) == {"a", "b"}

    def test_union_of_one_set(self) -> None:
        assert elements_of(setunion(S("a"))) == {"a"}

    def test_union_of_several_sets(self) -> None:
        assert elements_of(setunion(S("a"), S("b"), S("c"), S("a"))) == {"a", "b", "c"}

    def test_intersection(self) -> None:
        assert elements_of(setintersection(S("a", "b"), S("b", "c"))) == {"b"}

    def test_a_disjoint_intersection_is_empty(self) -> None:
        empty = setintersection(S("a"), S("b"))

        assert elements_of(empty) == set()
        assert empty.type == STRING_SET

    def test_subtract(self) -> None:
        assert elements_of(setsubtract(S("a", "b"), S("b"))) == {"a"}

    def test_symmetric_difference(self) -> None:
        """Not exposed by the oracle harness, so this follows `set.go` directly."""
        assert elements_of(setsymmetricdifference(S("a", "b"), S("b", "c"))) == {"a", "c"}

    def test_has_element(self) -> None:
        assert sethaselement(S("a"), CtyString().validate("a")).value is True
        assert sethaselement(S("a"), CtyString().validate("z")).value is False


class TestSetOperationTypes:
    def test_matching_element_types_are_kept(self) -> None:
        assert setunion(S("a"), S("b")).type == STRING_SET

    def test_two_empty_sets(self) -> None:
        result = setunion(S(), S())

        assert result.type == STRING_SET
        assert elements_of(result) == set()

    def test_an_empty_dynamic_set_does_not_drag_the_result_to_dynamic(self) -> None:
        """It converts to any concrete set type, so go-cty leaves it out of unification."""
        result = setunion(S("a"), CtySet(element_type=CtyDynamic()).validate([]))

        assert result.type == STRING_SET

    def test_all_empty_dynamic_sets_give_a_dynamic_set(self) -> None:
        empty_dynamic = CtySet(element_type=CtyDynamic()).validate([])

        assert setunion(empty_dynamic, empty_dynamic).type == CtySet(element_type=CtyDynamic())


class TestSetOperationUnknowns:
    """Only union tolerates an unknown element.

    Everywhere else, learning what the unknown is can remove elements from the
    result or change its length, so no partial answer is safe to give -- which
    is what go-cty's `allowUnknowns` flag encodes.
    """

    def unknown_element_set(self) -> CtyValue[object]:
        return STRING_SET.validate([CtyValue.unknown(CtyString())])

    def test_union_keeps_the_elements_it_was_given(self) -> None:
        """Union does the work rather than refusing, unlike the other three.

        The result still reports itself unknown, but for a different reason and
        from somewhere else: `CtySet.validate` propagates an unknown element up
        to the set, where go-cty's `SetVal` gives a known set holding an unknown.
        That is a container-level divergence -- the same inconsistency already
        recorded for lists against objects -- not something these functions
        decide. What is checked here is that union computed a result at all.
        """
        result = setunion(S("a"), self.unknown_element_set())

        assert len(result.value) == 2
        assert "a" in {element.value for element in result.value}

    @pytest.mark.parametrize("operation", [setintersection, setsubtract, setsymmetricdifference])
    def test_the_others_refuse_to_compute(self, operation: object) -> None:
        result = operation(S("a"), self.unknown_element_set())  # type: ignore[operator]

        # An unrefined unknown, not a set with elements in it: the operation
        # never ran.
        assert result.is_unknown
        assert not isinstance(result.value, frozenset)
        assert result.type == STRING_SET


class TestSetOperationRejects:
    @pytest.mark.parametrize(
        "bad",
        [
            CtyList(element_type=CtyString()).validate(["a"]),
            CtyString().validate("a"),
        ],
    )
    def test_an_argument_that_is_not_a_set(self, bad: CtyValue[object]) -> None:
        """go-cty's parameter type is set(dynamic); a list is refused, not converted."""
        with pytest.raises(CtyFunctionError, match="set required"):
            setunion(S("a"), bad)

    def test_no_arguments(self) -> None:
        with pytest.raises(CtyFunctionError, match="at least one set"):
            setunion()

    def test_a_dynamic_wrapper_around_a_set_is_seen_through(self) -> None:
        wrapped = CtyDynamic().validate(STRING_SET.validate(["b"]))

        assert elements_of(setunion(S("a"), wrapped)) == {"a", "b"}


class TestSetOperationUnifyGap:
    """A known divergence, and it is in `unify` rather than in these functions.

    go-cty unifies a mixture of primitives with `convert.UnifyUnsafe`, which
    widens everything to string, so `setunion(set(string), set(bool))` is a
    `set(string)` containing `"true"`. This package's `unify` has no primitive
    widening rule and answers dynamic. Pinned in the sweep as a strict xfail;
    asserted here so the current behaviour is at least written down.
    """

    def test_a_mixed_union_is_a_set_of_dynamic_here(self) -> None:
        mixed = setunion(S("a"), CtySet(element_type=CtyBool()).validate([True]))

        assert mixed.type == CtySet(element_type=CtyDynamic())

    def test_the_elements_survive_untouched(self) -> None:
        mixed = setunion(S("a"), NUMBER_SET.validate([1]))

        assert {element.raw_value for element in mixed.value} == {"a", 1}


# 🌊🪢🔚
