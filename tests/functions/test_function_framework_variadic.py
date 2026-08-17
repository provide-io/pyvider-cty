#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Every framework property, asserted for the *variadic* parameter.

The sibling module drives each property through a fixed parameter, and an
adversarial review on 2026-08-17 proved that was a narrower population than the
claims: a mutation making `_param_at` answer `allow_marked=True` (or
`allow_null=True, allow_unknown=True`) for every variadic slot left all 39 of
those tests green -- meaning variadic marks could be silently declassified, and
the variadic null refusal and unknown short-circuit could vanish, without a
single failure. go-cty tests the variadic half separately for the same reason
(`function_test.go:412-571`).
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import CtyBool, CtyDynamic, CtyNumber, CtyString, CtyType, CtyValue
from pyvider.cty.functions._function import (
    CtyArgumentError,
    CtyFunction,
    CtyFunctionSpec,
    CtyParameter,
    refine_not_null,
    static_return_type,
)
from pyvider.cty.functions._marks import collect_marks_deep
from pyvider.cty.values.markers import RefinedUnknownValue


def _joiner(
    *,
    var_param: CtyParameter,
    impl: Any = None,
    type_func: Any = None,
    refine_result: Any = None,
) -> CtyFunction:
    """A purely variadic function, defaulting to joining its arguments."""
    return CtyFunction(
        CtyFunctionSpec(
            name="joiner",
            params=(),
            var_param=var_param,
            type_func=type_func or static_return_type(CtyString()),
            impl=impl or (lambda args, _t: CtyString().validate("".join(str(a.value) for a in args))),
            refine_result=refine_result,
        )
    )


class TestVariadicArgumentPolicy:
    def test_a_null_is_refused_and_the_error_names_its_position(self) -> None:
        with pytest.raises(CtyArgumentError) as raised:
            _joiner(var_param=CtyParameter("s", CtyString())).call(
                [CtyString().validate("a"), CtyValue.null(CtyString())]
            )
        assert raised.value.index == 1

    def test_a_null_reaches_a_variadic_parameter_that_allows_one(self) -> None:
        function = _joiner(
            var_param=CtyParameter("s", CtyString(), allow_null=True),
            impl=lambda args, _t: CtyString().validate(str(sum(a.is_null for a in args))),
        )
        assert function.call([CtyValue.null(CtyString()), CtyString().validate("x")]).raw_value == "1"

    def test_a_wrong_type_is_refused_with_its_absolute_position(self) -> None:
        """go-cty reports the variadic-relative index here (`function.go:216`
        passes `i` where the null check uses `realI`) -- a bug in go-cty, since
        its own null check two lines up disagrees with it about the same
        argument. The absolute index is the deliberate divergence."""
        function = CtyFunction(
            CtyFunctionSpec(
                name="mixed",
                params=(CtyParameter("first", CtyString()),),
                var_param=CtyParameter("rest", CtyString()),
                type_func=static_return_type(CtyString()),
                impl=lambda args, _t: args[0],
            )
        )
        with pytest.raises(CtyArgumentError) as raised:
            function.call([CtyString().validate("a"), CtyString().validate("b"), CtyNumber().validate(1)])
        assert raised.value.index == 2


class TestVariadicUnknowns:
    def test_an_unknown_short_circuits_to_an_unknown_of_the_return_type(self) -> None:
        def explode(_args: Any, _t: CtyType[Any]) -> CtyValue[Any]:
            raise AssertionError("the implementation must not run")

        result = _joiner(var_param=CtyParameter("s", CtyString()), impl=explode).call(
            [CtyString().validate("a"), CtyValue.unknown(CtyString())]
        )

        assert result.is_unknown
        assert result.type.equal(CtyString())

    def test_a_variadic_parameter_that_allows_unknowns_gets_them(self) -> None:
        function = _joiner(
            var_param=CtyParameter("s", CtyString(), allow_unknown=True),
            impl=lambda args, _t: CtyString().validate(str(sum(a.is_unknown for a in args))),
        )
        assert function.call([CtyValue.unknown(CtyString())]).raw_value == "1"

    def test_an_unknown_dynamic_makes_the_result_dynamic(self) -> None:
        result = _joiner(var_param=CtyParameter("s", CtyString())).call(
            [CtyString().validate("a"), CtyValue.unknown(CtyDynamic())]
        )

        assert result.is_unknown
        assert isinstance(result.type, CtyDynamic)

    def test_allowing_the_dynamic_type_keeps_the_declared_return_type(self) -> None:
        function = _joiner(var_param=CtyParameter("s", CtyString(), allow_dynamic_type=True))
        result = function.call([CtyValue.unknown(CtyDynamic())])

        assert result.is_unknown
        assert result.type.equal(CtyString())

    def test_arguments_after_a_dynamic_one_are_not_checked(self) -> None:
        """go-cty returns at the first inexactly typed argument
        (`function.go:208-211`), so a null after a `DynamicVal` is not an
        error -- the call is already decided to be `DynamicVal`."""
        result = _joiner(var_param=CtyParameter("s", CtyString())).call(
            [CtyValue.unknown(CtyDynamic()), CtyValue.null(CtyString()), CtyNumber().validate(1)]
        )

        assert result.is_unknown
        assert isinstance(result.type, CtyDynamic)


class TestVariadicMarks:
    def test_marks_are_stripped_from_the_implementation_and_re_applied(self) -> None:
        def refuse_marks(args: Any, _t: CtyType[Any]) -> CtyValue[Any]:
            assert all(not a.marks for a in args)
            return CtyString().validate("ok")

        result = _joiner(var_param=CtyParameter("s", CtyString()), impl=refuse_marks).call(
            [CtyString().validate("a"), CtyString().validate("b").mark("sensitive")]
        )

        assert result.marks == frozenset({"sensitive"})

    def test_marks_survive_the_unknown_short_circuit(self) -> None:
        """go-cty finishes iterating every argument before returning the early
        unknown, precisely so a variadic mark is not dropped (`function.go:256`)."""
        result = _joiner(var_param=CtyParameter("s", CtyString())).call(
            [CtyValue.unknown(CtyString()), CtyString().validate("b").mark("sensitive")]
        )

        assert result.is_unknown
        assert result.marks == frozenset({"sensitive"})

    def test_a_variadic_parameter_that_allows_marks_sees_them(self) -> None:
        function = _joiner(
            var_param=CtyParameter("s", CtyString(), allow_marked=True),
            impl=lambda args, _t: CtyString().validate(str(sum(bool(a.marks) for a in args))),
        )
        result = function.call([CtyString().validate("a").mark("m"), CtyString().validate("b")])

        assert result.raw_value == "1"
        # The implementation owns propagation now, so the framework must not
        # have re-applied anything on its behalf.
        assert result.marks == frozenset()

    def test_an_allow_marked_arguments_marks_do_not_leak_onto_the_early_unknown(self) -> None:
        """go-cty's `params-partial-marks` (`function_test.go:524`): marks are
        auto-collected only from parameters that do *not* declare
        `AllowMarked` -- an `AllowMarked` argument's marks are the
        implementation's job, and the implementation never ran."""
        function = CtyFunction(
            CtyFunctionSpec(
                name="partial",
                params=(CtyParameter("a", CtyString(), allow_marked=True),),
                var_param=CtyParameter("rest", CtyString()),
                type_func=static_return_type(CtyString()),
                impl=lambda args, _t: args[0],
            )
        )

        result = function.call(
            [
                CtyString().validate("a").mark("owned-by-impl"),
                CtyString().validate("b").mark("special"),
                CtyValue.unknown(CtyString()),
            ]
        )

        assert result.is_unknown
        assert result.marks == frozenset({"special"})


class TestTypeFuncSeesUnmarkedArguments:
    """go-cty's two `Type`-must-not-see-marks cases (`function_test.go:125-180`).

    A `Type` implementation that inspects values could otherwise leak a mark
    into a type decision, so the framework unmarks before the type check for
    every parameter not declaring `allow_marked` -- fixed and variadic alike.
    """

    @staticmethod
    def _marked_refusing_type_func(args: Any) -> CtyType[Any]:
        for argument in args:
            assert not collect_marks_deep(argument), "the type callback saw a mark"
        return CtyString()

    def test_a_fixed_parameters_marks_are_invisible_to_the_type_callback(self) -> None:
        function = CtyFunction(
            CtyFunctionSpec(
                name="probe",
                params=(CtyParameter("a", CtyString()),),
                type_func=self._marked_refusing_type_func,
                impl=lambda args, _t: args[0],
            )
        )
        result = function.call([CtyString().validate("a").mark("sensitive")])

        assert result.marks == frozenset({"sensitive"})

    def test_a_variadic_parameters_marks_are_invisible_to_the_type_callback(self) -> None:
        function = _joiner(
            var_param=CtyParameter("s", CtyString()),
            type_func=self._marked_refusing_type_func,
        )
        result = function.call([CtyString().validate("a"), CtyString().validate("b").mark("sensitive")])

        assert result.marks == frozenset({"sensitive"})


class TestDynamicResultRefinement:
    """The `_refine` guard, driven through the *result* type rather than an argument.

    The guard exists for a `type_func` that answers `CtyDynamic()` from
    perfectly concrete arguments -- `jsondecode` of an unknown string is the
    canonical case -- and until 2026-08-17 no test drove that path: reverting
    the guard to gate on the arguments left every test green.
    """

    def test_an_unknown_of_a_dynamic_return_type_is_not_refined(self) -> None:
        function = _joiner(
            var_param=CtyParameter("s", CtyString()),
            type_func=lambda _args: CtyDynamic(),
            refine_result=refine_not_null,
        )
        result = function.call([CtyValue.unknown(CtyString())])

        assert result.is_unknown
        assert not isinstance(result.value, RefinedUnknownValue)

    def test_an_unknown_of_a_concrete_type_from_the_same_shape_is_refined(self) -> None:
        """The sibling that keeps the guard honest: go-cty still refines an
        unknown `list(dynamic)` -- the type merely *contains* dynamic, and only
        exactly-`DynamicPseudoType` skips (`function.go:281`)."""
        from pyvider.cty import CtyList

        function = _joiner(
            var_param=CtyParameter("s", CtyString()),
            type_func=lambda _args: CtyList(element_type=CtyDynamic()),
            refine_result=refine_not_null,
        )
        result = function.call([CtyValue.unknown(CtyString())])

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        assert result.value.is_known_null is False


class TestVariadicIntrospection:
    def test_descriptions_accept_none_for_a_parameterless_function(self) -> None:
        """go-cty's own tests pass `nil` here (`function_test.go:217`)."""
        function = CtyFunction(
            CtyFunctionSpec(
                name="nullary",
                params=(),
                var_param=CtyParameter("rest", CtyBool()),
                type_func=static_return_type(CtyBool()),
                impl=lambda _args, _t: CtyBool().validate(True),
            )
        )
        renamed = function.with_new_descriptions("described", None)

        assert renamed.description == "described"
        assert renamed.var_param is not None
        assert renamed.var_param.description == ""


# 🌊🪢🔚
