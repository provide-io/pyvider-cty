# tests/functions/test_structural_stdlib_functions.py
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

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
        null_val = CtyString().validate(None) if hasattr(CtyString().validate, '__call__') else CtyString()
        from pyvider.cty import CtyValue
        null_val = CtyValue.null(CtyString())
        assert coalesce(val1, val2).value == "a"
        assert coalesce(null_val, val2).value == "b"
        assert coalesce(null_val, null_val, val1).value == "a"


# 🐍⛓️🔣🪄
