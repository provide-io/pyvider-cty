"""
Comprehensive test suite for all standard library functions to ensure
parity with go-cty.
"""

from decimal import Decimal

import pytest

from pyvider.cty import (
    BytesCapsule,
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    abs_fn,
    add,
    byteslen,
    bytesslice,
    ceil_fn,
    chomp,
    chunklist,
    coalesce,
    coalescelist,
    compact,
    csvdecode,
    divide,
    element,
    equal,
    floor_fn,
    formatdate,
    greater_than,
    greater_than_or_equal_to,
    hasindex,
    indent,
    index,
    int_fn,
    join,
    jsondecode,
    jsonencode,
    less_than,
    less_than_or_equal_to,
    log_fn,
    lookup,
    lower,
    max_fn,
    merge,
    min_fn,
    modulo,
    multiply,
    negate,
    not_equal,
    parseint_fn,
    pow_fn,
    regex,
    regexall,
    regexreplace,
    replace,
    reverse,
    setproduct,
    signum_fn,
    split,
    strrev,
    substr,
    subtract,
    timeadd,
    title,
    trim,
    trimprefix,
    trimspace,
    trimsuffix,
    upper,
    zipmap,
)


# Helper functions for creating CtyValues to improve test readability
def S(v):
    return CtyString().validate(v)


def N(v):
    return CtyNumber().validate(v)


def B(v):
    return CtyBool().validate(v)


def L(t, v):
    return CtyList(element_type=t).validate(v)


def M(t, v):
    return CtyMap(element_type=t).validate(v)


def Set(t, v):
    return CtySet(element_type=t).validate(v)


class TestComparisonFunctions:
    def test_equal(self) -> None:
        assert equal(N(5), N(5)).is_true()
        assert equal(S("a"), S("b")).is_false()
        assert equal(CtyValue.unknown(CtyNumber()), N(5)).is_unknown

    def test_not_equal(self) -> None:
        assert not_equal(N(5), N(5)).is_false()
        assert not_equal(S("a"), S("b")).is_true()
        assert not_equal(CtyValue.unknown(CtyNumber()), N(5)).is_unknown

    def test_less_than(self) -> None:
        assert less_than(N(5), N(10)).is_true()
        assert less_than(S("a"), S("b")).is_true()
        with pytest.raises(CtyFunctionError):
            less_than(N(1), S("a"))

    def test_max_min(self) -> None:
        assert max_fn(N(1), N(10), N(5)).value == 10
        assert min_fn(S("z"), S("a"), S("m")).value == "a"
        with pytest.raises(CtyFunctionError):
            min_fn(N(1), S("a"))

    def test_compare_with_null(self) -> None:
        assert greater_than(CtyValue.null(CtyNumber()), N(1)).is_unknown
        assert greater_than(N(1), CtyValue.null(CtyNumber())).is_unknown

    def test_multi_compare_no_args(self) -> None:
        with pytest.raises(CtyFunctionError):
            max_fn()
        with pytest.raises(CtyFunctionError):
            min_fn()

    def test_multi_compare_all_null(self) -> None:
        assert max_fn(CtyValue.null(CtyNumber()), CtyValue.null(CtyNumber())).is_null

    def test_multi_compare_mixed_types(self) -> None:
        with pytest.raises(CtyFunctionError):
            max_fn(N(1), S("a"))

    def test_greater_than_or_equal_to(self) -> None:
        assert greater_than_or_equal_to(N(2), N(1)).is_true()
        assert greater_than_or_equal_to(N(1), N(1)).is_true()
        assert greater_than_or_equal_to(N(1), N(2)).is_false()

    def test_less_than_or_equal_to(self) -> None:
        assert less_than_or_equal_to(N(1), N(2)).is_true()
        assert less_than_or_equal_to(N(1), N(1)).is_true()
        assert less_than_or_equal_to(N(2), N(1)).is_false()


class TestNumericFunctions:
    def test_int_fn(self) -> None:
        assert int_fn(N(5.9)).value == 5
        assert int_fn(N(-5.9)).value == -5

    def test_int_fn_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            int_fn(S("a"))

    def test_int_fn_null_unknown(self) -> None:
        assert int_fn(CtyValue.null(CtyNumber())).is_null
        assert int_fn(CtyValue.unknown(CtyNumber())).is_unknown

    def test_add_numbers(self) -> None:
        assert add(CtyNumber().validate(1), CtyNumber().validate(2)).value == 3
        assert add(CtyNumber().validate(-1), CtyNumber().validate(2)).value == 1
        assert add(CtyNumber().validate(1.5), CtyNumber().validate(2.5)).value == 4.0

    def test_add_null(self) -> None:
        assert add(CtyValue.null(CtyNumber()), CtyNumber().validate(1)).is_unknown
        assert add(CtyNumber().validate(1), CtyValue.null(CtyNumber())).is_unknown

    def test_add_unknown(self) -> None:
        assert add(CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
        assert add(CtyNumber().validate(1), CtyValue.unknown(CtyNumber())).is_unknown

    def test_add_type_error(self) -> None:
        with pytest.raises(CtyFunctionError):
            add(CtyString().validate("a"), CtyNumber().validate(1))

    def test_subtract_numbers(self) -> None:
        assert subtract(CtyNumber().validate(3), CtyNumber().validate(2)).value == 1
        assert subtract(CtyNumber().validate(-1), CtyNumber().validate(2)).value == -3
        assert subtract(CtyNumber().validate(2.5), CtyNumber().validate(1.5)).value == 1.0

    def test_multiply_numbers(self) -> None:
        assert multiply(CtyNumber().validate(3), CtyNumber().validate(2)).value == 6
        assert multiply(CtyNumber().validate(-1), CtyNumber().validate(2)).value == -2
        assert multiply(CtyNumber().validate(1.5), CtyNumber().validate(2)).value == 3.0

    def test_divide_numbers(self) -> None:
        assert divide(CtyNumber().validate(6), CtyNumber().validate(2)).value == 3
        assert divide(CtyNumber().validate(-4), CtyNumber().validate(2)).value == -2
        assert divide(CtyNumber().validate(5), CtyNumber().validate(2)).value == 2.5

    def test_divide_by_zero(self) -> None:
        with pytest.raises(CtyFunctionError, match="divide by zero"):
            divide(CtyNumber().validate(1), CtyNumber().validate(0))

    def test_modulo_numbers(self) -> None:
        assert modulo(CtyNumber().validate(5), CtyNumber().validate(2)).value == 1
        assert modulo(CtyNumber().validate(-5), CtyNumber().validate(2)).value == -1
        assert modulo(CtyNumber().validate(5.5), CtyNumber().validate(2)).value == 1.5

    def test_modulo_by_zero(self) -> None:
        with pytest.raises(CtyFunctionError, match="modulo by zero"):
            modulo(CtyNumber().validate(1), CtyNumber().validate(0))

    def test_negate_number(self) -> None:
        assert negate(CtyNumber().validate(5)).value == -5
        assert negate(CtyNumber().validate(-5)).value == 5
        assert negate(CtyNumber().validate(0)).value == 0

    def test_abs_fn(self) -> None:
        assert abs_fn(CtyNumber().validate(5)).value == 5
        assert abs_fn(CtyNumber().validate(-5)).value == 5
        assert abs_fn(CtyNumber().validate(0)).value == 0
        assert abs_fn(CtyNumber().validate(-5.5)).value == 5.5

    def test_abs_fn_null_unknown(self) -> None:
        assert abs_fn(CtyValue.null(CtyNumber())).is_null
        assert abs_fn(CtyValue.unknown(CtyNumber())).is_unknown

    def test_abs_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            abs_fn(CtyString().validate("not a number"))

    def test_ceil_fn(self) -> None:
        assert ceil_fn(CtyNumber().validate(5.1)).value == Decimal("6")
        assert ceil_fn(CtyNumber().validate(5.9)).value == Decimal("6")
        assert ceil_fn(CtyNumber().validate(5.0)).value == Decimal("5")
        assert ceil_fn(CtyNumber().validate(-5.1)).value == Decimal("-5")

    def test_ceil_fn_null_unknown(self) -> None:
        assert ceil_fn(CtyValue.null(CtyNumber())).is_null
        assert ceil_fn(CtyValue.unknown(CtyNumber())).is_unknown

    def test_ceil_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            ceil_fn(CtyString().validate("not a number"))

    def test_floor_fn(self) -> None:
        assert floor_fn(CtyNumber().validate(5.1)).value == Decimal("5")
        assert floor_fn(CtyNumber().validate(5.9)).value == Decimal("5")
        assert floor_fn(CtyNumber().validate(5.0)).value == Decimal("5")
        assert floor_fn(CtyNumber().validate(-5.1)).value == Decimal("-6")

    def test_floor_fn_null_unknown(self) -> None:
        assert floor_fn(CtyValue.null(CtyNumber())).is_null
        assert floor_fn(CtyValue.unknown(CtyNumber())).is_unknown

    def test_floor_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            floor_fn(CtyString().validate("not a number"))

    def test_log_fn(self) -> None:
        assert log_fn(CtyNumber().validate(100), CtyNumber().validate(10)).value == Decimal("2")
        assert log_fn(CtyNumber().validate(8), CtyNumber().validate(2)).value == Decimal("3")

    def test_log_fn_null_unknown(self) -> None:
        assert log_fn(CtyValue.null(CtyNumber()), CtyNumber().validate(10)).is_unknown
        assert log_fn(CtyNumber().validate(100), CtyValue.null(CtyNumber())).is_unknown
        assert log_fn(CtyValue.unknown(CtyNumber()), CtyNumber().validate(10)).is_unknown
        assert log_fn(CtyNumber().validate(100), CtyValue.unknown(CtyNumber())).is_unknown

    def test_log_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            log_fn(CtyString().validate("a"), CtyNumber().validate(10))
        with pytest.raises(CtyFunctionError):
            log_fn(CtyNumber().validate(100), CtyString().validate("b"))

    def test_log_fn_invalid_values(self) -> None:
        with pytest.raises(CtyFunctionError):
            log_fn(CtyNumber().validate(-1), CtyNumber().validate(10))
        with pytest.raises(CtyFunctionError):
            log_fn(CtyNumber().validate(100), CtyNumber().validate(-1))
        with pytest.raises(CtyFunctionError):
            log_fn(CtyNumber().validate(100), CtyNumber().validate(1))

    def test_pow_fn(self) -> None:
        assert pow_fn(CtyNumber().validate(2), CtyNumber().validate(3)).value == 8
        assert pow_fn(CtyNumber().validate(4), CtyNumber().validate(0.5)).value == 2

    def test_pow_fn_null_unknown(self) -> None:
        assert pow_fn(CtyValue.null(CtyNumber()), CtyNumber().validate(2)).is_unknown
        assert pow_fn(CtyNumber().validate(2), CtyValue.null(CtyNumber())).is_unknown
        assert pow_fn(CtyValue.unknown(CtyNumber()), CtyNumber().validate(2)).is_unknown
        assert pow_fn(CtyNumber().validate(2), CtyValue.unknown(CtyNumber())).is_unknown

    def test_pow_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            pow_fn(CtyString().validate("a"), CtyNumber().validate(2))
        with pytest.raises(CtyFunctionError):
            pow_fn(CtyNumber().validate(2), CtyString().validate("b"))

    def test_signum_fn(self) -> None:
        assert signum_fn(CtyNumber().validate(10)).value == 1
        assert signum_fn(CtyNumber().validate(-10)).value == -1
        assert signum_fn(CtyNumber().validate(0)).value == 0

    def test_signum_fn_null_unknown(self) -> None:
        assert signum_fn(CtyValue.null(CtyNumber())).is_null
        assert signum_fn(CtyValue.unknown(CtyNumber())).is_unknown

    def test_signum_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            signum_fn(CtyString().validate("a"))

    def test_parseint_fn(self) -> None:
        assert parseint_fn(CtyString().validate("10"), CtyNumber().validate(10)).value == 10
        assert parseint_fn(CtyString().validate("FF"), CtyNumber().validate(16)).value == 255
        assert parseint_fn(CtyString().validate("0xFF"), CtyNumber().validate(0)).value == 255

    def test_parseint_fn_null_result(self) -> None:
        assert parseint_fn(CtyString().validate("z"), CtyNumber().validate(10)).is_null

    def test_parseint_fn_null_unknown(self) -> None:
        assert parseint_fn(CtyValue.null(CtyString()), CtyNumber().validate(10)).is_null
        assert parseint_fn(CtyString().validate("10"), CtyValue.null(CtyNumber())).is_null
        assert parseint_fn(CtyValue.unknown(CtyString()), CtyNumber().validate(10)).is_unknown
        assert parseint_fn(CtyString().validate("10"), CtyValue.unknown(CtyNumber())).is_unknown

    def test_parseint_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            parseint_fn(CtyNumber().validate(10), CtyNumber().validate(10))
        with pytest.raises(CtyFunctionError):
            parseint_fn(CtyString().validate("10"), CtyString().validate("10"))

    def test_parseint_fn_invalid_base(self) -> None:
        with pytest.raises(CtyFunctionError):
            parseint_fn(CtyString().validate("10"), CtyNumber().validate(1))
        with pytest.raises(CtyFunctionError):
            parseint_fn(CtyString().validate("10"), CtyNumber().validate(37))

    def test_add_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            add(CtyString().validate("a"), CtyString().validate("b"))

    def test_subtract_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            subtract(CtyString().validate("a"), CtyString().validate("b"))

    def test_multiply_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            multiply(CtyString().validate("a"), CtyString().validate("b"))

    def test_divide_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            divide(CtyString().validate("a"), CtyString().validate("b"))

    def test_modulo_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            modulo(CtyString().validate("a"), CtyString().validate("b"))

    def test_pow_invalid_operation(self) -> None:
        with pytest.raises(CtyFunctionError):
            pow_fn(CtyNumber().validate(-1), CtyNumber().validate(0.5))

    def test_add_invalid_types(self) -> None:
        with pytest.raises(CtyFunctionError):
            add(CtyString().validate("a"), CtyNumber().validate(1))
        with pytest.raises(CtyFunctionError):
            add(CtyNumber().validate(1), CtyString().validate("a"))


class TestStringFunctions:
    def test_join(self) -> None:
        assert join(S(","), L(CtyString(), ["a", "b"])).value == "a,b"

    def test_split(self) -> None:
        assert split(S(","), S("a,b,c")).raw_value == ["a", "b", "c"]

    def test_replace(self) -> None:
        assert replace(S("a-b-c"), S("-"), S(":")).value == "a:b:c"

    def test_regexreplace(self) -> None:
        assert regexreplace(S("a1b2"), S(r"\d"), S("*")).value == "a*b*"

    def test_upper_with_null_and_unknown(self) -> None:
        assert upper(CtyValue.null(CtyString())).is_null
        assert upper(CtyValue.unknown(CtyString())).is_unknown

    def test_lower_with_null_and_unknown(self) -> None:
        assert lower(CtyValue.null(CtyString())).is_null
        assert lower(CtyValue.unknown(CtyString())).is_unknown

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

    def test_upper(self) -> None:
        assert upper(CtyString().validate("hello")).value == "HELLO"

    def test_lower(self) -> None:
        assert lower(CtyString().validate("HELLO")).value == "hello"

    def test_indent(self) -> None:
        prefix = CtyString().validate("  ")
        text = CtyString().validate("hello\nworld")
        result = indent(prefix, text)
        assert result.value == "  hello\n  world"

    def test_indent_empty_string(self) -> None:
        prefix = CtyString().validate("  ")
        text = CtyString().validate("")
        result = indent(prefix, text)
        assert result.value == "  "

    def test_indent_no_newlines(self) -> None:
        prefix = CtyString().validate(">> ")
        text = CtyString().validate("single line")
        result = indent(prefix, text)
        assert result.value == ">> single line"

    def test_indent_null_unknown(self) -> None:
        prefix = CtyString().validate("  ")
        text = CtyString().validate("hello")
        assert indent(CtyValue.null(CtyString()), text).is_unknown
        assert indent(prefix, CtyValue.null(CtyString())).is_unknown
        assert indent(CtyValue.unknown(CtyString()), text).is_unknown
        assert indent(prefix, CtyValue.unknown(CtyString())).is_unknown

    def test_indent_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import indent
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            indent(CtyNumber().validate(123), CtyString().validate("hello"))
        with pytest.raises(CtyFunctionError):
            indent(CtyString().validate("  "), CtyNumber().validate(123))

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
        s = CtyString().validate("hello world")
        pattern = CtyString().validate(r"\w+")
        result = regex(s, pattern)
        assert result.value == "hello"

    def test_regex_no_match(self) -> None:
        s = CtyString().validate("hello world")
        pattern = CtyString().validate(r"\d+")
        result = regex(s, pattern)
        assert result.value == ""

    def test_regex_invalid_pattern(self) -> None:
        s = CtyString().validate("hello")
        pattern = CtyString().validate("[")
        with pytest.raises(CtyFunctionError):
            regex(s, pattern)

    def test_regex_null_unknown(self) -> None:
        s = CtyString().validate("hello")
        pattern = CtyString().validate(".")
        assert regex(CtyValue.null(CtyString()), pattern).is_unknown
        assert regex(s, CtyValue.null(CtyString())).is_unknown
        assert regex(CtyValue.unknown(CtyString()), pattern).is_unknown
        assert regex(s, CtyValue.unknown(CtyString())).is_unknown

    def test_regex_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import regex
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            regex(CtyNumber().validate(123), CtyString().validate("."))
        with pytest.raises(CtyFunctionError):
            regex(CtyString().validate("a"), CtyNumber().validate(123))

    def test_regexall(self) -> None:
        s = CtyString().validate("hello world")
        pattern = CtyString().validate(r"\w+")
        result = regexall(s, pattern)
        assert [v.value for v in result.value] == ["hello", "world"]

    def test_regexall_no_match(self) -> None:
        s = CtyString().validate("hello world")
        pattern = CtyString().validate(r"\d+")
        result = regexall(s, pattern)
        assert [v.value for v in result.value] == []

    def test_regexall_invalid_pattern(self) -> None:
        s = CtyString().validate("hello")
        pattern = CtyString().validate("[")
        with pytest.raises(CtyFunctionError):
            regexall(s, pattern)

    def test_regexall_null_unknown(self) -> None:
        s = CtyString().validate("hello")
        pattern = CtyString().validate(".")
        assert regexall(CtyValue.null(CtyString()), pattern).is_unknown
        assert regexall(s, CtyValue.null(CtyString())).is_unknown
        assert regexall(CtyValue.unknown(CtyString()), pattern).is_unknown
        assert regexall(s, CtyValue.unknown(CtyString())).is_unknown

    def test_regexall_wrong_type(self) -> None:
        from pyvider.cty.functions.string_functions import regexall
        from pyvider.cty.types import CtyNumber

        with pytest.raises(CtyFunctionError):
            regexall(CtyNumber().validate(123), CtyString().validate("."))
        with pytest.raises(CtyFunctionError):
            regexall(CtyString().validate("a"), CtyNumber().validate(123))

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

    def test_regexreplace_null_unknown(self) -> None:
        assert regexreplace(CtyValue.null(CtyString()), S("a"), S("b")).is_unknown
        assert regexreplace(S("a"), CtyValue.null(CtyString()), S("b")).is_unknown
        assert regexreplace(S("a"), S("b"), CtyValue.null(CtyString())).is_unknown
        assert regexreplace(CtyValue.unknown(CtyString()), S("a"), S("b")).is_unknown
        assert regexreplace(S("a"), CtyValue.unknown(CtyString()), S("b")).is_unknown
        assert regexreplace(S("a"), S("b"), CtyValue.unknown(CtyString())).is_unknown


class TestCollectionFunctions:
    def test_reverse(self) -> None:
        assert reverse(L(CtyString(), ["a", "b", "c"])).raw_value == ["c", "b", "a"]

    def test_hasindex(self) -> None:
        assert hasindex(L(CtyString(), ["a"]), N(0)).is_true()
        assert hasindex(M(CtyString(), {"k": "v"}), S("k")).is_true()
        assert hasindex(M(CtyString(), {"k": "v"}), S("z")).is_false()

    def test_index(self) -> None:
        assert index(L(CtyString(), ["a", "b"]), N(1)).value == "b"
        with pytest.raises(CtyFunctionError):
            index(L(CtyString(), []), N(0))

    def test_element(self) -> None:
        assert element(L(CtyString(), ["a", "b"]), N(3)).value == "b"  # wraps

    def test_coalescelist(self) -> None:
        l1, l2 = L(CtyString(), []), L(CtyString(), ["a"])
        assert coalescelist(l1, l2).raw_value == ["a"]

    def test_compact(self) -> None:
        assert compact(L(CtyString(), ["a", "", "b"])).raw_value == ["a", "b"]

    def test_chunklist(self) -> None:
        l = L(CtyString(), ["a", "b", "c", "d", "e"])
        assert chunklist(l, N(2)).raw_value == [["a", "b"], ["c", "d"], ["e"]]

    def test_lookup(self) -> None:
        m = M(CtyString(), {"a": "b"})
        assert lookup(m, S("a"), S("z")).value == "b"
        assert lookup(m, S("x"), S("z")).value == "z"

    def test_merge(self) -> None:
        m1 = M(CtyString(), {"a": "1", "b": "2"})
        m2 = M(CtyString(), {"b": "3", "c": "4"})
        assert merge(m1, m2).raw_value == {"a": "1", "b": "3", "c": "4"}

    def test_setproduct(self) -> None:
        s1 = Set(CtyString(), ["a", "b"])
        s2 = Set(CtyNumber(), [1, 2])
        prod = setproduct(s1, s2)
        assert isinstance(prod.type, CtySet)
        assert isinstance(prod.type.element_type, CtyTuple)
        result_set = {item.raw_value for item in prod.value}
        expected_set = {("a", 1), ("a", 2), ("b", 1), ("b", 2)}
        assert result_set == expected_set

    def test_zipmap(self) -> None:
        keys = L(CtyString(), ["a", "b"])
        vals = L(CtyNumber(), [1, 2])
        assert zipmap(keys, vals).raw_value == {"a": 1, "b": 2}


class TestEncodingFunctions:
    def test_jsonencode(self) -> None:
        val = M(CtyString(), {"a": "b"})
        assert jsonencode(val).value == '{"a": "b"}'

    def test_jsondecode(self) -> None:
        val = S('{"a": "b"}')
        decoded = jsondecode(val)
        assert isinstance(decoded.type, CtyDynamic)
        assert decoded.raw_value == {"a": "b"}

    def test_csvdecode(self) -> None:
        val = S("a,b\n1,2\n3,4")
        decoded = csvdecode(val)
        assert decoded.raw_value == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]


class TestDateTimeFunctions:
    def test_formatdate(self) -> None:
        ts = S("2020-02-03T04:05:06Z")
        assert formatdate(S("2006-01-02"), ts).value == "2020-02-03"

    def test_timeadd(self) -> None:
        ts = S("2020-01-02T03:04:05Z")
        dur = S("1h30m")
        assert "T04:34:05" in timeadd(ts, dur).value

    def test_formatdate_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            formatdate(CtyNumber().validate(123), S("..."))
        with pytest.raises(CtyFunctionError):
            formatdate(S("..."), CtyNumber().validate(123))

    def test_formatdate_null_unknown(self) -> None:
        spec = S("YYYY")
        ts = S("2020-01-01T00:00:00Z")
        assert formatdate(CtyValue.null(CtyString()), ts).is_unknown
        assert formatdate(CtyValue.unknown(CtyString()), ts).is_unknown
        assert formatdate(spec, CtyValue.null(CtyString())).is_unknown
        assert formatdate(spec, CtyValue.unknown(CtyString())).is_unknown

    def test_formatdate_invalid_timestamp(self) -> None:
        with pytest.raises(CtyFunctionError):
            formatdate(S("YYYY"), S("not a timestamp"))

    def test_timeadd_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            timeadd(CtyNumber().validate(123), S("1h"))
        with pytest.raises(CtyFunctionError):
            timeadd(S("..."), CtyNumber().validate(123))

    def test_timeadd_null_unknown(self) -> None:
        ts = S("2020-01-01T00:00:00Z")
        dur = S("1h")
        assert timeadd(CtyValue.null(CtyString()), dur).is_unknown
        assert timeadd(CtyValue.unknown(CtyString()), dur).is_unknown
        assert timeadd(ts, CtyValue.null(CtyString())).is_unknown
        assert timeadd(ts, CtyValue.unknown(CtyString())).is_unknown

    def test_timeadd_invalid_timestamp(self) -> None:
        with pytest.raises(CtyFunctionError):
            timeadd(S("not a timestamp"), S("1h"))

    def test_timeadd_invalid_duration(self) -> None:
        with pytest.raises(CtyFunctionError):
            timeadd(
                S("2020-01-01T00:00:00Z"),
                S("not a duration"),
            )


class TestBytesFunctions:
    def test_byteslen(self) -> None:
        assert byteslen(BytesCapsule.validate(b"hello")).value == 5

    def test_bytesslice(self) -> None:
        assert bytesslice(BytesCapsule.validate(b"hello"), N(1), N(4)).value == b"ell"

    def test_byteslen_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            byteslen(S("hello"))

    def test_byteslen_null_unknown(self) -> None:
        assert byteslen(CtyValue.null(BytesCapsule)).is_unknown
        assert byteslen(CtyValue.unknown(BytesCapsule)).is_unknown

    def test_bytesslice_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            bytesslice(S("hello"), N(0), N(1))
        with pytest.raises(CtyFunctionError):
            bytesslice(BytesCapsule.validate(b"hello"), S("0"), N(1))
        with pytest.raises(CtyFunctionError):
            bytesslice(BytesCapsule.validate(b"hello"), N(0), S("1"))

    def test_bytesslice_null_unknown(self) -> None:
        assert bytesslice(CtyValue.null(BytesCapsule), N(0), N(1)).is_unknown
        assert bytesslice(CtyValue.unknown(BytesCapsule), N(0), N(1)).is_unknown
        assert bytesslice(BytesCapsule.validate(b"hello"), CtyValue.null(CtyNumber()), N(1)).is_unknown
        assert bytesslice(BytesCapsule.validate(b"hello"), CtyValue.unknown(CtyNumber()), N(1)).is_unknown
        assert bytesslice(BytesCapsule.validate(b"hello"), N(0), CtyValue.null(CtyNumber())).is_unknown
        assert bytesslice(BytesCapsule.validate(b"hello"), N(0), CtyValue.unknown(CtyNumber())).is_unknown


class TestStructuralFunctions:
    def test_coalesce(self) -> None:
        val1 = S("a")
        val2 = S("b")
        null_val = CtyValue.null(CtyString())
        assert coalesce(val1, val2).value == "a"
        assert coalesce(null_val, val2).value == "b"
        assert coalesce(null_val, null_val, val1).value == "a"
