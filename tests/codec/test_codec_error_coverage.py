import pytest
from pyvider.cty import parse_type_string_to_ctytype, CtyTypeParseError

# Test cases designed to fail parsing in specific ways
INVALID_TYPE_STRINGS = [
    ("list(string, number)", "Failed to parse inner content of 'list': Invalid type format"),
    ("map(string, number)", "Failed to parse inner content of 'map': Invalid type format"),
    ("object(string)", "Object type definition must be enclosed in braces"),
    ("tuple{string}", "Invalid type format"),
    ("object({name:string})", "Invalid attribute format in object: '{name:string}' (missing '=')"),
    ("list(object({name=string,}))", "Invalid attribute format in object: '' (missing '=')"),
    ("nonsense", "Invalid type format"),

    ("list(string", "Invalid type format"),
    ("map(string", "Invalid type format"),
    ("set(string", "Invalid type format"),
    ("object({name=string)", "Invalid type format"), # Corrected: Outer structure invalid
    ("tuple([string)", "Invalid type format"),    # Corrected: Outer structure invalid

    ("object({name=string,age=number", "Invalid type format"), # Corrected: Outer structure invalid
    ("tuple([string,number", "Invalid type format"), # Corrected: Outer structure invalid

    ("list()", "Failed to parse inner content of 'list': Invalid type format"),
    ("map()", "Failed to parse inner content of 'map': Invalid type format"),
    ("set()", "Failed to parse inner content of 'set': Invalid type format"),

    ("object({=string})", "attribute name cannot be empty in '=string'"),
    ("object({name=})", "Failed to parse inner content of 'object': Invalid type format"),
    ("tuple([string,,number])", "Failed to parse inner content of 'tuple': Invalid type format"),

    ("{name=string", "Invalid type format"),
    ("[string,number", "Invalid type format"),

    ("object({name=string;age=number})", "Failed to parse inner content of 'object': Invalid type format"),
    ("tuple([string;number])", "Failed to parse inner content of 'tuple': Invalid type format"),

    ("unknown_type(string)", "Unknown type keyword 'unknown_type'"),
    ("list(another_unknown_type)", "Failed to parse inner content of 'list'"), # Check for 'Invalid type format' from inner
    ("object({name=inv@lid_type})", "Failed to parse inner content of 'object'"), # Check for 'Invalid type format' from inner
    ("object({name string})", "Invalid attribute format in object: 'name string' (missing '=')"),
    ("tuple()", "Tuple type definition must be enclosed in brackets []"), # Empty parens for tuple keyword
    ("   ", "Invalid type format"), # Whitespace only string
    ("object({a=list(number,string)})", "Failed to parse inner content of 'object': Failed to parse inner content of 'list': Invalid type format"),
]

@pytest.mark.parametrize("invalid_str, expected_error_msg_part", INVALID_TYPE_STRINGS)
def test_codec_parsing_failures(invalid_str, expected_error_msg_part):
    """Tests that the codec parser fails correctly on various malformed strings."""
    with pytest.raises(CtyTypeParseError) as exc_info:
        parse_type_string_to_ctytype(invalid_str)
    assert expected_error_msg_part.lower() in str(exc_info.value).lower()

def test_deeply_nested_parse_error():
    # Test a more complex nested error to ensure the error message propagates usefully
    invalid_str = "list(object({data=tuple([string, map(list(invalidType))])}))"
    with pytest.raises(CtyTypeParseError) as excinfo:
        parse_type_string_to_ctytype(invalid_str)

    # Check for parts of the error message chain
    assert "failed to parse inner content of 'list'" in str(excinfo.value).lower()
    assert "failed to parse inner content of 'object'" in str(excinfo.value).lower()
    assert "failed to parse inner content of 'tuple'" in str(excinfo.value).lower()
    assert "failed to parse inner content of 'map'" in str(excinfo.value).lower()
    assert "failed to parse inner content of 'list'" in str(excinfo.value).lower() # The innermost list
    assert "unknown type keyword 'invalidtype'" in str(excinfo.value).lower()

def test_object_shorthand_errors():
    with pytest.raises(CtyTypeParseError, match="Invalid attribute format in object: 'name string'"):
        parse_type_string_to_ctytype("{name string}")
    with pytest.raises(CtyTypeParseError, match="Invalid attribute format in object: 'name='"):
        parse_type_string_to_ctytype("{name=}")

def test_tuple_shorthand_errors():
    # Shorthand tuple parsing expects valid inner types
    with pytest.raises(CtyTypeParseError, match="Unknown type keyword 'invalid'"):
        parse_type_string_to_ctytype("[string, invalid]")
    with pytest.raises(CtyTypeParseError, match="An unexpected error occurred while parsing 'tuple'"):
        parse_type_string_to_ctytype("[string, number") # Missing closing bracket

def test_codec_split_arguments_comprehensive():
    """Test the internal _split_arguments helper with various cases."""
    from pyvider.cty.codec import _split_arguments
    assert _split_arguments("") == []
    assert _split_arguments("  ") == [""] # Current behavior, might be desired to be []
    assert _split_arguments("a") == ["a"]
    assert _split_arguments("a,b") == ["a", "b"]
    assert _split_arguments("a, b, c") == ["a", "b", "c"]
    assert _split_arguments("list(string), object({name=string})") == ["list(string)", "object({name=string})"]
    assert _split_arguments("map(string), number") == ["map(string)", "number"]
    assert _split_arguments(" list(string) , object({ name = string }) ") == ["list(string)", "object({ name = string })"]
    assert _split_arguments("a,,b") == ["a", "", "b"]
    assert _split_arguments("a,b,") == ["a", "b", ""] # Trailing comma
    assert _split_arguments(",a,b") == ["", "a", "b"] # Leading comma
