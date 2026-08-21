#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `stdlib/collection.go` and `stdlib/sequence.go`, declared rather than re-derived.

Every function here carries the `Spec` go-cty gives it: the per-parameter null,
unknown, dynamic and mark policy, the `Type` callback that decides the return
type before the values are known, and the `RefineResult` that says what stays
true of the answer even when the answer is unknown. `collection.go` is the
densest file in go-cty's stdlib for that declared policy -- fifteen
`RefineResult`, sixteen `AllowMarked`, six `AllowDynamicType`, four
`AllowUnknown` and three `AllowNull` -- and none of it was expressible before
`_function.py` existed.

Two deliberate departures, both recorded rather than accidental:

**Parameter types are widened where this package already accepted more than
go-cty does.** go-cty declares four of these parameters concretely -- `distinct`
and `chunklist` take `list(dynamic)`, `compact` and `sort` take `list(string)` --
and relies on its caller (HCL) to convert an argument to the parameter type
before the call. Nothing converts here, so declaring those types verbatim would
turn `sort` of a `list(number)`, `compact` of a set and `chunklist` of a tuple
from working calls into type errors. The precedent is `chunklist`'s tuple
support, which `tests/functions/test_gocty_stdlib_parity.py` documents as "a
deliberate superset". So the parameter is declared `dynamic` and go-cty's shape
check moves into the `Type` callback, which is where it can still refuse an
*unknown* of the wrong type. Every such widening is named at the function.

`zipmap`'s keys are the one concrete parameter kept verbatim, because there the
element type is load-bearing rather than incidental: the keys become map keys or
object attribute names, and a widened parameter admitted a `list(dynamic)` of
containers that `str()` then turned into a map keyed by a Python repr.

**`flatten` and `length` do not take `AllowMarked`, though go-cty gives it to
them.** go-cty's `flattener` propagates only the marks of the *sequences* it
unwraps, and `Value.Length()` only the collection's own top-level marks, so in
go-cty a mark on an inner element stays on that element (`flatten`) or is
dropped entirely (`length`). This package's rule is the framework default --
collect marks from anywhere inside the argument and re-apply their union to the
result -- and `tests/functions/test_mark_propagation.py` pins it for exactly
these two functions. Matching go-cty there would move a sensitivity flag off the
top level of a result, which is a declassification and not a decision to take
while migrating. The other fourteen `AllowMarked` parameters are declared and
handled as go-cty handles them.
"""

from __future__ import annotations

from pyvider.cty.functions.collection.combine import (
    merge,
    setproduct,
    zipmap,
)
from pyvider.cty.functions.collection.lookup import (
    contains,
    element,
    hasindex,
    index,
    keys,
    length,
    lookup,
    values,
)
from pyvider.cty.functions.collection.reshape import (
    chunklist,
    coalescelist,
    compact,
    concat,
    distinct,
    flatten,
    range_fn,
    reverse,
    slice,
    sort,
)

__all__ = [
    "chunklist",
    "coalescelist",
    "compact",
    "concat",
    "contains",
    "distinct",
    "element",
    "flatten",
    "hasindex",
    "index",
    "keys",
    "length",
    "lookup",
    "merge",
    "range_fn",
    "reverse",
    "setproduct",
    "slice",
    "sort",
    "values",
    "zipmap",
]

# 🌊🪢🔚
