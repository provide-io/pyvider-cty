"""
Tests for CtyObject type implementation.
"""

import pytest

from pyvider.cty.types.primitives.bool import CtyBool
from pyvider.cty.types.primitives.number import CtyNumber
from pyvider.cty.types.primitives.string import CtyString
from pyvider.cty.types.collections.list import CtyList
from pyvider.cty.types.structural.object import CtyObject
from pyvider.cty.exceptions import (
    AttributeValidationError,
    ValidationError,
)


def test_ctyobject_init_empty():
    """Test creating an empty object type."""
    obj = CtyObject()
    assert obj.attribute_types == {}
    assert obj.optional_attributes == frozenset()


def test_ctyobject_init_with_attributes():
    """Test creating an object type with attributes."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool()
    })
    assert set(obj.attribute_types.keys()) == {"name", "age", "active"}
    assert isinstance(obj.attribute_types["name"], CtyString)
    assert isinstance(obj.attribute_types["age"], CtyNumber)
    assert isinstance(obj.attribute_types["active"], CtyBool)
    assert obj.optional_attributes == frozenset()


def test_ctyobject_init_with_optional_attributes():
    """Test creating an object type with optional attributes."""
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool()
        },
        optional_attributes=frozenset(["age", "active"])
    )
    assert set(obj.attribute_types.keys()) == {"name", "age", "active"}
    assert obj.optional_attributes == frozenset(["age", "active"])


def test_ctyobject_init_invalid_attribute_type():
    """Test validation fails for invalid attribute types."""
    with pytest.raises(AttributeValidationError):
        CtyObject({
            "name": CtyString(),
            "age": "not a type"
        })


def test_ctyobject_init_invalid_optional_attribute():
    """Test validation fails for invalid optional attributes."""
    with pytest.raises(AttributeValidationError):
        CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber()
            },
            optional_attributes=frozenset(["unknown"])
        )


def test_ctyobject_validate_valid_object():
    """Test validation of a valid object."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool()
    })
    data = {
        "name": "Alice",
        "age": 30,
        "active": True
    }
    result = obj.validate(data)
    assert result == data


def test_ctyobject_validate_invalid_object_type():
    """Test validation fails for non-dict values."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    with pytest.raises(ValidationError):
        obj.validate("not an object")


def test_ctyobject_validate_missing_required_attribute():
    """Test validation fails for missing required attributes."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    with pytest.raises(ValidationError):
        obj.validate({"name": "Alice"})


def test_ctyobject_validate_with_optional_attributes():
    """Test validation with optional attributes."""
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        },
        optional_attributes=frozenset(["age"])
    )
    result = obj.validate({"name": "Alice"})
    assert result["name"] == "Alice"
    assert result["age"] is None


def test_ctyobject_validate_unknown_attribute():
    """Test validation fails for unknown attributes."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    with pytest.raises(ValidationError):
        obj.validate({
            "name": "Alice",
            "age": 30,
            "unknown": "value"
        })


def test_ctyobject_validate_invalid_attribute_value():
    """Test validation fails for invalid attribute values."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    with pytest.raises(ValidationError):
        obj.validate({
            "name": "Alice",
            "age": "thirty"  # Should be a number
        })


def test_ctyobject_get_valid_attribute():
    """Test attribute access for valid attributes."""
    # Setup object type and data
    obj = CtyObject({
        "title": CtyString(),
        "level": CtyNumber()
    })

    data = obj.validate({"title": "Game Title", "level": 5})

    # Access attribute
    attr_value = obj.get_attribute(data, "title")

    # Verify attribute value
    assert isinstance(attr_value, str)
    assert attr_value == 'Game Title'


def test_ctyobject_get_invalid_attribute():
    """Test attribute access fails for non-existent attributes."""
    # Setup object type and data
    obj = CtyObject({
        "title": CtyString(),
        "level": CtyNumber()
    })
    data = obj.validate({"title": "Game Title", "level": 5})

    # Try to access non-existent attribute
    with pytest.raises(AttributeValidationError):
        obj.get_attribute(data, "unknown")


def test_ctyobject_get_attribute_invalid_value():
    """Test attribute access fails for invalid values."""
    # Setup object type
    obj = CtyObject({
        "title": CtyString(),
        "level": CtyNumber()
    })

    # Try to access attribute on non-dict value
    with pytest.raises(ValidationError):
        obj.get_attribute("not an object", "title")


def test_ctyobject_has_attribute():
    """Test checking if an attribute exists."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    assert obj.has_attribute("name") is True
    assert obj.has_attribute("age") is True
    assert obj.has_attribute("unknown") is False


def test_ctyobject_required_attributes():
    """Test getting required attributes."""
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool()
        },
        optional_attributes=frozenset(["age", "active"])
    )
    required = obj.required_attributes()
    assert required == frozenset(["name"])


def test_ctyobject_with_optional_attributes_method():
    """Test with_optional_attributes method."""
    # Setup base object
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool()
    })
    # Mark attributes as optional
    obj2 = obj.with_optional_attributes("age", "active")
    # Verify attributes were marked as optional
    assert "age" in obj2.optional_attributes
    assert "active" in obj2.optional_attributes
    assert "name" not in obj2.optional_attributes
    # Original object should be unchanged
    assert "age" not in obj.optional_attributes
    assert "active" not in obj.optional_attributes


def test_ctyobject_with_optional_attributes_unknown():
    """Test with_optional_attributes fails for unknown attributes."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    with pytest.raises(AttributeValidationError):
        obj.with_optional_attributes("unknown")


def test_ctyobject_with_required_attributes_method():
    """Test with_required_attributes method."""
    # Setup base object
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool()
        },
        optional_attributes=frozenset(["name", "age", "active"])
    )
    # Mark attributes as required
    obj2 = obj.with_required_attributes("name", "age")
    # Verify attributes were marked as required
    assert "name" not in obj2.optional_attributes
    assert "age" not in obj2.optional_attributes
    assert "active" in obj2.optional_attributes
    # Original object should be unchanged
    assert "name" in obj.optional_attributes
    assert "age" in obj.optional_attributes


def test_ctyobject_with_required_attributes_unknown():
    """Test with_required_attributes fails for unknown attributes."""
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        },
        optional_attributes=frozenset(["age"])
    )
    with pytest.raises(AttributeValidationError):
        obj.with_required_attributes("unknown")


def test_ctyobject_with_required_attributes_already_required():
    """Test with_required_attributes fails for already required attributes."""
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        },
        optional_attributes=frozenset(["age"])
    )
    with pytest.raises(AttributeValidationError):
        obj.with_required_attributes("name")  # Already required


def test_ctyobject_with_attribute_method():
    """Test with_attribute method."""
    # Setup base object
    obj = CtyObject({
        "name": CtyString()
    })
    # Add new attribute
    obj2 = obj.with_attribute("age", CtyNumber())
    # Verify attribute was added
    assert "age" in obj2.attribute_types
    assert isinstance(obj2.attribute_types["age"], CtyNumber)
    assert "age" not in obj2.optional_attributes
    # Original object should be unchanged
    assert "age" not in obj.attribute_types


