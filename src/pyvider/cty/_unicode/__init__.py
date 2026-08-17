#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Vendored Unicode algorithms, kept private to this package.

Nothing here is part of the public API. It exists because Python's standard
library has no UAX#29 segmentation and four stdlib functions need it to answer
what go-cty answers.

The two modules alongside this one are MIT licensed and carry their own
copyright headers -- see LICENSES/MIT.txt.
"""

from pyvider.cty._unicode.grapheme import cluster_count, iter_clusters

__all__ = ["cluster_count", "iter_clusters"]

# 🌊🪢🔚
