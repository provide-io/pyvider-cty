#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The `cty/function` framework itself, apart from any function declared through it.

go-cty tests this separately too (`cty/function/function_test.go`), and for the
same reason: the framework decides arity, type conformance, the null and unknown
policies, mark propagation and the result check for all 83 stdlib functions at
once, so a fault here is 83 faults. The functions' own tests cannot see it,
because they only ever drive one declaration.

Built here from synthetic declarations rather than by reaching for a real stdlib
function, so that each test drives exactly the one property it names.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import CtyBool, CtyDynamic, CtyList, CtyNumber, CtyString, CtyType, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._function import (
    CtyArgumentError,
    CtyFunction,
    CtyFunctionPanicError,
    CtyFunctionSpec,
    CtyParameter,
    refine_not_null,
    static_return_type,
    unpredictable,
)
from pyvider.cty.values.markers import RefinedUnknownValue


def _shout(args: Any, _return_type: CtyType[Any]) -> CtyValue[Any]:
    return CtyString().validate(f"{args[0].value}!")


def _function(
    *,
    params: tuple[CtyParameter, ...] = (CtyParameter("str", CtyString()),),
    var_param: CtyParameter | None = None,
    returns: CtyType[Any] | None = None,
    type_func: Any = None,
    impl: Any = None,
    refine_result: Any = None,
    description: str = "",
) -> CtyFunction:
    """A declaration to test against, defaulting to a one-string-argument shouter."""
    return CtyFunction(
        CtyFunctionSpec(
            params=params,
            var_param=var_param,
            type_func=type_func or static_return_type(returns or CtyString()),
            impl=impl or _shout,
            refine_result=refine_result,
            description=description,
        )
    )


class TestArity:
    def test_too_few_arguments_says_how_many_are_required(self) -> None:
        with pytest.raises(CtyFunctionError, match=r"wrong number of arguments \(1 required; 0 given\)"):
            _function().call([])

    def test_too_many_arguments_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError, match=r"\(1 required; 2 given\)"):
            _function().call([CtyString().validate("a"), CtyString().validate("b")])

    def test_a_variadic_function_says_at_least(self) -> None:
        """go-cty words the two cases differently, because they mean different things."""
        function = _function(var_param=CtyParameter("more", CtyString()))
        with pytest.raises(CtyFunctionError, match=r"at least 1 required; 0 given"):
            function.call([])

    def test_a_variadic_function_takes_any_number_beyond_its_fixed_parameters(self) -> None:
        function = _function(
            var_param=CtyParameter("more", CtyString()),
            impl=lambda args, _t: CtyString().validate("".join(a.value for a in args)),
        )
        result = function.call([CtyString().validate(letter) for letter in "abcd"])
        assert result.raw_value == "abcd"


class TestArgumentPolicy:
    def test_a_null_is_refused_and_the_error_names_its_position(self) -> None:
        with pytest.raises(CtyArgumentError) as raised:
            _function(params=(CtyParameter("a", CtyString()), CtyParameter("b", CtyString()))).call(
                [CtyString().validate("a"), CtyValue.null(CtyString())]
            )
        assert raised.value.index == 1

    def test_a_null_reaches_a_parameter_that_allows_one(self) -> None:
        function = _function(
            params=(CtyParameter("a", CtyString(), allow_null=True),),
            returns=CtyBool(),
            impl=lambda args, _t: CtyBool().validate(args[0].is_null),
        )
        assert function.call([CtyValue.null(CtyString())]).raw_value is True

    def test_an_argument_error_is_still_a_function_error(self) -> None:
        """Callers already catch `CtyFunctionError`; a new hierarchy would slip past them."""
        with pytest.raises(CtyFunctionError):
            _function().call([CtyValue.null(CtyString())])

    def test_a_wrong_type_is_refused_by_position(self) -> None:
        with pytest.raises(CtyArgumentError) as raised:
            _function().call([CtyNumber().validate(1)])
        assert raised.value.index == 0

    def test_conformance_allows_a_dynamic_parameter_to_take_anything(self) -> None:
        function = _function(
            params=(CtyParameter("any", CtyDynamic()),),
            returns=CtyBool(),
            impl=lambda _args, _t: CtyBool().validate(True),
        )
        assert function.call([CtyNumber().validate(1)]).raw_value is True


class TestUnknowns:
    def test_an_unknown_argument_short_circuits_to_an_unknown_of_the_return_type(self) -> None:
        """The payoff of declaring a return type: the unknown is typed, not dynamic.

        Hand-rolled guards in this package returned `unknown(dynamic)`, which
        tells a caller nothing about what the call will eventually produce.
        """
        result = _function(returns=CtyNumber()).call([CtyValue.unknown(CtyString())])

        assert result.is_unknown
        assert result.type.equal(CtyNumber())

    def test_the_implementation_is_not_called_for_an_unknown(self) -> None:
        def explode(_args: Any, _t: CtyType[Any]) -> CtyValue[Any]:
            raise AssertionError("the implementation must not see an unknown here")

        assert _function(impl=explode).call([CtyValue.unknown(CtyString())]).is_unknown

    def test_a_parameter_that_allows_unknowns_gets_them(self) -> None:
        function = _function(
            params=(CtyParameter("a", CtyString(), allow_unknown=True),),
            returns=CtyBool(),
            impl=lambda args, _t: CtyBool().validate(args[0].is_unknown),
        )
        assert function.call([CtyValue.unknown(CtyString())]).raw_value is True

    def test_an_unknown_of_dynamic_type_makes_the_result_dynamic(self) -> None:
        """go-cty's `dynTypeArgs`: too vaguely typed to predict a return type."""
        result = _function(params=(CtyParameter("a", CtyString()),)).call([CtyValue.unknown(CtyDynamic())])

        assert result.is_unknown
        assert isinstance(result.type, CtyDynamic)

    def test_allowing_the_dynamic_type_keeps_the_declared_return_type(self) -> None:
        """`AllowDynamicType` without `AllowUnknown` is a valid and useful combination.

        The implementation still does not run, but the answer is a typed unknown
        rather than a dynamic one, which is what lets a derived value stay
        type-checkable (`function.go:44`).
        """
        function = _function(params=(CtyParameter("a", CtyString(), allow_dynamic_type=True),))
        result = function.call([CtyValue.unknown(CtyDynamic())])

        assert result.is_unknown
        assert result.type.equal(CtyString())

    def test_a_known_dynamic_wrapper_is_transparent(self) -> None:
        """This package's `CtyDynamic` wrapper is representation, not policy.

        go-cty has nothing to unwrap, so a parameter declaring `CtyString` has to
        see through the wrapper to be asking go-cty's question. Fifteen function
        bodies were doing this by hand before 2026-08-17.
        """
        assert _function().call([CtyDynamic().validate("a")]).raw_value == "a!"


class TestMarks:
    def test_marks_are_stripped_from_the_implementation_and_re_applied(self) -> None:
        def refuse_marks(args: Any, _t: CtyType[Any]) -> CtyValue[Any]:
            assert not args[0].marks
            return CtyString().validate(args[0].value)

        result = _function(impl=refuse_marks).call([CtyString().validate("a").mark("sensitive")])

        assert result.marks == frozenset({"sensitive"})

    def test_a_mark_inside_a_collection_reaches_the_result(self) -> None:
        """go-cty collects marks with `UnmarkDeep`, so nesting does not hide one."""
        marked = CtyList(element_type=CtyString()).validate([CtyString().validate("a").mark("secret")])
        function = _function(
            params=(CtyParameter("list", CtyList(element_type=CtyString())),),
            returns=CtyNumber(),
            impl=lambda args, _t: CtyNumber().validate(len(args[0].value)),
        )

        assert function.call([marked]).marks == frozenset({"secret"})

    def test_an_unknown_result_still_carries_the_marks(self) -> None:
        """Losing a mark on the short-circuit path is a silent declassification.

        go-cty finishes iterating the arguments before returning the unknown for
        exactly this reason (`function.go:256`).
        """
        result = _function().call([CtyValue.unknown(CtyString()).mark("sensitive")])

        assert result.is_unknown
        assert result.marks == frozenset({"sensitive"})

    def test_a_parameter_that_allows_marks_sees_them(self) -> None:
        function = _function(
            params=(CtyParameter("a", CtyString(), allow_marked=True),),
            returns=CtyBool(),
            impl=lambda args, _t: CtyBool().validate(bool(args[0].marks)),
        )
        assert function.call([CtyString().validate("a").mark("m")]).raw_value is True

    def test_a_mark_on_a_dynamic_wrapper_survives_unwrapping(self) -> None:
        """Unwrapping the `CtyDynamic` wrapper must move its marks, not drop them.

        Found 2026-08-17 during the stdlib migration: an `allow_marked`
        parameter receives the unwrapped value directly, so a mark carried by
        the wrapper -- go-cty has no wrapper, the mark would be on the value --
        vanished before the implementation ever saw it. A dynamic-typed
        sensitive value was silently declassified by the calling convention.
        """
        function = _function(
            params=(CtyParameter("a", CtyString(), allow_marked=True),),
            returns=CtyBool(),
            impl=lambda args, _t: CtyBool().validate("sensitive" in args[0].marks),
        )

        wrapped = CtyDynamic().validate("a").mark("sensitive")
        assert function.call([wrapped]).raw_value is True

    def test_a_mark_on_a_dynamic_wrapper_reaches_a_stripping_parameter_result(self) -> None:
        """The default path collects off the original argument, so the wrapper's
        mark must land on the result even though the body never sees it."""
        result = _function().call([CtyDynamic().validate("a").mark("sensitive")])

        assert result.raw_value == "a!"
        assert result.marks == frozenset({"sensitive"})


class TestReturnType:
    def test_the_return_type_is_answerable_without_any_value(self) -> None:
        """The capability this framework exists for.

        A language runtime type checks an expression before the values are known,
        which nothing in this package could do before 2026-08-17.
        """
        assert _function(returns=CtyNumber()).return_type([CtyString()]).equal(CtyNumber())

    def test_a_value_dependent_return_type_uses_the_values(self) -> None:
        function = _function(
            params=(CtyParameter("a", CtyString()),),
            type_func=lambda args: CtyNumber() if args[0].is_unknown else CtyBool(),
            impl=lambda _args, _t: CtyBool().validate(True),
        )

        assert function.return_type([CtyString()]).equal(CtyNumber())
        assert function.return_type_for_values([CtyString().validate("a")]).equal(CtyBool())

    def test_asking_the_return_type_refuses_a_bad_call_too(self) -> None:
        """The check runs before the type callback, so a runtime learns early."""
        with pytest.raises(CtyFunctionError):
            _function().return_type([CtyString(), CtyString()])

    def test_a_result_that_breaks_the_declaration_is_reported(self) -> None:
        """go-cty panics here: the function lied about itself, and the caller is
        entitled not to handle that (`function.go:364`)."""
        liar = _function(returns=CtyNumber(), impl=lambda _a, _t: CtyString().validate("not a number"))

        with pytest.raises(CtyFunctionPanicError, match="does not conform"):
            liar.call([CtyString().validate("a")])


class TestPanics:
    def test_an_exception_from_the_implementation_lands_in_the_taxonomy(self) -> None:
        """A bare `TypeError` out of a body would escape `except CtyFunctionError`.

        go-cty recovers a panic and returns it as an ordinary error so a calling
        language runtime never has to deal with panics (`error.go:36`).
        """

        def boom(_args: Any, _t: CtyType[Any]) -> CtyValue[Any]:
            raise TypeError("unhashable type: 'CtyValue[list]'")

        with pytest.raises(CtyFunctionPanicError) as raised:
            _function(impl=boom).call([CtyString().validate("a")])
        assert isinstance(raised.value.__cause__, TypeError)

    def test_an_exception_from_the_type_callback_lands_in_the_taxonomy(self) -> None:
        def boom(_args: Any) -> CtyType[Any]:
            raise KeyError("nope")

        with pytest.raises(CtyFunctionPanicError):
            _function(type_func=boom).call([CtyString().validate("a")])

    def test_a_deliberate_refusal_passes_through_unchanged(self) -> None:
        """A `CtyFunctionError` is the function answering, not the function breaking."""

        def refuse(_args: Any, _t: CtyType[Any]) -> CtyValue[Any]:
            raise CtyFunctionError("substr: offset out of range")

        with pytest.raises(CtyFunctionError, match="offset out of range") as raised:
            _function(impl=refuse).call([CtyString().validate("a")])
        assert not isinstance(raised.value, CtyFunctionPanicError)


class TestRefineResult:
    def test_an_unknown_result_carries_the_declared_refinement(self) -> None:
        """The 75 `RefineResult` callbacks in go-cty's stdlib are why this matters.

        "Unknown" and "unknown but definitely not null" are different answers,
        and Terraform acts on the difference.
        """
        result = _function(refine_result=refine_not_null).call([CtyValue.unknown(CtyString())])

        assert result.is_unknown
        assert result.value.is_known_null is False

    def test_a_known_result_is_returned_untouched(self) -> None:
        """A refinement of a known value is a claim to be checked, not recorded."""
        assert _function(refine_result=refine_not_null).call([CtyString().validate("a")]).raw_value == "a!"

    def test_an_unknown_of_dynamic_type_carries_no_refinement(self) -> None:
        """There is no type yet for a refinement to be about (`function.go:281`)."""
        result = _function(refine_result=refine_not_null).call([CtyValue.unknown(CtyDynamic())])

        assert result.is_unknown
        assert not isinstance(result.value, RefinedUnknownValue)

    def test_a_refinement_the_result_contradicts_is_reported(self) -> None:
        """An inconsistent declaration must fail on the known path too, not only
        when an argument happens to be unknown."""
        function = _function(
            params=(CtyParameter("a", CtyString(), allow_null=True),),
            impl=lambda _a, _t: CtyValue.null(CtyString()),
            refine_result=refine_not_null,
        )

        with pytest.raises(Exception, match="non-null"):
            function.call([CtyValue.null(CtyString())])


class TestIntrospection:
    def test_the_parameters_are_readable(self) -> None:
        function = _function(var_param=CtyParameter("more", CtyNumber()), description="shout")

        assert [param.name for param in function.params] == ["str"]
        assert function.var_param is not None
        assert function.var_param.name == "more"
        assert function.description == "shout"

    def test_descriptions_can_be_replaced_without_changing_behaviour(self) -> None:
        renamed = _function().with_new_descriptions("SHOUT", ["the string"])

        assert renamed.description == "SHOUT"
        assert renamed.params[0].description == "the string"
        assert renamed.call([CtyString().validate("a")]).raw_value == "a!"

    def test_replacing_descriptions_checks_the_count(self) -> None:
        with pytest.raises(CtyFunctionError, match="length 1"):
            _function().with_new_descriptions("x", [])

    def test_a_variadic_parameter_description_is_optional(self) -> None:
        """So adding a variadic parameter does not break an existing caller of
        this method (`function.go:425`)."""
        function = _function(var_param=CtyParameter("more", CtyString(), description="kept"))

        assert function.with_new_descriptions("x", ["a"]).var_param.description == "kept"  # type: ignore[union-attr]
        assert function.with_new_descriptions("x", ["a", "b"]).var_param.description == "b"  # type: ignore[union-attr]

    def test_proxy_calls_positionally(self) -> None:
        assert _function().proxy()(CtyString().validate("a")).raw_value == "a!"


class TestUnpredictable:
    def test_it_keeps_the_signature_and_answers_unknown(self) -> None:
        """go-cty's `Unpredictable` (`unpredictable.go:24`)."""
        wrapped = unpredictable(_function(returns=CtyNumber()))

        result = wrapped.call([CtyString().validate("a")])
        assert result.is_unknown
        assert result.type.equal(CtyNumber())

    def test_it_still_type_checks_its_arguments(self) -> None:
        """It is unpredictable in its value, not in its type behaviour."""
        with pytest.raises(CtyArgumentError):
            unpredictable(_function()).call([CtyNumber().validate(1)])


# 🌊🪢🔚
