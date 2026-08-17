#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""UAX#29 grapheme cluster segmentation, as a public surface.

go-cty keeps its own copy under `cty/internal/graphemes`, so nothing here
corresponds to a go-cty export. It is published anyway for one concrete reason:
`pyvider-components` registers a provider function named `length` that shadows
Terraform's builtin, and Terraform's `length` counts *characters* -- grapheme
clusters -- where Python's `len` counts code points. `length("👨‍👩‍👧‍👦")` is 1 in
Terraform and 7 in Python, and the only way for another package to agree with
Terraform is to reach the same segmentation this one uses.

The alternative was for that package to vendor a second copy of the tables. Two
copies of a Unicode algorithm is the shape of divergence this repository keeps
finding: they agree today and nothing makes them agree tomorrow.

The names are longer than the private ones deliberately. `cluster_count` reads
unambiguously inside `pyvider.cty._unicode`, where the only clusters under
discussion are graphemes; at the top level of a type-system package, "cluster"
could be several things.
"""

from __future__ import annotations

from collections.abc import Iterator

from pyvider.cty._unicode import cluster_count, iter_clusters

__all__ = ["grapheme_cluster_count", "grapheme_clusters"]


def grapheme_cluster_count(text: str, /) -> int:
    """How many grapheme clusters `text` contains.

    What a reader would call the number of characters, and what go-cty's
    `Strlen` and Terraform's `length` answer for a string.
    """
    return cluster_count(text)


def grapheme_clusters(text: str, /) -> Iterator[str]:
    """`text` split into grapheme clusters, in order."""
    return iter_clusters(text)


# 🌊🪢🔚
