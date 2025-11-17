#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for structural functions (coalesce)."""

from pyvider.cty import CtyString
from pyvider.cty.functions import coalesce


# Helper functions for creating CtyValues to improve test readability
def S(v):
    return CtyString().validate(v)


class TestStructuralFunctions:
    def test_coalesce(self) -> None:
        val1 = S("a")
        val2 = S("b")
        from pyvider.cty import CtyValue

        null_val = CtyValue.null(CtyString())
        assert coalesce(val1, val2).value == "a"
        assert coalesce(null_val, val2).value == "b"
        assert coalesce(null_val, null_val, val1).value == "a"


# 🌊🪢🔚
