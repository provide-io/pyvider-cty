# pyvider-cty/src/pyvider/cty/functions/string_functions.py
from pyvider.cty import CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError


def chomp(input_val: CtyValue) -> CtyValue:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"): return CtyString().validate(s[:-2])
    if s.endswith("\n"): return CtyString().validate(s[:-1])
    return input_val

def strrev(input_val: CtyValue) -> CtyValue:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"strrev: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value[::-1])

def trimspace(input_val: CtyValue) -> CtyValue:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"trimspace: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value.strip())

def indent(prefix_val: CtyValue, input_val: CtyValue) -> CtyValue:
    if not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError(f"indent: prefix must be a string, got {prefix_val.type.ctype}")
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"indent: input must be a string, got {input_val.type.ctype}")

    if prefix_val.is_unknown or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if prefix_val.is_null or input_val.is_null:
        return input_val

    prefix, s = prefix_val.value, input_val.value
    if not s: return CtyString().validate("")

    lines = s.split('\n')
    if s.endswith('\n'):
        return CtyString().validate('\n'.join(prefix + line for line in lines[:-1]) + '\n')
    return CtyString().validate('\n'.join(prefix + line for line in lines))

def substr(input_val: CtyValue, offset_val: CtyValue, length_val: CtyValue) -> CtyValue:
    from pyvider.cty.types import CtyNumber
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"substr: input must be a string, got {input_val.type.ctype}")
    if not isinstance(offset_val.type, CtyNumber) or not isinstance(length_val.type, CtyNumber):
        raise CtyFunctionError("substr: offset and length must be numbers")

    if input_val.is_unknown or offset_val.is_unknown or length_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if input_val.is_null or offset_val.is_null or length_val.is_null:
        raise CtyFunctionError("substr: cannot operate on null values")

    s, offset, length = input_val.value, int(offset_val.value), int(length_val.value)
    s_len = len(s)
    if offset < 0: offset += s_len
    if offset < 0: offset = 0
    if offset > s_len: return CtyString().validate("")
    if length == -1: return CtyString().validate(s[offset:])
    if length < 0: raise CtyFunctionError("substr: length cannot be negative (unless -1)")

    end = offset + length
    return CtyString().validate(s[offset:min(end, s_len)])

def trim(input_val: CtyValue, cutset_val: CtyValue) -> CtyValue:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")

    if input_val.is_unknown or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if input_val.is_null or cutset_val.is_null:
        return input_val

    return CtyString().validate(input_val.value.strip(cutset_val.value))

def title(input_val: CtyValue) -> CtyValue:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value.title())

def trimprefix(input_val: CtyValue, prefix_val: CtyValue) -> CtyValue:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")

    if input_val.is_unknown or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if input_val.is_null or prefix_val.is_null:
        return input_val

    return CtyString().validate(input_val.value.removeprefix(prefix_val.value))

def trimsuffix(input_val: CtyValue, suffix_val: CtyValue) -> CtyValue:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")

    if input_val.is_unknown or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if input_val.is_null or suffix_val.is_null:
        return input_val

    return CtyString().validate(input_val.value.removesuffix(suffix_val.value))

def regex(pattern_val: CtyValue, input_val: CtyValue) -> CtyValue:
    import re

    from pyvider.cty.types import CtyBool
    if not isinstance(pattern_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")

    if pattern_val.is_unknown or input_val.is_unknown:
        return CtyValue.unknown(CtyBool())
    if pattern_val.is_null or input_val.is_null:
        raise CtyFunctionError("regex: cannot operate on null values")

    try:
        return CtyBool().validate(re.search(pattern_val.value, input_val.value) is not None)
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}")

def regexall(pattern_val: CtyValue, input_val: CtyValue) -> CtyValue:
    import re

    from pyvider.cty.types import CtyList
    if not isinstance(pattern_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")

    if pattern_val.is_unknown or input_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    if pattern_val.is_null or input_val.is_null:
        raise CtyFunctionError("regexall: cannot operate on null values")

    try:
        matches = re.findall(pattern_val.value, input_val.value)
        return CtyList(element_type=CtyString()).validate(matches)
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}")
