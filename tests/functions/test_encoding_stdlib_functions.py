#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for encoding functions (jsonencode, jsondecode, csvdecode)."""

from pyvider.cty import CtyDynamic, CtyMap, CtyString


# Helper functions for creating CtyValues to improve test readability
def S(v):
    return CtyString().validate(v)


def M(t, v):
    return CtyMap(element_type=t).validate(v)


class TestEncodingFunctions:
    def test_jsonencode(self) -> None:
        from pyvider.cty.functions import jsonencode

        val = M(CtyString(), {"a": "b"})
        assert jsonencode(val).value == '{"a": "b"}'

    def test_jsondecode(self) -> None:
        from pyvider.cty.functions import jsondecode

        val = S('{"a": "b"}')
        decoded = jsondecode(val)
        assert isinstance(decoded.type, CtyDynamic)
        assert decoded.raw_value == {"a": "b"}

    def test_csvdecode(self) -> None:
        from pyvider.cty.functions import csvdecode

        val = S("a,b\n1,2\n3,4")
        decoded = csvdecode(val)
        assert decoded.raw_value == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]


# 🌊🪢🔚
