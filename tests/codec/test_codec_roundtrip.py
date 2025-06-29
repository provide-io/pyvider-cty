# pyvider-cty/tests/codec/test_codec_roundtrip.py
"""
Provides comprehensive round-trip tests for the CTY type codec.
Ensures that parsing a type string and re-serializing it results in an
equivalent representation, guaranteeing stability and correctness.
"""

import pytest

from pyvider.cty import (
    CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber,
    CtyObject, CtySet, CtyString, CtyTuple, CtyType,
    CtyTypeParseError, parse_type_string_to_ctytype
)

# A comprehensive list of type strings to test, from simple to complex.
# The "expected" string is a canonicalized version that the __str__ method produces.
# This tests both parsing flexibility and serialization consistency.
TEST_CASES = [
    # Primitives
    ("string", "string"),
    ("number", "number"),
    ("bool", "bool"),
    ("dynamic", "dynamic"),
    ("  string  ", "string"), # Whitespace trimming

    # Simple Collections
    ("list(string)", "list(string)"),
    ("set(number)", "set(number)"),
    ("map(bool)", "map(bool)"),
    (" list( dynamic ) ", "list(dynamic)"), # Whitespace

    # Nested Collections
    ("list(list(string))", "list(list(string))"),
    ("map(set(number))", "map(set(number))"),
    ("list(map(bool))", "list(map(bool))"),

    # Simple Tuple (FIXED canonical representation)
    ("tuple([])", "tuple([])"), # Empty tuple
    ("tuple([string])", "tuple([string])"),
    ("tuple([string, number, bool])", "tuple([string, number, bool])"),
    (" tuple( [ string, list(number) ] ) ", "tuple([string, list(number)])"),

    # Simple Object
    ("object({})", "object({})"), # Empty object
    ("object({name=string})", "object({name=string})"),
    # Test attribute order canonicalization (sorted alphabetically)
    ("object({age=number, name=string})", "object({age=number, name=string})"),
    ("object({name=string, age=number})", "object({age=number, name=string})"),
    (" object( { enabled = bool, id = string } ) ", "object({enabled=bool, id=string})"),

    # Complex Nested Structures
    (
        "object({users=list(object({name=string, roles=list(string)}))})",
        "object({users=list(object({name=string, roles=list(string)}))})"
    ),
    (
        "map(tuple([string, number]))",
        "map(tuple([string, number]))"
    ),
    (
        "list(object({cpu_utilization=number,memory_usage=number,disk_io=list(number)}))",
        "list(object({cpu_utilization=number, disk_io=list(number), memory_usage=number}))"
    ),
]

@pytest.mark.parametrize("input_str, canonical_str", TEST_CASES)
def test_type_codec_roundtrip(input_str: str, canonical_str: str):
    """
    Tests that parsing and then re-serializing a type string is stable and correct.

    Args:
        input_str: The initial type string to parse.
        canonical_str: The expected canonical string representation after parsing.
    """
    # 1. First Parse: Parse the initial input string.
    try:
        first_parsed_type = parse_type_string_to_ctytype(input_str)
    except CtyTypeParseError as e:
        pytest.fail(f"First parse failed for input '{input_str}': {e}")

    # 2. First Serialization: Convert the parsed type object back to a string.
    #    This should produce the canonical representation.
    first_serialized_str = str(first_parsed_type)
    assert first_serialized_str == canonical_str

    # 3. Second Parse: Parse the canonical string representation.
    #    This ensures that our own output is valid input.
    try:
        second_parsed_type = parse_type_string_to_ctytype(first_serialized_str)
    except CtyTypeParseError as e:
        pytest.fail(f"Second parse failed for canonical string '{first_serialized_str}': {e}")

    # 4. Final Validation:
    #    a. The two parsed CtyType objects must be equal.
    assert first_parsed_type.equal(second_parsed_type), \
        f"Parsed types should be equal, but were not.\n  - First: {first_parsed_type!r}\n  - Second: {second_parsed_type!r}"

    #    b. The string representation of the second parsed object should still be the canonical form.
    second_serialized_str = str(second_parsed_type)
    assert second_serialized_str == canonical_str, "Serialization should be stable and idempotent."


# Test cases for expected parsing errors
INVALID_TEST_CASES = [
    "list)",          # Missing opening parenthesis
    "list(string",    # Missing closing parenthesis
    "object({name})", # Missing equals and type for attribute
    "object(name=string)", # Missing braces
    "tuple{string}",  # Wrong brackets for tuple
    "map(string, number)", # Map only takes one argument (value type)
    "nonsense",       # Not a valid keyword
    "list(object({name=string,}))", # Trailing comma in object
]

@pytest.mark.parametrize("invalid_str", INVALID_TEST_CASES)
def test_type_codec_invalid_strings(invalid_str: str):
    """
    Tests that the parser correctly raises CtyTypeParseError for invalid syntax.
    """
    with pytest.raises(CtyTypeParseError):
        parse_type_string_to_ctytype(invalid_str)
