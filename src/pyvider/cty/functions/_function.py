#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/function` framework: a function's shape, declared rather than re-derived.

A go-cty stdlib function is a `Spec`: a list of `Parameter`s each saying what
type it accepts and whether it tolerates a null, an unknown, a dynamic type or a
mark; a `Type` callback giving the return type from the arguments; an `Impl` that
runs only once every declared precondition holds; and an optional `RefineResult`
describing what is true of the answer even when the answer is unknown.

This package hand-rolled all of that inside the function bodies -- 98 `is_null`
tests, 103 `is_unknown` tests and 15 copies of the dynamic-unwrap loop, no two
quite alike. Every argument-handling divergence found against go-cty so far came
from a body re-deriving policy: `contains`, `equal`, `length`, `merge`, `sort`,
`zipmap`, `formatlist` and both decoders. Declaring it makes that class of bug
unrepresentable rather than fixed one at a time.

Three things this buys that were previously impossible:

  - **Return-type prediction.** `CtyFunction.return_type([...])` answers what a
    call would produce without making it, which is how a language runtime type
    checks an expression before any value is known. Nothing here could do that.
  - **Correctly typed unknowns.** The short-circuit returns `unknown(ret_type)`,
    so `upper(unknown)` is an unknown *string* rather than an unknown dynamic.
  - **Refined unknowns.** go-cty's stdlib carries 75 `RefineResult` callbacks;
    this package carried none, so it answered "unknown" where go-cty answers
    "unknown, and not null" -- information Terraform acts on.

Why this lives in `pyvider.cty.functions` rather than a sibling
`pyvider.cty.function`: go-cty can afford `cty/function` beside
`cty/function/stdlib` because the stdlib is nested inside the framework package.
Here the stdlib *is* `pyvider.cty.functions`, so a singular sibling would differ
from it by one character, and importing the wrong one fails with an
`AttributeError` several frames from the typo. The public names are re-exported
from `pyvider.cty` instead.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
import inspect
from typing import Any

import attrs

from pyvider.cty.config.defaults import ERR_ARGUMENT_MUST_NOT_BE_NULL
from pyvider.cty.conformance import conformance_errors
from pyvider.cty.exceptions import CtyError, CtyFunctionError, CtyValidationError
from pyvider.cty.functions._marks import _arg_marks
from pyvider.cty.marks import _strip
from pyvider.cty.refinement import RefinementBuilder, refine
from pyvider.cty.types import CtyDynamic, CtyType
from pyvider.cty.values import CtyValue

__all__ = [
    "CtyArgumentError",
    "CtyFunction",
    "CtyFunctionPanicError",
    "CtyFunctionSpec",
    "CtyParameter",
    "ImplFunc",
    "RefineResult",
    "TypeFunc",
    "refine_not_null",
    "static_return_type",
    "unpredictable",
]

# go-cty's `TypeFunc`. Any of the values may be unknown, even where the
# parameters do not admit unknowns, because a return type has to be computable
# before the values are (`function.go:88`).
TypeFunc = Callable[[Sequence[CtyValue[Any]]], CtyType[Any]]

# go-cty's `ImplFunc`. The second argument is the type the `TypeFunc` already
# decided, passed along so a generic function need not compute it twice
# (`function.go:98`).
ImplFunc = Callable[[Sequence[CtyValue[Any]], CtyType[Any]], CtyValue[Any]]

# go-cty's `Spec.RefineResult` (`function.go:53`).
RefineResult = Callable[[RefinementBuilder], RefinementBuilder]


class CtyArgumentError(CtyFunctionError):
    """go-cty's `function.ArgError`: an error about one argument, by position.

    A subclass rather than a new hierarchy, so every existing
    `except CtyFunctionError` still catches it. `index` is zero-based, as
    go-cty's is (`error.go:13`).
    """

    def __init__(self, index: int, message: str, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.index = index


class CtyFunctionPanicError(CtyFunctionError):
    """A function implementation raised something outside the library's taxonomy.

    go-cty recovers a panic out of `Type` or `Impl` and returns it as an ordinary
    error, so a calling language runtime never has to deal with panics
    (`error.go:36`). The Python equivalent of a panic here is any exception that
    is not a `CtyError` -- a bare `TypeError` out of `__hash__`, an
    `IndexError`, a `KeyError` -- which would otherwise escape a caller's
    `except CtyFunctionError` and reach Terraform as a crash.

    The original is chained, so nothing is hidden from a traceback.
    """


def static_return_type(return_type: CtyType[Any], /) -> TypeFunc:
    """A `TypeFunc` for a function whose return type does not vary.

    go-cty's `StaticReturnType` (`function.go:104`).
    """

    def type_func(_args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
        return return_type

    return type_func


def refine_not_null(builder: RefinementBuilder) -> RefinementBuilder:
    """go-cty's `refineNonNull`, the refinement almost every stdlib function has.

    A function that always produces a value produces a non-null one, and that
    stays true when the value itself is unknown. `stdlib/refine.go`.
    """
    return builder.not_null()


@attrs.frozen(kw_only=False)
class CtyParameter:
    """One positional parameter of a function. go-cty's `function.Parameter`.

    Every flag defaults to the strict answer, as go-cty's zero value does, so a
    declaration that says nothing rejects nulls, short-circuits unknowns,
    short-circuits an unknown of dynamic type, and strips marks.

    `type` has no default. go-cty's zero `cty.Type` is unusable, and a permissive
    default here would let a parameter be declared without anyone deciding what
    it accepts -- which is the state this framework exists to end.
    """

    name: str
    type: CtyType[Any]
    description: str = attrs.field(default="", kw_only=True)

    # A null may reach both the type-check and the implementation
    # (`argument.go:25`).
    allow_null: bool = attrs.field(default=False, kw_only=True)

    # An unknown may reach the implementation. Without this, an unknown argument
    # returns an unknown of the return type without calling it
    # (`argument.go:31`).
    allow_unknown: bool = attrs.field(default=False, kw_only=True)

    # An unknown of *dynamic* type may reach the implementation. Note go-cty's
    # rule that this is independent of `allow_unknown`: allowing the dynamic type
    # without allowing unknowns lets the type-check see it while the
    # implementation still does not, which keeps the return type concrete for a
    # function whose type does not depend on its arguments (`argument.go:38`).
    allow_dynamic_type: bool = attrs.field(default=False, kw_only=True)

    # A marked value may reach the implementation, which then owns propagating
    # the marks. Without this the value is unmarked first and the union of every
    # argument's marks is re-applied to the result (`argument.go:55`).
    allow_marked: bool = attrs.field(default=False, kw_only=True)


def _as_params(value: Sequence[CtyParameter]) -> tuple[CtyParameter, ...]:
    """A typed converter, because a bare `tuple` defeats mypy's field inference."""
    return tuple(value)


@attrs.frozen(kw_only=True)
class CtyFunctionSpec:
    """The specification of a function. go-cty's `function.Spec`.

    `type_func` is go-cty's `Spec.Type`; the name differs because
    `CtyFunction.return_type` is the method that consults it, and a field and a
    method called the same thing on the same object read as one thing.
    """

    # The go-cty stdlib name, used in argument errors so a practitioner reading
    # "upper: argument 0 must not be null" knows which call failed. go-cty's
    # `Spec` has no name field -- its errors lean on the caller to attribute
    # them -- and this package's error house style already names the function.
    name: str = ""

    # Converted, because a frozen spec holding a caller's *list* is not frozen:
    # the caller can still append to it, and `params` is re-read on every call.
    params: tuple[CtyParameter, ...] = attrs.field(default=(), converter=_as_params)
    var_param: CtyParameter | None = None
    type_func: TypeFunc
    impl: ImplFunc
    description: str = ""
    refine_result: RefineResult | None = None


def _arity_error(required: int, given: int, *, variadic: bool) -> CtyFunctionError:
    if variadic:
        return CtyFunctionError(f"wrong number of arguments (at least {required} required; {given} given)")
    return CtyFunctionError(f"wrong number of arguments ({required} required; {given} given)")


def _unwrap_dynamic(value: CtyValue[Any]) -> CtyValue[Any]:
    """See through this package's `CtyDynamic` wrapper to the concrete value.

    go-cty has no such wrapper: a dynamic-typed *value* there is `cty.DynamicVal`,
    an unknown whose type is `DynamicPseudoType`, and a value that merely arrived
    through a dynamic-typed slot carries its own concrete type. Here a known
    dynamic value is a `CtyValue` whose type is `CtyDynamic` and whose payload is
    another `CtyValue`, so the wrapper has to be removed before any type check to
    ask go-cty's question rather than a different one.

    That is representation, not policy, which is why it is unconditional and not
    governed by `allow_dynamic_type`. Fifteen function bodies were doing it by
    hand, three of them with a byte-identical copy of this loop.

    Each removed wrapper's marks move onto what it wrapped. In go-cty the same
    marks would already be on the value itself -- there is no wrapper to carry
    them -- so dropping them here would declassify a sensitive value merely for
    having arrived through a dynamic slot. Invisible for a parameter that strips
    marks (the call collects them off the *original* argument), and a live leak
    for one that declares `allow_marked` and is trusted to see every mark.
    """
    while isinstance(value.type, CtyDynamic) and isinstance(value.value, CtyValue):
        wrapper_marks = value.marks
        value = value.value
        if wrapper_marks:
            value = value.with_marks(wrapper_marks)
    return value


def _is_dynamic_typed(value: CtyValue[Any]) -> bool:
    """Whether this is go-cty's `cty.DynamicVal` -- a value of no decided type.

    Only an *unknown* dynamic qualifies. A known one has been unwrapped to its
    concrete type by the time this is asked, and a null dynamic is a value whose
    type genuinely is not decided, which go-cty spells `cty.NullVal(DynamicPseudoType)`
    and treats as dynamically typed too.
    """
    return isinstance(value.type, CtyDynamic)


def _check_argument(
    name: str, param: CtyParameter, index: int, arg: CtyValue[Any]
) -> tuple[CtyValue[Any], bool]:
    """One argument checked against its parameter, as go-cty's type-check loop does.

    Returns the argument as the type callback should see it -- dynamic wrapper
    removed, and unmarked unless the parameter admits marks -- and whether it was
    too vaguely typed to predict a return type from.
    """
    value = _unwrap_dynamic(arg)

    # go-cty unmarks for the type check and discards the marks, on the
    # understanding that the call will collect them separately. A `Type`
    # implementation therefore must not consult marks (`function.go:154`).
    if not param.allow_marked:
        value = _strip(value)

    if value.is_null and not param.allow_null:
        # go-cty's text is the bare "argument must not be null" with the index
        # carried on `ArgError.Index`; this package's house style names the
        # function, which is strictly more useful to a practitioner reading a
        # diagnostic. The index still rides on the exception.
        raise CtyArgumentError(index, ERR_ARGUMENT_MUST_NOT_BE_NULL.format(func=name, position=index))

    # `allow_unknown` is deliberately not consulted here: a return type has to be
    # computable from unknown values, which is the whole point of computing it
    # separately from the answer.
    if _is_dynamic_typed(value):
        return value, not param.allow_dynamic_type

    if errors := conformance_errors(value.type, param.type):
        raise CtyArgumentError(index, str(errors[0]))

    return value, False


@attrs.frozen
class CtyFunction:
    """A function: its declared signature, and the implementation behind it.

    go-cty's `function.Function`. Construct one from a `CtyFunctionSpec`; the
    spec is not read again after construction, matching go-cty's rule that a
    caller must not mutate a `Spec` it has handed to `New`.
    """

    spec: CtyFunctionSpec

    # -- signature --------------------------------------------------------

    @property
    def params(self) -> tuple[CtyParameter, ...]:
        """The fixed positional parameters. Variadic ones are `var_param`."""
        return self.spec.params

    @property
    def var_param(self) -> CtyParameter | None:
        """The variadic parameter, or `None` for a fixed-arity function."""
        return self.spec.var_param

    @property
    def description(self) -> str:
        return self.spec.description

    def with_new_descriptions(self, func_desc: str, param_descs: Sequence[str] | None) -> CtyFunction:
        """The same function with its prose replaced. go-cty's `WithNewDescriptions`.

        `param_descs` may either cover the variadic parameter or stop short of
        it, so adding a variadic parameter to a function does not break an
        existing caller of this method (`function.go:425`). `None` is an empty
        list, as go-cty's own tests pass `nil` for a function with no
        parameters to describe.
        """
        param_descs = param_descs if param_descs is not None else ()
        params = self.spec.params
        var_param = self.spec.var_param
        if var_param is not None:
            allowed = (len(params), len(params) + 1)
            if len(param_descs) not in allowed:
                raise CtyFunctionError(f"param_descs must have length of either {allowed[1]} or {allowed[0]}")
        elif len(param_descs) != len(params):
            raise CtyFunctionError(f"param_descs must have length {len(params)}")

        new_params = tuple(
            attrs.evolve(param, description=desc)
            for param, desc in zip(params, param_descs[: len(params)], strict=True)
        )
        new_var_param = var_param
        for desc in param_descs[len(params) :]:
            assert var_param is not None
            new_var_param = attrs.evolve(var_param, description=desc)

        return CtyFunction(
            attrs.evolve(
                self.spec,
                params=new_params,
                var_param=new_var_param,
                description=func_desc,
            )
        )

    # -- return type ------------------------------------------------------

    def return_type(self, arg_types: Sequence[CtyType[Any]]) -> CtyType[Any]:
        """What a call with arguments of these types would return.

        go-cty's `ReturnType` (`function.go:117`). Values are not needed, so
        each type stands in as an unknown of itself -- which is also why a
        function whose return type depends on an argument's *value* answers
        dynamic here and something narrower from `return_type_for_values`.
        """
        return self.return_type_for_values([CtyValue.unknown(arg_type) for arg_type in arg_types])

    def return_type_for_values(self, args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
        """What a call with these arguments would return. go-cty's `ReturnTypeForValues`."""
        return_type, _, _ = self._prepare(args)
        return return_type

    def _prepare(self, args: Sequence[CtyValue[Any]]) -> tuple[CtyType[Any], bool, tuple[CtyValue[Any], ...]]:
        """Check the arguments, and decide the return type.

        Returns the return type, whether any argument was too vaguely typed for
        the implementation to be worth calling, and the arguments with this
        package's dynamic wrapper removed. go-cty's `returnTypeForValues`
        (`function.go:125`), which reports the same three things -- the third as
        a rewritten `args` slice.
        """
        params = self.spec.params
        var_param = self.spec.var_param

        if var_param is None:
            if len(args) != len(params):
                raise _arity_error(len(params), len(args), variadic=False)
        elif len(args) < len(params):
            raise _arity_error(len(params), len(args), variadic=True)

        prepared: list[CtyValue[Any]] = []
        for index, arg in enumerate(args):
            value, vague = _check_argument(self.spec.name, self._param_at(index), index, arg)
            prepared.append(value)
            if vague:
                # go-cty returns the moment it meets an inexactly typed argument
                # (`function.go:178-181`): the later arguments are never checked
                # at all, so a null or a mistyped value *after* a `DynamicVal`
                # is not an error -- the whole call is already decided to be
                # `DynamicVal`. Checking them anyway failed 20 of the 83 stdlib
                # functions on `f(DynamicVal, null)`, a call Terraform accepts.
                prepared.extend(_unwrap_dynamic(later) for later in args[index + 1 :])
                return CtyDynamic(), True, tuple(prepared)

        return self._call_type_func(prepared), False, tuple(prepared)

    def _param_at(self, index: int) -> CtyParameter:
        """The parameter governing argument `index`. Arity is already checked."""
        params = self.spec.params
        if index < len(params):
            return params[index]
        var_param = self.spec.var_param
        assert var_param is not None
        return var_param

    def _call_type_func(self, args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
        try:
            return self.spec.type_func(args)
        except (CtyError, CtyValidationError, RecursionError):
            # A library error is the function *answering* -- go-cty passes an
            # error returned from `Type` straight through and reserves
            # `PanicError` for an actual panic. `CtyValidationError` descends
            # from the foundation's validation error rather than `CtyError`, so
            # it is named here explicitly. A `RecursionError` must never be
            # wrapped: building a rich exception on an exhausted stack raises a
            # second one from inside the handler, and the recursion guard
            # upstream re-raises foreign overflows on purpose.
            raise
        except Exception as exc:
            raise CtyFunctionPanicError(f"error in function type implementation: {exc}") from exc

    # -- calling ----------------------------------------------------------

    def call(self, args: Sequence[CtyValue[Any]]) -> CtyValue[Any]:
        """Call the function. go-cty's `Function.Call` (`function.go:249`).

        The order of operations is go-cty's, and each step is load-bearing:
        check arity and types and decide the return type; unmark what the
        parameters do not admit marked, keeping the union; short-circuit to an
        unknown of the return type if anything is unknown that the parameters do
        not admit unknown; otherwise run the implementation; re-apply the marks;
        check the answer against the promised return type; and finally apply
        `refine_result`, which holds on every path because it describes the
        function's whole range.
        """
        return_type, dynamically_typed, prepared = self._prepare(args)

        # Marks are collected from every argument even when the answer is already
        # known to be unknown, because losing a mark is a silent
        # declassification and an unknown value is still sensitive
        # (`function.go:256`).
        result_marks: frozenset[Any] = frozenset()
        return_unknown = dynamically_typed

        arguments = list(prepared)
        for index, value in enumerate(prepared):
            param = self._param_at(index)
            # `_arg_marks` rather than `collect_marks_deep`, because this runs on
            # every argument of every stdlib call and the common case -- an
            # unmarked scalar -- must not pay to set up a walk. Skipping that fast
            # path once cost `length()` on a 200k-element list 41 ms per call
            # instead of 0.005 ms.
            if not param.allow_marked and (marks := _arg_marks(args[index])):
                result_marks |= marks
                arguments[index] = _strip(value)
            if value.is_unknown and not param.allow_unknown:
                return_unknown = True

        if return_unknown:
            return self._refine(CtyValue.unknown(return_type).with_marks(result_marks))

        result = self._call_impl(arguments, return_type)
        if result_marks:
            result = result.with_marks(result_marks)

        # go-cty panics here rather than returning an error: a result that does
        # not match the type its own `Type` promised is a bug in the function,
        # not in the call, and callers are entitled not to handle it
        # (`function.go:364`).
        if errors := conformance_errors(result.type, return_type):
            # The type objects themselves, not `.ctype`: a capsule type's ctype
            # is `None`, and "type None does not conform to None" names nothing.
            raise CtyFunctionPanicError(
                f"returned value of type {result.type} does not conform to "
                f"declared return type {return_type}: {errors[0]}"
            )

        return self._refine(result)

    def _call_impl(self, args: Sequence[CtyValue[Any]], return_type: CtyType[Any]) -> CtyValue[Any]:
        try:
            return self.spec.impl(args, return_type)
        except (CtyError, CtyValidationError, RecursionError):
            # See `_call_type_func`: library errors and stack exhaustion pass
            # through; only genuinely foreign exceptions become "panics".
            raise
        except Exception as exc:
            raise CtyFunctionPanicError(f"error in function implementation: {exc}") from exc

    def _refine(self, value: CtyValue[Any]) -> CtyValue[Any]:
        """Apply `refine_result`, if any.

        A refinement of a *known* value is a claim the builder checks and then
        returns the value untouched, so this runs on both paths rather than only
        the unknown one -- which is what makes an inconsistent declaration fail
        loudly instead of only when an argument happened to be unknown.

        The exception is an unknown whose *type* is dynamic: go-cty guards its
        deferred refinement with `val.IsKnown() || val.Type() != DynamicPseudoType`
        (`function.go:281`), because there is no type yet for a refinement to be
        about. The gate is on the result, not the arguments -- `jsondecode` of an
        unknown string returns an unknown *dynamic* from perfectly concrete
        arguments, and refining it anyway was measured as a divergence on
        2026-08-17 (`regex`, `concat`, `merge`, `csvdecode` all hit it).
        """
        refine_result = self.spec.refine_result
        if refine_result is None:
            return value
        if value.is_unknown and isinstance(value.type, CtyDynamic):
            return value
        return refine_result(refine(value)).new_value()

    def proxy(self) -> Callable[..., CtyValue[Any]]:
        """A plain callable taking the arguments positionally. go-cty's `Proxy`."""

        def proxied(*args: CtyValue[Any]) -> CtyValue[Any]:
            return self.call(args)

        return proxied


def unpredictable(function: CtyFunction, /) -> CtyFunction:
    """The same signature and type checking, but always answering unknown.

    go-cty's `function.Unpredictable` (`unpredictable.go:24`), for standing in
    for a function whose result depends on state outside the values -- reading a
    file, asking the time -- during a phase that must not have the effect yet.
    """

    def impl(_args: Sequence[CtyValue[Any]], return_type: CtyType[Any]) -> CtyValue[Any]:
        return CtyValue.unknown(return_type)

    return CtyFunction(attrs.evolve(function.spec, impl=impl))


def positional_impl(fn: Callable[..., Any], *, wants_return_type: bool = False) -> ImplFunc:
    """Adapt a Python function of named parameters to go-cty's `ImplFunc` shape.

    go-cty's implementations take `(args []cty.Value, retType cty.Type)` because
    Go has no other way to write a variadic heterogeneous signature. Python does,
    and `substr(s, offset, length)` is more readable than `args[0], args[1],
    args[2]` -- so the adapter spreads the arguments and the bodies keep their
    parameter names.

    `wants_return_type` passes the already-decided return type as a keyword, for
    a generic function that would otherwise compute it a second time.
    """
    if wants_return_type:

        def impl_with_type(args: Sequence[CtyValue[Any]], return_type: CtyType[Any]) -> CtyValue[Any]:
            return fn(*args, return_type=return_type)  # type: ignore[no-any-return]

        return impl_with_type

    def impl(args: Sequence[CtyValue[Any]], _return_type: CtyType[Any]) -> CtyValue[Any]:
        return fn(*args)  # type: ignore[no-any-return]

    return impl


def bind_positionally(
    fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]
) -> tuple[Any, ...]:
    """Every argument as a positional tuple, in declaration order.

    The framework speaks go-cty's positional vocabulary, and callers of this
    package's stdlib have always been able to pass an argument by its Python
    parameter name. Binding through the signature keeps both true rather than
    breaking the second, and costs nothing on the ordinary path because it is
    only reached when `kwargs` is non-empty.

    `bind_partial` rather than `bind`, and keyword-only parameters are skipped:
    a keyword-only parameter is plumbing the framework itself supplies -- 25
    functions take `return_type` that way -- so a full `bind` would demand it
    from the caller and refuse every keyword call to those functions.
    """
    if not kwargs:
        return args
    signature = inspect.signature(fn)
    bound = signature.bind_partial(*args, **kwargs)
    positional: list[Any] = []
    for parameter_name, parameter in signature.parameters.items():
        if parameter.kind is inspect.Parameter.KEYWORD_ONLY:
            continue
        if parameter_name not in bound.arguments:
            continue
        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            positional.extend(bound.arguments[parameter_name])
        else:
            positional.append(bound.arguments[parameter_name])
    return tuple(positional)


# 🌊🪢🔚
