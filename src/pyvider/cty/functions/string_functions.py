import re
from typing import Any

from pyvider.cty import CtyList, CtyNumber, CtyString, CtyTuple, CtyValue
from pyvider.cty.exceptions import CtyFunctionError


def chomp(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(
            f"chomp: input must be a string, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if not isinstance(s, str):
        raise CtyFunctionError("chomp: input must be a string")
    if s.endswith("\r\n"):
        return CtyString().validate(s[:-2])
    if s.endswith("\n") or s.endswith("\r"):
        return CtyString().validate(s[:-1])
    return input_val


def strrev(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(
            f"strrev: input must be a string, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return input_val
    if not isinstance(input_val.value, str):
        raise CtyFunctionError("strrev: input must be a string")
    return CtyString().validate(input_val.value[::-1])


def trimspace(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(
            f"trimspace: input must be a string, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return input_val
    if not isinstance(input_val.value, str):
        raise CtyFunctionError("trimspace: input must be a string")
    return CtyString().validate(input_val.value.strip())


def indent(prefix_val: "CtyValue[Any]", input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(prefix_val.type, CtyString) or not isinstance(
        input_val.type, CtyString
    ):
        raise CtyFunctionError("indent: arguments must be strings")
    if (
        input_val.is_null
        or input_val.is_unknown
        or prefix_val.is_null
        or prefix_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    if not isinstance(input_val.value, str) or not isinstance(prefix_val.value, str):
        raise CtyFunctionError("indent: arguments must be strings")
    indented_lines = [
        f"{prefix_val.value}{line}" for line in input_val.value.splitlines()
    ]
    return CtyString().validate("\n".join(indented_lines))


def substr(
    input_val: "CtyValue[Any]", offset_val: "CtyValue[Any]", length_val: "CtyValue[Any]"
) -> "CtyValue[Any]":
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    if not isinstance(offset_val.value, int | float) or not isinstance(
        length_val.value, int | float
    ):
        raise CtyFunctionError("substr: offset and length must be numbers")
    offset, length = int(offset_val.value), int(length_val.value)
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = input_val.value
    if not isinstance(s, str):
        raise CtyFunctionError("substr: input must be a string")
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def trim(input_val: "CtyValue[Any]", cutset_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString) or not isinstance(
        cutset_val.type, CtyString
    ):
        raise CtyFunctionError("trim: both arguments must be strings")
    if (
        input_val.is_null
        or input_val.is_unknown
        or cutset_val.is_null
        or cutset_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    if not isinstance(input_val.value, str) or not isinstance(cutset_val.value, str):
        raise CtyFunctionError("trim: both arguments must be strings")
    return CtyString().validate(input_val.value.strip(cutset_val.value))


def title(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(
            f"title: input must be a string, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return input_val
    if not isinstance(input_val.value, str):
        raise CtyFunctionError("title: input must be a string")
    return CtyString().validate(input_val.value.title())


def trimprefix(
    input_val: "CtyValue[Any]", prefix_val: "CtyValue[Any]"
) -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString) or not isinstance(
        prefix_val.type, CtyString
    ):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if (
        input_val.is_null
        or input_val.is_unknown
        or prefix_val.is_null
        or prefix_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    if not isinstance(input_val.value, str) or not isinstance(prefix_val.value, str):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.value.startswith(prefix_val.value):
        return CtyString().validate(input_val.value[len(prefix_val.value) :])
    return input_val


def trimsuffix(
    input_val: "CtyValue[Any]", suffix_val: "CtyValue[Any]"
) -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString) or not isinstance(
        suffix_val.type, CtyString
    ):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if (
        input_val.is_null
        or input_val.is_unknown
        or suffix_val.is_null
        or suffix_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    if not isinstance(input_val.value, str) or not isinstance(suffix_val.value, str):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.value.endswith(suffix_val.value):
        return CtyString().validate(input_val.value[: -len(suffix_val.value)])
    return input_val


def regex(input_val: "CtyValue[Any]", pattern_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString) or not isinstance(
        pattern_val.type, CtyString
    ):
        raise CtyFunctionError("regex: both arguments must be strings")
    if (
        input_val.is_null
        or input_val.is_unknown
        or pattern_val.is_null
        or pattern_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    if not isinstance(input_val.value, str) or not isinstance(pattern_val.value, str):
        raise CtyFunctionError("regex: both arguments must be strings")
    try:
        match = re.search(pattern_val.value, input_val.value)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def regexall(
    input_val: "CtyValue[Any]", pattern_val: "CtyValue[Any]"
) -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString) or not isinstance(
        pattern_val.type, CtyString
    ):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if (
        input_val.is_null
        or input_val.is_unknown
        or pattern_val.is_null
        or pattern_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    if not isinstance(input_val.value, str) or not isinstance(pattern_val.value, str):
        raise CtyFunctionError("regexall: both arguments must be strings")
    try:
        matches = re.findall(pattern_val.value, input_val.value)
        return CtyList(element_type=CtyString()).validate(matches)
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def upper(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(
            f"upper: input must be a string, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return input_val
    if not isinstance(input_val.value, str):
        raise CtyFunctionError("upper: input must be a string")
    return CtyString().validate(input_val.value.upper())


def lower(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(
            f"lower: input must be a string, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return input_val
    if not isinstance(input_val.value, str):
        raise CtyFunctionError("lower: input must be a string")
    return CtyString().validate(input_val.value.lower())


def join(separator: "CtyValue[Any]", elements: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(separator.type, CtyString) or not isinstance(
        elements.type, CtyList | CtyTuple
    ):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if (
        separator.is_null
        or separator.is_unknown
        or elements.is_null
        or elements.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    if not isinstance(separator.value, str) or not hasattr(elements.value, "__iter__"):
        raise CtyFunctionError("join: arguments must be string and iterable")

    str_elements = [str(el.value) for el in elements.value]  # type: ignore
    return CtyString().validate(separator.value.join(str_elements))


def split(separator: "CtyValue[Any]", text: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(separator.type, CtyString) or not isinstance(
        text.type, CtyString
    ):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    if not isinstance(separator.value, str) or not isinstance(text.value, str):
        raise CtyFunctionError("split: arguments must be strings")
    parts = text.value.split(separator.value)
    return CtyList(element_type=CtyString()).validate(parts)


def replace(
    string: "CtyValue[Any]", substring: "CtyValue[Any]", replacement: "CtyValue[Any]"
) -> "CtyValue[Any]":
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    if (
        not isinstance(string.value, str)
        or not isinstance(substring.value, str)
        or not isinstance(replacement.value, str)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    result = string.value.replace(substring.value, replacement.value)
    return CtyString().validate(result)


def regexreplace(
    string: "CtyValue[Any]", pattern: "CtyValue[Any]", replacement: "CtyValue[Any]"
) -> "CtyValue[Any]":
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    if (
        not isinstance(string.value, str)
        or not isinstance(pattern.value, str)
        or not isinstance(replacement.value, str)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    try:
        result = re.sub(pattern.value, replacement.value, string.value)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e
