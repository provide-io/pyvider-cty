#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `UnknownAsNull` (`cty/unknown_as_null.go`).

Replaces every unknown in a value, at any depth, with a null of the same type.
Terraform uses this when it needs a value that can be *stored* -- an unknown is
a promise about a future apply and has no representation in state, whereas a
null is an ordinary value. Anything that must serialize a plan-time value
without waiting for it goes through this.

The rules that are easy to get wrong, and are therefore tested directly:

  - A **null stays null**. Only unknowns are rewritten, and a null is already
    a value.
  - An **unknown container becomes a null container**, not a container of
    nulls. There are no elements to descend into -- the collection itself is
    what is unknown.
  - **Marks survive** (go-cty 1.16.4). Marks are stripped at each level,
    the level is rewritten, and the marks are re-applied. A value being
    unknown is not what makes it sensitive, so making it null must not
    declassify it.
"""

from __future__ import annotations

from typing import Any, cast

from pyvider.cty.types import (
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyTuple,
)
from pyvider.cty.values import CtyValue

__all__ = ["unknown_as_null"]

_SEQUENCES = (CtyList, CtyTuple, CtySet)
_MAPPINGS = (CtyMap, CtyObject)


def unknown_as_null(value: CtyValue[Any], /) -> CtyValue[Any]:
    """Every unknown in `value`, at any depth, replaced by a null of its type."""
    if value.marks:
        # Unmark, rewrite, re-mark -- go-cty's own first step, and the reason
        # is that the rewrite below rebuilds containers, which would otherwise
        # drop the marks the original was carrying.
        #
        # `unmark()`, not `with_marks(frozenset())`: `with_marks` *unions*, so
        # asking it for no marks returns the value unchanged and this recurses
        # until the stack runs out.
        bare, marks = value.unmark()
        return unknown_as_null(bare).with_marks(marks)

    if value.is_null:
        return value
    if value.is_unknown:
        return CtyValue.null(value.type)

    if isinstance(value.type, _SEQUENCES):
        return _rewrite_sequence(value)
    if isinstance(value.type, _MAPPINGS):
        return _rewrite_mapping(value)
    return value


def _rewrite_sequence(value: CtyValue[Any]) -> CtyValue[Any]:
    elements = value.value
    if not elements:
        # go-cty returns the value untouched here rather than rebuilding it:
        # with no elements there is nothing that could be unknown, and
        # rebuilding an empty set or tuple is where a type would get lost.
        return value

    rewritten = [unknown_as_null(element) for element in cast("tuple[CtyValue[Any], ...]", elements)]
    if isinstance(value.type, CtySet):
        # Rebuilt through the type so the set re-deduplicates, as go-cty's
        # `SetVal` does. Two elements that differed only in being unknown can
        # become equal once both are null, and a set must not hold both.
        return cast("CtyValue[Any]", value.type.validate(rewritten))
    return CtyValue(vtype=value.type, value=tuple(rewritten))


def _rewrite_mapping(value: CtyValue[Any]) -> CtyValue[Any]:
    items = value.value
    if not items:
        return value

    rewritten = {
        key: unknown_as_null(element) for key, element in cast("dict[str, CtyValue[Any]]", items).items()
    }
    # Built with the original type rather than inferred from the payload, which
    # is what go-cty's `ObjectVal` does. Inference would discard the object's
    # optional-attribute set, and that set is part of the wire type Terraform
    # is told about.
    return value.type.validate(rewritten)


# 🌊🪢🔚
