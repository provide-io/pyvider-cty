#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for advanced string functions (regex, trim, substr, indent, chomp, strrev, etc.)."""

import pytest

from pyvider.cty import CtyList, CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    chomp,
    indent,
    regex,
    regexall,
    regexreplace,
    strrev,
    substr,
    title,
    trim,
    trimprefix,
    trimspace,
    trimsuffix,
)


# Helper functions for creating CtyValues to improve test readability
def S(v):
    return CtyString().validate(v)


def N(v):
    return CtyNumber().validate(v)


def L(t, v):
    return CtyList(element_type=t).validate(v)


class TestStringAdvancedFunctions:
    @pytest.mark.parametrize(
        "input_str, expected_str",
        [
            ("hello\n", "hello"),
            ("hello\r\n", "hello"),
            ("hello\n\r", "hello\n"),
            ("hello", "hello"),
            ("\n", ""),
            ("\r\n", ""),
            ("", ""),
            ("multi\nline\n", "multi\nline"),
            ("multi\r\nline\r\n", "multi\r\nline"),
        ],
    )
    def test_chomp_various_inputs(self, input_str: str, expected_str: str) -> None:
        cty_input = CtyString().validate(input_str)
        result = chomp(cty_input)
        assert result.value == expected_str

    def test_chomp_null_unknown(self) -> None:
        assert chomp(CtyValue.null(CtyString())).is_null
        assert chomp(CtyValue.unknown(CtyString())).is_unknown

    def test_chomp_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import chomp
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            chomp(CtyNumber().validate(123))

    @pytest.mark.parametrize(
        "input_str, expected_str",
        [
            ("hello", "olleh"),
            ("racecar", "racecar"),
            ("", ""),
            ("a", "a"),
            ("こんにちは", "はちにんこ"),
        ],
    )
    def test_strrev_various_inputs(self, input_str: str, expected_str: str) -> None:
        cty_input = CtyString().validate(input_str)
        result = strrev(cty_input)
        assert result.value == expected_str

    def test_strrev_null_unknown(self) -> None:
        assert strrev(CtyValue.null(CtyString())).is_null
        assert strrev(CtyValue.unknown(CtyString())).is_unknown

    def test_strrev_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import strrev
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            strrev(CtyNumber().validate(123))

    @pytest.mark.parametrize(
        "input_str, expected_str",
        [
            ("  hello  ", "hello"),
            ("\t\n hello \r\x0c\x0b", "hello"),
            ("hello", "hello"),
            ("", ""),
            ("   ", ""),
            ("hello world", "hello world"),
            ("　こんにちは　", "こんにちは"),
        ],
    )
    def test_trimspace_various_inputs(self, input_str: str, expected_str: str) -> None:
        cty_input = CtyString().validate(input_str)
        result = trimspace(cty_input)
        assert result.value == expected_str

    def test_trimspace_null_unknown(self) -> None:
        assert trimspace(CtyValue.null(CtyString())).is_null
        assert trimspace(CtyValue.unknown(CtyString())).is_unknown

    def test_trimspace_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import trimspace
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            trimspace(CtyNumber().validate(123))

    def test_indent(self) -> None:
        """`indent` takes a number of spaces and leaves the first line alone.

        The rest of its behaviour, and why it changed, is in
        tests/functions/test_gocty_stdlib_parity.py.
        """
        result = indent(CtyNumber().validate(2), CtyString().validate("hello\nworld"))
        assert result.value == "hello\n  world"

    def test_substr(self) -> None:
        s = CtyString().validate("hello world")
        offset = CtyNumber().validate(6)
        length = CtyNumber().validate(5)
        result = substr(s, offset, length)
        assert result.value == "world"

    def test_substr_negative_one_length(self) -> None:
        s = CtyString().validate("hello world")
        offset = CtyNumber().validate(6)
        length = CtyNumber().validate(-1)
        result = substr(s, offset, length)
        assert result.value == "world"

    def test_substr_null_unknown(self) -> None:
        s = CtyString().validate("hello world")
        offset = CtyNumber().validate(6)
        length = CtyNumber().validate(5)
        assert substr(CtyValue.null(CtyString()), offset, length).is_unknown
        assert substr(s, CtyValue.null(CtyNumber()), length).is_unknown
        assert substr(s, offset, CtyValue.null(CtyNumber())).is_unknown
        assert substr(CtyValue.unknown(CtyString()), offset, length).is_unknown
        assert substr(s, CtyValue.unknown(CtyNumber()), length).is_unknown
        assert substr(s, offset, CtyValue.unknown(CtyNumber())).is_unknown

    def test_substr_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import substr
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            substr(
                CtyNumber().validate(123),
                CtyNumber().validate(0),
                CtyNumber().validate(1),
            )
        with pytest.raises(CtyFunctionError):
            substr(
                CtyString().validate("a"),
                CtyString().validate("b"),
                CtyNumber().validate(1),
            )
        with pytest.raises(CtyFunctionError):
            substr(
                CtyString().validate("a"),
                CtyNumber().validate(0),
                CtyString().validate("c"),
            )

    def test_substr_invalid_values(self) -> None:
        s = CtyString().validate("hello")
        with pytest.raises(CtyFunctionError):
            substr(s, CtyNumber().validate(-1), CtyNumber().validate(1))
        with pytest.raises(CtyFunctionError):
            substr(s, CtyNumber().validate(0), CtyNumber().validate(-2))

    def test_trim(self) -> None:
        s = CtyString().validate("...hello...")
        cutset = CtyString().validate(".")
        result = trim(s, cutset)
        assert result.value == "hello"

    def test_trim_null_unknown(self) -> None:
        s = CtyString().validate("...hello...")
        cutset = CtyString().validate(".")
        assert trim(CtyValue.null(CtyString()), cutset).is_unknown
        assert trim(s, CtyValue.null(CtyString())).is_unknown
        assert trim(CtyValue.unknown(CtyString()), cutset).is_unknown
        assert trim(s, CtyValue.unknown(CtyString())).is_unknown

    def test_trim_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import trim
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            trim(CtyNumber().validate(123), CtyString().validate("."))
        with pytest.raises(CtyFunctionError):
            trim(CtyString().validate("a"), CtyNumber().validate(123))

    def test_title(self) -> None:
        s = CtyString().validate("hello world")
        result = title(s)
        assert result.value == "Hello World"

    def test_title_null_unknown(self) -> None:
        assert title(CtyValue.null(CtyString())).is_null
        assert title(CtyValue.unknown(CtyString())).is_unknown

    def test_title_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import title
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            title(CtyNumber().validate(123))

    def test_trimprefix(self) -> None:
        s = CtyString().validate("prefix_hello")
        prefix = CtyString().validate("prefix_")
        result = trimprefix(s, prefix)
        assert result.value == "hello"

    def test_trimprefix_no_prefix(self) -> None:
        s = CtyString().validate("hello")
        prefix = CtyString().validate("prefix_")
        result = trimprefix(s, prefix)
        assert result.value == "hello"

    def test_trimprefix_null_unknown(self) -> None:
        s = CtyString().validate("prefix_hello")
        prefix = CtyString().validate("prefix_")
        assert trimprefix(CtyValue.null(CtyString()), prefix).is_unknown
        assert trimprefix(s, CtyValue.null(CtyString())).is_unknown
        assert trimprefix(CtyValue.unknown(CtyString()), prefix).is_unknown
        assert trimprefix(s, CtyValue.unknown(CtyString())).is_unknown

    def test_trimprefix_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import trimprefix
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            trimprefix(CtyNumber().validate(123), CtyString().validate("p"))
        with pytest.raises(CtyFunctionError):
            trimprefix(CtyString().validate("a"), CtyNumber().validate(123))

    def test_trimsuffix(self) -> None:
        s = CtyString().validate("hello_suffix")
        suffix = CtyString().validate("_suffix")
        result = trimsuffix(s, suffix)
        assert result.value == "hello"

    def test_trimsuffix_no_suffix(self) -> None:
        s = CtyString().validate("hello")
        suffix = CtyString().validate("_suffix")
        result = trimsuffix(s, suffix)
        assert result.value == "hello"

    def test_trimsuffix_null_unknown(self) -> None:
        s = CtyString().validate("hello_suffix")
        suffix = CtyString().validate("_suffix")
        assert trimsuffix(CtyValue.null(CtyString()), suffix).is_unknown
        assert trimsuffix(s, CtyValue.null(CtyString())).is_unknown
        assert trimsuffix(CtyValue.unknown(CtyString()), suffix).is_unknown
        assert trimsuffix(s, CtyValue.unknown(CtyString())).is_unknown

    def test_trimsuffix_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import trimsuffix
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            trimsuffix(CtyNumber().validate(123), CtyString().validate("s"))
        with pytest.raises(CtyFunctionError):
            trimsuffix(CtyString().validate("a"), CtyNumber().validate(123))

    def test_regex(self) -> None:
        """Pattern first, then the string. The result shape follows the capture
        groups; that, and everything else, is pinned against real go-cty in
        tests/functions/test_gocty_regexp_parity.py."""
        assert regex(CtyString().validate(r"\w+"), CtyString().validate("hello world")).value == "hello"

    def test_regexall(self) -> None:
        result = regexall(CtyString().validate(r"\w+"), CtyString().validate("hello world"))
        assert [v.value for v in result.value] == ["hello", "world"]

    def test_regexreplace(self) -> None:
        from pyvider.cty.functions import regexreplace

        assert regexreplace(S("a1b2"), S(r"\d"), S("*")).value == "a*b*"

    def test_regexreplace_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import regexreplace
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            regexreplace(
                CtyNumber().validate(123),
                CtyString().validate("a"),
                CtyString().validate("b"),
            )
        with pytest.raises(CtyFunctionError):
            regexreplace(
                CtyString().validate("a"),
                CtyNumber().validate(123),
                CtyString().validate("b"),
            )
        with pytest.raises(CtyFunctionError):
            regexreplace(
                CtyString().validate("a"),
                CtyString().validate("b"),
                CtyNumber().validate(123),
            )

    def test_regexreplace_null_unknown(self) -> None:
        assert regexreplace(CtyValue.null(CtyString()), S("a"), S("b")).is_unknown
        assert regexreplace(S("a"), CtyValue.null(CtyString()), S("b")).is_unknown
        assert regexreplace(S("a"), S("b"), CtyValue.null(CtyString())).is_unknown
        assert regexreplace(CtyValue.unknown(CtyString()), S("a"), S("b")).is_unknown
        assert regexreplace(S("a"), CtyValue.unknown(CtyString()), S("b")).is_unknown
        assert regexreplace(S("a"), S("b"), CtyValue.unknown(CtyString())).is_unknown


# 🌊🪢🔚
