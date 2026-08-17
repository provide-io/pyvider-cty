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
    SIGNATURES,
    sethaselement,
    setintersection,
    setsubtract,
    setsymmetricdifference,
    setunion,
)
from pyvider.cty.values.markers import RefinedUnknownValue

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

    def test_has_element_of_the_wrong_type_is_absent_rather_than_an_error(self) -> None:
        """A set cannot hold an element of any type but its own.

        2026-08-17: `sethaselement` used to delegate to `contains`, which is
        `ContainsFunc` and answers a different question -- it accepts a list or
        a tuple too. `SetHasElementFunc`'s whole body is `args[0].HasElement(...)`,
        which settles a mismatched element type as a definite *absence*
        (`value_ops.go:1088`). The oracle agrees: `sethaselement(set(string),
        number)` answers false, not an error.
        """
        assert sethaselement(S("a"), CtyNumber().validate(1)).value is False

    def test_has_element_sees_past_an_unknown_element_to_a_hit(self) -> None:
        """A hit cannot be un-hit by whatever the unknown turns out to be.

        A *miss* against the same set is undecided rather than false, because
        the unknown could still turn out to be the element asked about
        (`value_ops.go:1081`). Both answers confirmed against the oracle.
        """
        partly_unknown = STRING_SET.validate(["a", CtyValue.unknown(CtyString())])

        assert sethaselement(partly_unknown, CtyString().validate("a")).value is True
        assert sethaselement(partly_unknown, CtyString().validate("z")).is_unknown


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

        # An unknown, not a set with elements in it: the operation never ran.
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
        """go-cty's parameter type is set(dynamic); a list is refused, not converted.

        2026-08-17: this matched `"set required"`, the text of
        `ERR_SET_OP_ARG_MUST_BE_SET` raised by a hand-rolled check inside the
        function. The check is now the framework's per-parameter conformance
        test against `cty.Set(cty.DynamicPseudoType)` (`stdlib/set.go:38`), and
        its wording is go-cty's own: the oracle answers `set of dynamic
        required, but received list of string` for this exact call. The text
        moved *towards* go-cty rather than away from it.
        """
        with pytest.raises(CtyFunctionError, match="set of dynamic required"):
            setunion(S("a"), bad)

    def test_no_arguments(self) -> None:
        """2026-08-17: this matched `"at least one set must be provided"`.

        `setunion` declares one fixed parameter and a `VarParam`
        (`stdlib/set.go:35`), so too few arguments is an arity error rather than
        something the implementation gets to say. go-cty's message for this call
        is `wrong number of arguments (at least 1 required; 0 given)`, which the
        framework now reproduces verbatim, so the guard inside the function --
        and `ERR_SET_OP_REQUIRES_ONE_SET` with it -- became unreachable.
        """
        with pytest.raises(CtyFunctionError, match=r"at least 1 required; 0 given"):
            setunion()

    def test_a_dynamic_wrapper_around_a_set_is_seen_through(self) -> None:
        wrapped = CtyDynamic().validate(STRING_SET.validate(["b"]))

        assert elements_of(setunion(S("a"), wrapped)) == {"a", "b"}

    def test_an_unsettled_dynamic_is_refused_rather_than_unwrapped(self) -> None:
        """`cty.DynamicVal` in a set slot is an error, not an unknown set.

        Every set parameter declares `AllowDynamicType` (`stdlib/set.go:39`), so
        a value of undecided type passes the conformance check and reaches
        `setOperationReturnType`, which calls `Type.ElementType()` on
        `DynamicPseudoType` and panics; go-cty's framework recovers that into an
        ordinary error (`function.go:226`) and the oracle answers `panic in
        function implementation: not a collection type`. Both implementations
        therefore refuse, and only the wording differs.

        2026-08-17: this used to be a test about the hand-rolled dynamic-unwrap
        loop, which needed both of its conditions -- a mutation run turned its
        `and` into an `or` and nothing failed. That loop now lives once in the
        framework, and the value still has to be refused rather than descended
        into.
        """
        with pytest.raises(CtyFunctionError, match="set required"):
            setunion(S("a"), CtyValue.unknown(CtyDynamic()))


class TestSetOperationRefinements:
    """All five carry `RefineResult: refineNonNull`, and none used to.

    Added 2026-08-17. `set.go` declares it on every one of the five
    (lines 27, 48, 69, 90, 111); this package declared none, so an unknown
    answer arrived saying only "unknown" where go-cty's says "unknown, and not
    null" -- information Terraform acts on. Verified against the oracle, which
    answers `{"is_known_null": false}` for each of these calls.
    """

    @pytest.mark.parametrize("operation", [setunion, setintersection, setsubtract, setsymmetricdifference])
    def test_an_unknown_set_answer_is_known_not_null(self, operation: object) -> None:
        result = operation(CtyValue.unknown(STRING_SET), S("a"))  # type: ignore[operator]

        assert result.is_unknown
        assert result.type == STRING_SET
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_an_unknown_sethaselement_answer_is_known_not_null(self) -> None:
        result = sethaselement(CtyValue.unknown(STRING_SET), CtyString().validate("a"))

        assert result.is_unknown
        assert result.type == CtyBool()
        assert result.value == RefinedUnknownValue(is_known_null=False)


class TestSetOperationArities:
    """`setsubtract` is the one that is not variadic.

    `set.go` gives it two fixed parameters and no `VarParam` (line 77), where
    the other three take one fixed set and a variadic tail. Every one of the
    four used to accept any number of arguments here, so `setsubtract(a, b, c)`
    quietly subtracted twice; go-cty answers `wrong number of arguments
      (2 required; 3 given)`, which is what the oracle returns.
    """

    def test_setsubtract_takes_exactly_two_sets(self) -> None:
        with pytest.raises(CtyFunctionError, match=r"2 required; 3 given"):
            setsubtract(S("a"), S("b"), S("c"))  # type: ignore[call-arg]

    @pytest.mark.parametrize(
        ("operation", "expected"),
        [
            # Chosen so the third argument changes every one of the three
            # answers: with only the first two they are {a,b,c}, {b} and {a,c}.
            (setunion, {"a", "b", "c"}),
            (setintersection, {"b"}),
            (setsymmetricdifference, {"a", "b", "c"}),
        ],
    )
    def test_the_other_three_take_a_variadic_tail(self, operation: object, expected: set[str]) -> None:
        answer = operation(S("a", "b"), S("b", "c"), S("b"))  # type: ignore[operator]

        assert elements_of(answer) == expected


class TestSetOperationReturnTypesArePredictable:
    """The declared signature answers what a call would return, with no values.

    Impossible before the framework landed: `setOperationReturnType` is
    go-cty's `Spec.Type` and had nowhere to live, so the element type was
    decided inside the body and could not be asked about in advance.
    """

    def test_a_union_of_two_string_sets_is_predicted(self) -> None:
        assert SIGNATURES["setunion"].return_type([STRING_SET, STRING_SET]) == STRING_SET

    def test_a_mixed_union_is_predicted_to_widen(self) -> None:
        predicted = SIGNATURES["setunion"].return_type([STRING_SET, CtySet(element_type=CtyBool())])

        assert predicted == STRING_SET

    def test_sethaselement_always_predicts_bool(self) -> None:
        assert SIGNATURES["sethaselement"].return_type([STRING_SET, CtyString()]) == CtyBool()


class TestSetOperationsWidenTheirElements:
    """This class used to be `TestSetOperationUnifyGap` and asserted the gap.

    `unify` had no primitive widening rule, so `setunion(set(string),
    set(bool))` came back a `set(dynamic)` holding the two originals rather than
    a `set(string)` holding `"true"`. It was pinned here as "at least written
    down", which is how a divergence becomes furniture. `unify` is now a port of
    go-cty's, so these assert the widening instead.
    """

    def test_a_mixed_union_widens_to_a_set_of_string(self) -> None:
        mixed = setunion(S("a"), CtySet(element_type=CtyBool()).validate([True]))

        assert mixed.type == CtySet(element_type=CtyString())
        assert {element.raw_value for element in mixed.value} == {"a", "true"}

    def test_the_elements_are_converted_not_merely_collected(self) -> None:
        mixed = setunion(S("a"), NUMBER_SET.validate([1]))

        assert mixed.type == CtySet(element_type=CtyString())
        assert {element.raw_value for element in mixed.value} == {"a", "1"}

    def test_elements_with_no_common_type_are_refused(self) -> None:
        """go-cty's `setOperationReturnType` errors rather than answering.

        A `set(dynamic)` used to come back here, which is the same value `unify`
        produced when it *did* have an answer -- so "these have nothing in
        common" and "these unify to dynamic" were indistinguishable.
        """
        with pytest.raises(CtyFunctionError):
            setunion(NUMBER_SET.validate([1]), CtySet(element_type=CtyBool()).validate([True]))


# 🌊🪢🔚
