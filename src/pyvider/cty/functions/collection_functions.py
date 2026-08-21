#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Compatibility facade: the collection functions live in `pyvider.cty.functions.collection`.

The module was split on 2026-08-21 -- it had grown to 1,745 lines -- into
`collection/reshape.py`, `collection/lookup.py` and `collection/combine.py`,
with the shared helpers in `collection/_shared.py`. This name is kept so that
`from pyvider.cty.functions.collection_functions import X` keeps working.
"""

from __future__ import annotations

from pyvider.cty.functions.collection import (
    chunklist,
    coalescelist,
    compact,
    concat,
    contains,
    distinct,
    element,
    flatten,
    hasindex,
    index,
    keys,
    length,
    lookup,
    merge,
    range_fn,
    reverse,
    setproduct,
    slice,
    sort,
    values,
    zipmap,
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
