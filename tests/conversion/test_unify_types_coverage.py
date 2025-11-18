#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pyvider.cty.conversion.raw_to_cty import _unify_types
from pyvider.cty.types import CtyDynamic, CtyNumber, CtyString


def test_unify_types_empty() -> None:
    assert _unify_types(set()) == CtyDynamic()


def test_unify_types_single() -> None:
    assert _unify_types({CtyString()}) == CtyString()


def test_unify_types_all_same() -> None:
    assert _unify_types({CtyString(), CtyString()}) == CtyString()


def test_unify_types_different() -> None:
    assert _unify_types({CtyString(), CtyNumber()}) == CtyDynamic()


# 🌊🪢🔚
