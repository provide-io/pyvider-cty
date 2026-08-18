#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for encoding functions (jsonencode, jsondecode, csvdecode)."""

from pyvider.cty import CtyMap, CtyObject, CtyString


# Helper functions for creating CtyValues to improve test readability
def S(v):
    return CtyString().validate(v)


def M(t, v):
    return CtyMap(element_type=t).validate(v)


class TestEncodingFunctions:
    def test_jsonencode(self) -> None:
        from pyvider.cty.functions import jsonencode

        val = M(CtyString(), {"a": "b"})
        # Go's encoding/json emits no spaces after `:` or `,`; Python's does.
        # jsonencode output lands in Terraform state and is compared as text, so
        # the separators are part of the answer, not formatting.
        assert jsonencode(val).value == '{"a":"b"}'

    def test_jsondecode(self) -> None:
        from pyvider.cty.functions import jsondecode

        val = S('{"a": "b"}')
        decoded = jsondecode(val)
        # The type is the one the document implies, not a dynamic wrapper. This
        # assertion used to require CtyDynamic, which is what this package
        # returned and what go-cty does not: the concrete type is what reaches
        # Terraform over the wire.
        assert isinstance(decoded.type, CtyObject)
        assert decoded.type.attribute_types == {"a": CtyString()}
        assert decoded.raw_value == {"a": "b"}

    def test_csvdecode(self) -> None:
        from pyvider.cty.functions import csvdecode

        val = S("a,b\n1,2\n3,4")
        decoded = csvdecode(val)
        assert decoded.raw_value == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]


# 🌊🪢🔚
