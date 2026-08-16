#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Mark preservation across validation.

Most `validate` implementations unwrap an incoming `CtyValue` to reach its raw
payload and then build a fresh result, which loses whatever marks the input was
carrying. Marks are how Terraform tracks sensitivity, so that quietly turns a
sensitive value into a non-sensitive one.

It matters at two levels, and one rule covers both: a marked value validated on
its own keeps its mark, and a marked value validated as a collection element
keeps it too, because collections validate each element through its element
type.

Stated once here rather than in each of the ten `validate` implementations, for
the same reason `CtyType.unknown_marker` is stated once — every type owes the
same guarantee, and repeating it is how types drift apart. `CtyObject` grew its
own copy of this logic before there was a shared place to put it.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar, cast

if TYPE_CHECKING:
    from pyvider.cty.values.base import CtyValue

ValidateFn = TypeVar("ValidateFn", bound=Callable[..., Any])

# Resolved once, lazily: importing CtyValue at module scope would cycle.
_CTY_VALUE_TYPE: type | None = None


def reapply_marks(source: object, result: Any) -> Any:
    """Carry `source`'s marks onto `result`, if it had any.

    The rule itself, stated once. It is applied from two places because of
    stack depth, not because it differs between them -- see `preserves_marks`.

    Checks the type, not just for a `marks` attribute. Duck-typing here was
    faster -- this runs once per element of every collection validated -- but a
    capsule can wrap an arbitrary Python object, and an object that happens to
    carry its own `marks` had that attribute adopted as cty marks: a string
    became a frozenset of its characters, and an int raised TypeError out of
    `validate`. The class is cached so the check stays one isinstance, without
    the per-call import lookup that motivated the duck-typing.
    """
    global _CTY_VALUE_TYPE
    if _CTY_VALUE_TYPE is None:
        from pyvider.cty.values import CtyValue

        _CTY_VALUE_TYPE = CtyValue

    if not isinstance(source, _CTY_VALUE_TYPE):
        return result
    marked = cast("CtyValue[Any]", source)
    if not marked.marks:
        return result
    return result.with_marks(marked.marks)


def preserves_marks(func: ValidateFn) -> ValidateFn:
    """Re-apply the marks carried by a validated value to the result.

    For leaf types only -- primitives and capsules, which never recurse.

    The recursing types (collections, object, tuple, dynamic) get the same
    treatment from inside `with_recursion_detection` instead of from a second
    decorator here. A decorator that wraps a recursive call keeps its frame on
    the stack for every level of nesting, so stacking a second one over
    `with_recursion_detection` took the per-level cost from two frames to
    three and cut the maximum validatable nesting depth by a third. Leaf types
    have no such cost: their frame is live once, at the bottom.

    That per-level frame cost is not incidental -- `FRAMES_PER_VALIDATION_LEVEL`
    is what the advertised depth limit is derived from, so a third frame here
    would silently make that number a lie again.

    Declared as an identity on the function type so each `validate` keeps its
    own signature. `validate` implementations return differently-parameterised
    `CtyValue`s -- `CtyValue[str]`, `CtyValue[tuple[T, ...]]`, `CtyValue[Any]`
    -- and any single concrete signature here would flatten all of them and
    change what mypy infers at every call site in the package.
    """

    @wraps(func)
    def wrapper(self: Any, value: Any, *args: Any, **kwargs: Any) -> Any:
        return reapply_marks(value, func(self, value, *args, **kwargs))

    return cast(ValidateFn, wrapper)


# 🌊🪢🔚
