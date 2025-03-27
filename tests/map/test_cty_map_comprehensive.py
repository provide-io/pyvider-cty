#
# tests/map/test_cty_map_comprehensive.py
#

import pytest
from decimal import Decimal

from pyvider.cty.exceptions import ValidationError
from pyvider.cty import (
    CtyBool,
    CtyMap,
    CtyNumber,
    CtyString,
    CtyObject,
    CtyList,
    CtyValue,
)

@pytest.mark.asyncio
async def test_map_init_validation():
    """Test validation during CtyMap initialization."""
    # Valid initialization
    valid_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    assert valid_map.key_type == CtyString()
    assert valid_map.value_type == CtyNumber()

    # Invalid key_type
    with pytest.raises(ValidationError):
        CtyMap(key_type="not_a_cty_type", value_type=CtyNumber())

    # Invalid value_type
    with pytest.raises(ValidationError):
        CtyMap(key_type=CtyString(), value_type="not_a_cty_type")

@pytest.mark.asyncio
async def test_map_validate_none():
    """Test validation with None value."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    result = map_type.validate(None)

    assert isinstance(result, CtyMap)
    assert len(result.value) == 0

@pytest.mark.asyncio
async def test_map_validate_empty_dict():
    """Test validation with empty dictionary."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    result = map_type.validate({})

    assert isinstance(result, CtyMap)
    assert len(result.value) == 0

@pytest.mark.asyncio
async def test_map_validate_non_dict():
    """Test validation with non-dictionary value."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Test with various non-dict types
    for invalid in ["string", 123, True, [1, 2, 3], (1, 2)]:
        with pytest.raises(ValidationError, match=f"Expected dict, got {type(invalid).__name__}"):
            map_type.validate(invalid)

@pytest.mark.asyncio
async def test_map_validate_valid_data():
    """Test validation with valid data."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Valid data
    data = {
        "one": 1,
        "two": 2.5,
        "three": Decimal("3.14")
    }

    result = map_type.validate(data)

    assert isinstance(result, CtyMap)
    assert len(result.value) == 3

    # Find values by iterating
    for k, v in result.value.items():
        assert isinstance(k, CtyString)
        assert isinstance(v, CtyNumber)

        if k.value == "one":
            assert v.value == 1
        elif k.value == "two":
            assert v.value == 2.5
        elif k.value == "three":
            assert v.value == Decimal("3.14")

@pytest.mark.asyncio
async def test_map_validate_invalid_key():
    """Test validation with invalid key type."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Data with invalid key type
    data = {
        "one": 1,
        2: 2,  # Invalid key type (int instead of string)
        "three": 3
    }

    with pytest.raises(ValidationError):
        map_type.validate(data)

@pytest.mark.asyncio
async def test_map_validate_invalid_value():
    """Test validation with invalid value type."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Data with invalid value type
    data = {
        "one": 1,
        "two": "not_a_number",  # Invalid value type (string instead of number)
        "three": 3
    }

    with pytest.raises(ValidationError):
        map_type.validate(data)

@pytest.mark.asyncio
async def test_map_validate_with_cty_instances():
    """Test validation with pre-created CtyType instances."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Create CtyType instances
    key1 = CtyString(value="one")
    key2 = CtyString(value="two")
    val1 = CtyNumber(value=1)
    val2 = CtyNumber(value=2)

    # Data with CtyType instances
    data = {
        key1: val1,
        key2: val2,
        "three": 3  # Mixed with raw value
    }

    result = map_type.validate(data)

    assert isinstance(result, CtyMap)
    assert len(result.value) == 3

    # Verify CtyType instances are preserved
    for k, v in result.value.items():
        assert isinstance(k, CtyString)
        assert isinstance(v, CtyNumber)

        if k.value == "one":
            assert k is key1  # Should be same instance
            assert v is val1  # Should be same instance
        elif k.value == "two":
            assert k is key2  # Should be same instance
            assert v is val2  # Should be same instance

@pytest.mark.asyncio
async def test_map_get_method():
    """Test the get() method."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Create and validate a map
    data = {"one": 1, "two": 2}
    map_val = map_type.validate(data)

    # Test get with string key
    result = map_val.get("one")
    assert result is not None
    assert isinstance(result, CtyNumber)
    assert result.value == 1

    # Test get with CtyString key
    key = CtyString(value="two")
    result = map_val.get(key)
    assert result is not None
    assert isinstance(result, CtyNumber)
    assert result.value == 2

    # Test get with missing key
    default = CtyNumber(value=999)
    result = map_val.get("missing", default)
    assert result is default

    # Test get with invalid key type (should return default)
    result = map_val.get(123, default)
    assert result is default

@pytest.mark.asyncio
async def test_map_set_method():
    """Test the set() method."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Create an empty map
    map_val = map_type.validate({})

    # Add a new key-value pair
    new_map = map_val.set("one", 1)

    # Verify the new map
    assert isinstance(new_map, CtyMap)
    assert len(new_map.value) == 1

    # Find the key-value pair
    for k, v in new_map.value.items():
        assert k.value == "one"
        assert v.value == 1

    # Update existing key
    updated_map = new_map.set("one", 100)

    # Verify the updated map
    for k, v in updated_map.value.items():
        assert k.value == "one"
        assert v.value == 100

    # Verify original map is unchanged (immutability)
    for k, v in new_map.value.items():
        assert k.value == "one"
        assert v.value == 1

    # Test setting with pre-validated CtyType values
    pre_key = CtyString(value="two")
    pre_val = CtyNumber(value=2)
    pre_map = updated_map.set(pre_key, pre_val)

    # Verify pre-validated values are used directly
    key2_found = False
    for k, v in pre_map.value.items():
        if k.value == "two":
            key2_found = True
            assert k is pre_key  # Should be same instance
            assert v is pre_val  # Should be same instance

    assert key2_found, "pre-validated key-value not found"

    # Test set with invalid value type
    with pytest.raises(ValidationError):
        updated_map.set("three", "not_a_number")  # String instead of number

@pytest.mark.asyncio
async def test_map_delete_method():
    """Test the delete() method."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Create a map with data
    data = {"one": 1, "two": 2, "three": 3}
    map_val = map_type.validate(data)

    # Delete a key
    new_map = map_val.delete("two")

    # Verify key was deleted
    assert len(new_map.value) == 2

    keys_found = []
    for k in new_map.value:
        keys_found.append(k.value)

    assert "one" in keys_found
    assert "three" in keys_found
    assert "two" not in keys_found

    # Verify original map is unchanged
    assert len(map_val.value) == 3

    # Delete a non-existent key (should not error)
    result = new_map.delete("nonexistent")
    assert len(result.value) == 2  # No change

    # Delete with pre-validated key
    key3 = CtyString(value="three")
    result = new_map.delete(key3)
    assert len(result.value) == 1

    # Delete with invalid key type (should be handled gracefully)
    result = new_map.delete(123)  # Should not change the map
    assert len(result.value) == 1

@pytest.mark.asyncio
async def test_map_equality_operators():
    """Test equality and inequality operators."""
    # Create two identical maps
    map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    map1 = map1.validate({"one": 1, "two": 2})

    map2 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    map2 = map2.validate({"one": 1, "two": 2})

    # Create a different map
    map3 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    map3 = map3.validate({"one": 1, "three": 3})

    # Test equality
    assert map1 == map2
    assert not (map1 != map2)

    # Test inequality
    assert map1 != map3
    assert not (map1 == map3)

    # Test inequality with different types
    assert map1 != "not_a_map"
    assert map1 != CtyString(value="string")

@pytest.mark.asyncio
async def test_map_iteration():
    """Test iteration over map keys."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Create a map with data
    data = {"one": 1, "two": 2, "three": 3}
    map_val = map_type.validate(data)

    # Test __iter__
    keys = set()
    for key in map_val:
        assert isinstance(key, CtyString)
        keys.add(key.value)

    assert keys == {"one", "two", "three"}

@pytest.mark.asyncio
async def test_map_string_representations():
    """Test string representation methods."""
    # Create a map type
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Test __str__
    str_repr = str(map_type)
    assert "map" in str_repr
    assert "CtyNumber" in str_repr

    # Test __repr__
    repr_str = repr(map_type)
    assert "CtyMap" in repr_str
    assert "key_type" in repr_str
    assert "value_type" in repr_str

@pytest.mark.asyncio
async def test_map_with_nested_value_types():
    """Test map with complex nested value types."""
    # Create an object type for the map value
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        }
    )

    # Create a map type with the object as its value type
    map_type = CtyMap(key_type=CtyString(), value_type=person_type)

    # Create data
    data = {
        "person1": {
            "name": "Alice",
            "age": 30
        },
        "person2": {
            "name": "Bob",
            "age": 25
        }
    }

    # Validate
    result = map_type.validate(data)

    # Verify structure
    assert isinstance(result, CtyMap)
    assert len(result.value) == 2

    # Check values
    for k, v in result.value.items():
        assert isinstance(k, CtyString)
        assert isinstance(v, dict)

        # Check nested object attributes
        assert isinstance(v["name"], CtyString)
        assert isinstance(v["age"], CtyNumber)

        if k.value == "person1":
            assert v["name"].value == "Alice"
            assert v["age"].value == 30
        elif k.value == "person2":
            assert v["name"].value == "Bob"
            assert v["age"].value == 25

@pytest.mark.asyncio
async def test_map_validation_error_details():
    """Test that validation errors provide detailed information."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Data with multiple issues
    data = {
        "one": 1,
        "two": "not_a_number",  # Invalid value
        123: 3,  # Invalid key
    }

    # Validate and catch detailed error
    with pytest.raises(ValidationError) as excinfo:
        map_type.validate(data)

    # Error message should contain details
    error_msg = str(excinfo.value)
    assert "validation failed" in error_msg

@pytest.mark.asyncio
async def test_map_equal_and_usable_as():
    """Test equal() and usable_as() methods."""
    # Create different map types
    str_str_map = CtyMap(key_type=CtyString(), value_type=CtyString())
    str_num_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    str_str_map2 = CtyMap(key_type=CtyString(), value_type=CtyString())

    # Test equal()
    assert str_str_map.equal(str_str_map2)
    assert not str_str_map.equal(str_num_map)
    assert not str_str_map.equal(CtyString())

    # Test usable_as()
    assert str_str_map.usable_as(str_str_map2)
    assert not str_str_map.usable_as(str_num_map)
    assert not str_str_map.usable_as(CtyString())
