# pyvider-cty/src/pyvider/cty/functions/string_functions.py

from pyvider.cty import CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError

# Helper to define a CTY function signature and wrapper easily could be added later.
# For now, direct implementation.

def chomp(input_val: CtyValue) -> CtyValue:
    """
    Removes trailing newline characters from a string.
    Specifically, it removes a single trailing \n or \r\n.
    """
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val # Passthrough null/unknown

    s = input_val.value
    if s.endswith("\r\n"):
        return CtyString().validate(s[:-2])
    if s.endswith("\n"):
        return CtyString().validate(s[:-1])
    return input_val # Return original if no trailing newline

def strrev(input_val: CtyValue) -> CtyValue:
    """
    Reverses a string.
    """
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"strrev: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    return CtyString().validate(s[::-1])

def trimspace(input_val: CtyValue) -> CtyValue:
    """
    Removes leading and trailing whitespace from a string.
    Whitespace includes space, tab, newline, carriage return, form feed, vertical tab.
    """
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"trimspace: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    # Python's str.strip() handles all Unicode whitespace by default.
    return CtyString().validate(s.strip())

def indent(prefix_val: CtyValue, input_val: CtyValue) -> CtyValue:
    """
    Adds a prefix to the beginning of each line in a string.
    The final line of the string will not have the prefix added if it is empty.
    """
    if not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError(f"indent: prefix must be a string, got {prefix_val.type.ctype}")
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"indent: input must be a string, got {input_val.type.ctype}")

    if prefix_val.is_null or prefix_val.is_unknown:
        # If prefix is null/unknown, the result is effectively the original string (or its unknown/null state)
        return input_val
    if input_val.is_null or input_val.is_unknown:
        return input_val

    prefix = prefix_val.value
    s = input_val.value

    if not s: # Empty string input
        return input_val

    lines = s.splitlines(True) # Keep line endings
    indented_lines = []
    for i, line in enumerate(lines):
        if line == "\n" and i == len(lines) -1 and not s.endswith("\n"):
            # Special case for go-cty: if the string doesn't end with a newline,
            # but splitlines produced a final empty string representing the part after the last newline,
            # don't indent that "phantom" line. More simply: if the last line is empty
            # and it's not because the original string ended with a newline, don't indent it.
            # Python's s.splitlines() behavior for strings not ending in \n differs from Go's strings.Split.
            # A simpler approach for go-cty parity:
            # If the original string `s` does not end with a newline, and the last line after splitlines()
            # is effectively empty (just a newline character perhaps, or truly empty if keepends=False),
            # it should not get the prefix.
            # Let's refine based on observed go-cty behavior.
            # go-cty indent: "foo\nbar" with " " -> " foo\n bar"
            # go-cty indent: "foo\nbar\n" with " " -> " foo\n bar\n"
            # go-cty indent: "" with " " -> ""
            # go-cty indent: "\n" with " " -> " \n"
            # go-cty indent: "foo" with " " -> " foo"

            # If the last line is empty (it's just a newline from splitlines(True)
            # on a string that itself ended with a newline), it should be prefixed.
            # If the original string did NOT end with a newline, the last "line" from
            # splitlines(True) will be the content itself without a newline.
            # The logic should be: prefix every line. If the original string is empty, return empty.
            # If the original string is not empty but ends with a newline, the last "empty" line
            # (which is just the newline char) also gets prefixed.
            # This seems to be covered by simply prefixing all lines from s.splitlines(True)
            # *unless* the line itself is empty AND it's the very last line AND the original string didn't end with newline.
            # This is complex. Let's simplify: textwrap.indent in Python 3.9+ is the way.
            # For broader compatibility or direct go-cty logic:
            pass # Will handle below with simpler logic for now.


        if i == len(lines) - 1 and not line.endswith('\n') and not line:
            # If the last line is empty and does not have a newline (meaning original string didn't end with newline)
            # then don't prefix it. This matches `go-cty` behavior more closely.
            indented_lines.append(line)
        elif line: # Prefix non-empty lines, or any line that is not the special last empty one.
            indented_lines.append(prefix + line)
        else: # Empty lines (e.g. trailing newline) should be preserved if not the special case.
             indented_lines.append(line)


    # Correction based on go-cty behavior:
    # - Empty string in -> empty string out
    # - Prefix is added to each line.
    # - If the last line is empty (the string ends with a newline), that "empty" line after the newline
    #   is NOT prefixed.
    if not s:
        return CtyString().validate("")

    lines = s.split('\n')
    # If the original string ends with a newline, split() will produce an empty string at the end.
    # This empty string should not be prefixed.
    if s.endswith('\n'):
        # Process all but the last (empty) line
        indented_lines_processed = [prefix + line for line in lines[:-1]]
        # Add the last empty line (which is just the newline) back without a prefix
        result = '\n'.join(indented_lines_processed) + '\n'
    else:
        indented_lines_processed = [prefix + line for line in lines]
        result = '\n'.join(indented_lines_processed)

    return CtyString().validate(result)

def substr(input_val: CtyValue, offset_val: CtyValue, length_val: CtyValue) -> CtyValue:
    """
    Extracts a substring from a given string.
    - offset: 0-based start index. Negative values count from the end.
    - length: Number of characters to extract. If -1, extracts to the end.
    """
    from pyvider.cty.types import CtyNumber # Import here to avoid circular dependency at module level

    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"substr: input must be a string, got {input_val.type.ctype}")
    if not isinstance(offset_val.type, CtyNumber):
        raise CtyFunctionError(f"substr: offset must be a number, got {offset_val.type.ctype}")
    if not isinstance(length_val.type, CtyNumber):
        raise CtyFunctionError(f"substr: length must be a number, got {length_val.type.ctype}")

    if input_val.is_null or input_val.is_unknown or \
       offset_val.is_null or offset_val.is_unknown or \
       length_val.is_null or length_val.is_unknown:
        return CtyValue.unknown(CtyString()) # If any param is unknown/null, result is unknown string

    s = input_val.value
    offset = int(offset_val.value)
    length = int(length_val.value)

    s_len = len(s)

    if offset < 0:
        offset = s_len + offset
        if offset < 0: # Still negative after adjustment means it's out of bounds from left
            offset = 0

    if offset > s_len: # Offset is beyond the string length
        return CtyString().validate("")

    if length == -1:
        return CtyString().validate(s[offset:])

    if length < 0: # Invalid length
        raise CtyFunctionError(f"substr: length cannot be negative (unless -1 for 'to end')")

    end = offset + length
    if end > s_len:
        end = s_len

    return CtyString().validate(s[offset:end])

def trim(input_val: CtyValue, cutset_val: CtyValue) -> CtyValue:
    """
    Removes leading and trailing characters from a string that are present in the cutset.
    """
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"trim: input must be a string, got {input_val.type.ctype}")
    if not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError(f"trim: cutset must be a string, got {cutset_val.type.ctype}")

    if input_val.is_null or input_val.is_unknown:
        return input_val
    if cutset_val.is_null or cutset_val.is_unknown:
         # If cutset is null/unknown, behavior is to return original string or its unknown/null state.
         # For unknown cutset, the result of trimming is unknown.
        return CtyValue.unknown(CtyString()) if cutset_val.is_unknown else input_val


    s = input_val.value
    cutset = cutset_val.value

    return CtyString().validate(s.strip(cutset))

def title(input_val: CtyValue) -> CtyValue:
    """
    Converts the first character of each word in a string to uppercase
    and all other characters to lowercase.
    """
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    return CtyString().validate(s.title())

def trimprefix(input_val: CtyValue, prefix_val: CtyValue) -> CtyValue:
    """
    Removes the specified prefix from the beginning of a string, if present.
    """
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"trimprefix: input must be a string, got {input_val.type.ctype}")
    if not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError(f"trimprefix: prefix must be a string, got {prefix_val.type.ctype}")

    if input_val.is_null or input_val.is_unknown:
        return input_val
    if prefix_val.is_null or prefix_val.is_unknown:
        # If prefix is null/unknown, it cannot match, so return original or its unknown/null state.
        # For unknown prefix, the result of trimming is unknown.
        return CtyValue.unknown(CtyString()) if prefix_val.is_unknown else input_val

    s = input_val.value
    prefix = prefix_val.value

    # str.removeprefix is available in Python 3.9+
    if hasattr(str, "removeprefix"):
        return CtyString().validate(s.removeprefix(prefix))
    else: # Fallback for older Python versions
        if s.startswith(prefix):
            return CtyString().validate(s[len(prefix):])
        return input_val

def trimsuffix(input_val: CtyValue, suffix_val: CtyValue) -> CtyValue:
    """
    Removes the specified suffix from the end of a string, if present.
    """
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"trimsuffix: input must be a string, got {input_val.type.ctype}")
    if not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError(f"trimsuffix: suffix must be a string, got {suffix_val.type.ctype}")

    if input_val.is_null or input_val.is_unknown:
        return input_val
    if suffix_val.is_null or suffix_val.is_unknown:
        # If suffix is null/unknown, it cannot match, so return original or its unknown/null state.
        # For unknown suffix, the result of trimming is unknown.
        return CtyValue.unknown(CtyString()) if suffix_val.is_unknown else input_val

    s = input_val.value
    suffix = suffix_val.value

    # str.removesuffix is available in Python 3.9+
    if hasattr(str, "removesuffix"):
        return CtyString().validate(s.removesuffix(suffix))
    else: # Fallback for older Python versions
        if s.endswith(suffix):
            return CtyString().validate(s[:-len(suffix)])
        return input_val

def regex(pattern_val: CtyValue, input_val: CtyValue) -> CtyValue:
    """
    Checks if a regular expression pattern matches any part of a string.
    Returns a boolean CtyValue.
    """
    import re
    from pyvider.cty.types import CtyBool # Local import

    if not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError(f"regex: pattern must be a string, got {pattern_val.type.ctype}")
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"regex: input must be a string, got {input_val.type.ctype}")

    if pattern_val.is_null or pattern_val.is_unknown or \
       input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyBool())

    pattern = pattern_val.value
    s = input_val.value

    try:
        match = re.search(pattern, s)
        return CtyBool().validate(match is not None)
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}")


def regexall(pattern_val: CtyValue, input_val: CtyValue) -> CtyValue:
    """
    Finds all non-overlapping matches of the regular expression pattern in a string.
    Returns a list of strings (CtyList(CtyString)).
    """
    import re
    from pyvider.cty.types import CtyList # Local import

    if not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError(f"regexall: pattern must be a string, got {pattern_val.type.ctype}")
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"regexall: input must be a string, got {input_val.type.ctype}")

    if pattern_val.is_null or pattern_val.is_unknown or \
       input_val.is_null or input_val.is_unknown:
        # If any param is unknown/null, result is unknown list of string
        return CtyValue.unknown(CtyList(CtyString()))

    pattern = pattern_val.value
    s = input_val.value

    try:
        matches = re.findall(pattern, s)
        # Ensure matches are CtyValues of CtyString
        cty_matches = [CtyString().validate(m) for m in matches]
        return CtyList(CtyString()).validate(cty_matches)
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}")


# TODO: Register these functions with a central Cty function registry if one exists/is planned.
# For now, they are standalone Python functions that operate on CtyValues.
# A full integration would involve defining CtyFunction instances with parameter types and return types.
# Example (hypothetical):
# from pyvider.cty.functions.core import CtyFunction, FunctionParameter
#
# chomp_func = CtyFunction(
#     name="chomp",
#     description="Removes trailing newline characters.",
#     return_type=CtyString(),
#     parameters=[FunctionParameter(name="input", type=CtyString())],
#     variadic_parameter=None,
#     impl_fn=lambda input_str: chomp(input_str) # Wrapper might be needed for direct fn call
# )
# Similar for strrev and trimspace.
