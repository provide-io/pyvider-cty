# tests/test_cty_type_conversion.py


import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtySet,
    CtyString,
)
from pyvider.cty.conversion.format import (
    TypeCategory,
    classify_type,
    ensure_quoted_bytes,
    parse_collection_type,
    standardize_type_string,
)
from pyvider.cty.conversion.marshal import (
    marshal_type,
    unmarshal_type,
)
from pyvider.cty.exceptions import CtyConversionError

# Test data: (type_str, expected_category)
TYPE_CATEGORY_CASES = [
    # Primitive types
    ("string", TypeCategory.PRIMITIVE),
    ("number", TypeCategory.PRIMITIVE),
    ("bool", TypeCategory.PRIMITIVE),
    ("dynamic", TypeCategory.PRIMITIVE),
    ("null", TypeCategory.PRIMITIVE),
    # Collection types
    ("list(string)", TypeCategory.COLLECTION),
    ("map(number)", TypeCategory.COLLECTION),
    ("set(bool)", TypeCategory.COLLECTION),
    # Nested collection types
    ("list(list(string))", TypeCategory.COLLECTION),
    ("map(list(number))", TypeCategory.COLLECTION),
    ("set(map(bool))", TypeCategory.COLLECTION),
]

# Test data: (type_str, expected_standardized)
STANDARDIZE_CASES = [
    # Primitive types
    ("string", "string"),
    ('"string"', "string"),
    ("number", "number"),
    ('"number"', "number"),
    # Collection types
    ("list(string)", "list(string)"),
    ('"list(string)"', "list(string)"),
    ("map(number)", "map(number)"),
    # Nested types
    ("list(list(string))", "list(list(string))"),
    ('"list(list(string))"', "list(list(string))"),
    # Edge cases
    (" string ", "string"),
    ('  "string"  ', "string"),
    ("", "dynamic"),
    (None, "dynamic"),
]

# Test data: (type_str, expected_collection_type, expected_element_type)
PARSE_COLLECTION_CASES = [
    ("list(string)", "list", "string"),
    ("map(number)", "map", "number"),
    ("set(bool)", "set", "bool"),
    # Nested collection types
    ("list(list(string))", "list", "list(string)"),
    ("map(map(number))", "map", "map(number)"),
    ("set(set(bool))", "set", "set(bool)"),
]

# Test data: (type_str, expected_bytes)
BYTES_CASES = [
    ("string", b'"string"'),
    ('"string"', b'"string"'),
    ("list(string)", b'"list(string)"'),
    ('"list(string)"', b'"list(string)"'),
]

# CtyList(element_type=CtyString()))

# Test data: (type_obj, expected_bytes)
MARSHAL_CASES = [
    (CtyString(), b'"string"'),
    (CtyNumber(), b'"number"'),
    (CtyBool(), b'"bool"'),
    (CtyDynamic(), b'"dynamic"'),
    (CtyList(element_type=CtyString()), b'"list(string)"'),
    (CtyMap(key_type=CtyString(), value_type=CtyNumber()), b'"map(number)"'),
    (CtySet(element_type=CtyBool()), b'"set(bool)"'),
    (CtyList(element_type=CtyList(element_type=CtyString())), b'"list(list(string))"'),
]

# Test data: (type_bytes, expected_cty_type)
UNMARSHAL_CASES = [
    (b'"string"', CtyString()),
    (b'"number"', CtyNumber()),
    (b'"bool"', CtyBool()),
    (b'"dynamic"', CtyDynamic()),
    (b'"list(string)"', CtyList(element_type=CtyString())),
    (b'"map(number)"', CtyMap(key_type=CtyString(), value_type=CtyNumber())),
    (b'"set(bool)"', CtySet(element_type=CtyBool())),
    (b'"list(list(string))"', CtyList(element_type=CtyList(element_type=CtyString()))),
]

# Invalid types that should raise errors
INVALID_CASES = [
    b'"list("',
    b'"list(invalid)"',
    b'"unknown"',
    b'"list(list("',
]


@pytest.mark.parametrize("type_str, expected_category", TYPE_CATEGORY_CASES)
def test_classify_type(type_str, expected_category) -> None:
    """Test the classify_type function with various type strings."""
    result = classify_type(type_str)
    assert result == expected_category, (
        f"Expected {expected_category} for {type_str}, got {result}"
    )


@pytest.mark.parametrize("type_str, expected_standardized", STANDARDIZE_CASES)
def test_standardize_type_string(type_str, expected_standardized) -> None:
    """Test the standardize_type_string function with various type strings."""
    result = standardize_type_string(type_str)
    assert result == expected_standardized, (
        f"Expected {expected_standardized} for {type_str}, got {result}"
    )


@pytest.mark.parametrize(
    "type_str, expected_collection_type, expected_element_type", PARSE_COLLECTION_CASES
)
def test_parse_collection_type(
    type_str, expected_collection_type, expected_element_type
) -> None:
    """Test the parse_collection_type function with various collection types."""
    collection_type, element_type = parse_collection_type(type_str)
    assert collection_type == expected_collection_type, (
        f"Expected collection type {expected_collection_type} for {type_str}, got {collection_type}"
    )
    assert element_type == expected_element_type, (
        f"Expected element type {expected_element_type} for {type_str}, got {element_type}"
    )


@pytest.mark.parametrize("type_str, expected_bytes", BYTES_CASES)
def test_ensure_quoted_bytes(type_str, expected_bytes) -> None:
    """Test the ensure_quoted_bytes function with various type strings."""
    result = ensure_quoted_bytes(type_str)
    assert result == expected_bytes, (
        f"Expected {expected_bytes} for {type_str}, got {result}"
    )


@pytest.mark.parametrize("type_obj, expected_bytes", MARSHAL_CASES)
def test_marshal_type(type_obj, expected_bytes) -> None:
    """Test the marshal_type function with various CtyType objects."""
    result = marshal_type(type_obj)
    assert result == expected_bytes, (
        f"Expected {expected_bytes} for {type_obj}, got {result}"
    )


@pytest.mark.parametrize("type_bytes, expected_cty_type", UNMARSHAL_CASES)
def test_unmarshal_type(type_bytes, expected_cty_type) -> None:
    """Test the unmarshal_type function with various type bytes."""
    result = unmarshal_type(type_bytes)
    assert isinstance(result, expected_cty_type.__class__), (
        f"Expected {expected_cty_type.__class__.__name__}, got {result.__class__.__name__}"
    )

    # For collection types, check the element type
    if isinstance(expected_cty_type, CtyList | CtySet):
        assert isinstance(
            result.element_type, expected_cty_type.element_type.__class__
        ), (
            f"Expected element type {expected_cty_type.element_type.__class__.__name__}, got {result.element_type.__class__.__name__}"
        )

    # For nested collection types, check the nested element type
    if isinstance(expected_cty_type, CtyList) and isinstance(
        expected_cty_type.element_type, CtyList
    ):
        assert isinstance(
            result.element_type.element_type,
            expected_cty_type.element_type.element_type.__class__,
        ), "Nested element type doesn't match expected"


@pytest.mark.parametrize("invalid_type", INVALID_CASES)
def test_unmarshal_type_invalid(invalid_type) -> None:
    """Test that unmarshal_type correctly handles invalid type bytes."""
    # Either raises an exception or returns a CtyDynamic as fallback
    from pyvider.cty.types import (  # Ensure types are available for isinstance checks
        CtyDynamic,
        CtyList,
    )

    try:
        result = unmarshal_type(invalid_type)
        if invalid_type == b'"list(invalid)"':
            assert isinstance(result, CtyList), (
                f"Expected CtyList for 'list(invalid)', got {result.__class__.__name__}"
            )
            assert isinstance(result.element_type, CtyDynamic), (
                f"Expected CtyList(CtyDynamic) for 'list(invalid)', got CtyList({result.element_type.__class__.__name__})"
            )
        else:
            assert isinstance(result, CtyDynamic), (
                f"Expected CtyDynamic for invalid type {invalid_type!r}, got {result.__class__.__name__}"
            )
    except CtyConversionError:
        # This is also acceptable behavior
        pass


def test_type_conversion_roundtrip() -> None:
    """Test full roundtrip of marshal_type and unmarshal_type."""
    # Start with a complex nested type
    original = CtyList(
        element_type=CtyMap(
            key_type=CtyString(), value_type=CtyList(element_type=CtyBool())
        )
    )

    # Marshal to bytes
    marshaled = marshal_type(original)

    # Unmarshal back to CtyType
    unmarshaled = unmarshal_type(marshaled)

    # Check that we get the right type structure
    assert isinstance(unmarshaled, CtyList)
    assert isinstance(unmarshaled.element_type, CtyMap)
    assert isinstance(unmarshaled.element_type.key_type, CtyString)
    assert isinstance(unmarshaled.element_type.value_type, CtyList)
    assert isinstance(unmarshaled.element_type.value_type.element_type, CtyBool)
