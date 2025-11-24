#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for basic string functions (join, split, replace, upper, lower, etc.)."""

import pytest

from pyvider.cty import CtyList, CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    join,
    lower,
    replace,
    split,
    upper,
)


# Helper functions for creating CtyValues to improve test readability
def S(v):
    return CtyString().validate(v)


def N(v):
    return CtyNumber().validate(v)


def L(t, v):
    return CtyList(element_type=t).validate(v)


class TestStringBasicFunctions:
    def test_join(self) -> None:
        assert join(S(","), L(CtyString(), ["a", "b"])).value == "a,b"

    def test_split(self) -> None:
        assert split(S(","), S("a,b,c")).raw_value == ["a", "b", "c"]

    def test_replace(self) -> None:
        assert replace(S("a-b-c"), S("-"), S(":")).value == "a:b:c"

    def test_upper_with_null_and_unknown(self) -> None:
        assert upper(CtyValue.null(CtyString())).is_null
        assert upper(CtyValue.unknown(CtyString())).is_unknown

    def test_lower_with_null_and_unknown(self) -> None:
        assert lower(CtyValue.null(CtyString())).is_null
        assert lower(CtyValue.unknown(CtyString())).is_unknown

    def test_upper(self) -> None:
        assert upper(CtyString().validate("hello")).value == "HELLO"

    def test_lower(self) -> None:
        assert lower(CtyString().validate("HELLO")).value == "hello"

    def test_join_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import join
        from pyvider.cty.types import CtyList, CtyNumber

        with pytest.raises(CtyFunctionError):
            join(
                CtyNumber().validate(123),
                CtyList(element_type=CtyString()).validate([]),
            )
        with pytest.raises(CtyFunctionError):
            join(CtyString().validate(","), CtyNumber().validate(123))

    def test_split_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import split
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            split(CtyNumber().validate(123), CtyString().validate("a"))
        with pytest.raises(CtyFunctionError):
            split(CtyString().validate(","), CtyNumber().validate(123))

    def test_replace_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import replace
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            replace(
                CtyNumber().validate(123),
                CtyString().validate("a"),
                CtyString().validate("b"),
            )
        with pytest.raises(CtyFunctionError):
            replace(
                CtyString().validate("a"),
                CtyNumber().validate(123),
                CtyString().validate("b"),
            )
        with pytest.raises(CtyFunctionError):
            replace(
                CtyString().validate("a"),
                CtyString().validate("b"),
                CtyNumber().validate(123),
            )

    def test_join_null_unknown(self) -> None:
        assert join(CtyValue.null(CtyString()), L(CtyString(), ["a"])).is_unknown
        assert join(S(","), CtyValue.null(CtyList(element_type=CtyString()))).is_unknown
        assert join(CtyValue.unknown(CtyString()), L(CtyString(), ["a"])).is_unknown
        assert join(S(","), CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_split_null_unknown(self) -> None:
        assert split(CtyValue.null(CtyString()), S("a,b")).is_unknown
        assert split(S(","), CtyValue.null(CtyString())).is_unknown
        assert split(CtyValue.unknown(CtyString()), S("a,b")).is_unknown
        assert split(S(","), CtyValue.unknown(CtyString())).is_unknown

    def test_replace_null_unknown(self) -> None:
        assert replace(CtyValue.null(CtyString()), S("a"), S("b")).is_unknown
        assert replace(S("a"), CtyValue.null(CtyString()), S("b")).is_unknown
        assert replace(S("a"), S("b"), CtyValue.null(CtyString())).is_unknown
        assert replace(CtyValue.unknown(CtyString()), S("a"), S("b")).is_unknown
        assert replace(S("a"), CtyValue.unknown(CtyString()), S("b")).is_unknown
        assert replace(S("a"), S("b"), CtyValue.unknown(CtyString())).is_unknown


# 🌊🪢🔚
