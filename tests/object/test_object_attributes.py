#
# tests/object/test_object_attributes.py
#
"""
Tests for CtyObject type implementation.
"""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyNumber,
    CtyString,
    CtyList,
    CtyMap,
    CtyObject,
)

from pyvider.cty.exceptions import (
    AttributeValidationError,
    ValidationError,
)

@pytest.mark.asyncio
async def test_object_get_valid_attribute():
    """Test attribute access for valid attributes."""
    # Setup object type and data
    obj = CtyObject({
        "title": CtyString(),
        "level": CtyNumber()
    })

    data = obj.validate({"title": "Game Title", "level": 5})

    # Access attribute
    attr_value = obj.get_attribute(data, "title")

    # Verify attribute value is a CtyString
    assert isinstance(attr_value, CtyString)
    assert attr_value.value == 'Game Title'

@pytest.mark.asyncio
async def test_object_get_invalid_attribute():
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

@pytest.mark.asyncio
async def test_object_get_attribute_invalid_value():
    """Test attribute access fails for invalid values."""
    # Setup object type
    obj = CtyObject({
        "title": CtyString(),
        "level": CtyNumber()
    })

    # Try to access attribute on non-dict value
    with pytest.raises(ValidationError):
        obj.get_attribute("not an object", "title")

@pytest.mark.asyncio
async def test_object_has_attribute():
    """Test checking if an attribute exists."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    assert obj.has_attribute("name") is True
    assert obj.has_attribute("age") is True
    assert obj.has_attribute("unknown") is False

@pytest.mark.asyncio
async def test_has_attribute():
    """Test checking if attribute exists."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )
    
    # Check attributes
    assert person_type.has_attribute("name") is True
    assert person_type.has_attribute("age") is True
    assert person_type.has_attribute("unknown") is False

@pytest.mark.asyncio
async def test_object_required_attributes():
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

@pytest.mark.asyncio
async def test_object_with_optional_attributes_method():
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

@pytest.mark.asyncio
async def test_object_with_required_attributes_method():
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

@pytest.mark.asyncio
async def test_object_with_optional_attributes_unknown():
    """Test with_optional_attributes fails for unknown attributes."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    with pytest.raises(AttributeValidationError):
        obj.with_optional_attributes("unknown")

@pytest.mark.asyncio
async def test_object_with_required_attributes_unknown():
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

@pytest.mark.asyncio
async def test_object_with_required_attributes_already_required():
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

@pytest.mark.asyncio
async def test_object_with_attribute_method():
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

@pytest.mark.asyncio
async def test_object_with_optional_attributes():
    """Test object with optional attributes."""
    # Create object with optional attributes
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        },
        optional_attributes=frozenset(["age", "active"])
    )
    
    # Verify optional attributes
    assert len(person_type.optional_attributes) == 2
    assert "age" in person_type.optional_attributes
    assert "active" in person_type.optional_attributes
    
    # Verify required attributes
    required = person_type.required_attributes()
    assert len(required) == 1
    assert "name" in required

@pytest.mark.asyncio
async def test_get_attribute():
    """Test getting attribute from object value."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )
    
    # Create and validate value
    raw_value = {
        "name": "Alice",
        "age": 30,
        "active": True,
    }
    value = person_type.validate(raw_value)
    
    # Get attributes
    name = person_type.get_attribute(value, "name")
    age = person_type.get_attribute(value, "age")
    active = person_type.get_attribute(value, "active")
    
    # Verify attributes
    assert isinstance(name, CtyString)
    assert name.value == "Alice"
    
    assert isinstance(age, CtyNumber)
    assert age.value == 30
    
    assert isinstance(active, CtyBool)
    assert active.value is True

@pytest.mark.asyncio
async def test_get_attribute_unknown():
    """Test getting unknown attribute."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )
    
    # Create and validate value
    raw_value = {
        "name": "Alice",
        "age": 30,
    }
    value = person_type.validate(raw_value)
    
    # Try to get unknown attribute
    with pytest.raises(AttributeValidationError) as excinfo:
        person_type.get_attribute(value, "unknown")
    
    # Check error message
    error_msg = str(excinfo.value)
    assert "Unknown attribute: unknown" in error_msg

@pytest.mark.asyncio
async def test_with_optional_attributes():
    """Test adding optional attributes."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
            "email": CtyString(),
        }
    )
    
    # Add optional attributes
    new_type = person_type.with_optional_attributes("age", "active")
    
    # Verify original type is unchanged
    assert len(person_type.optional_attributes) == 0
    
    # Verify new type has optional attributes
    assert len(new_type.optional_attributes) == 2
    assert "age" in new_type.optional_attributes
    assert "active" in new_type.optional_attributes
    
    # Try to add unknown attribute
    with pytest.raises(AttributeValidationError) as excinfo:
        person_type.with_optional_attributes("unknown")
    
    # Check error message
    error_msg = str(excinfo.value)
    assert "Unknown attributes: unknown" in error_msg

@pytest.mark.asyncio
async def test_with_required_attributes():
    """Test making attributes required."""
    # Create object type with optional attributes
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
            "email": CtyString(),
        },
        optional_attributes=frozenset(["age", "active", "email"])
    )
    
    # Make some attributes required
    new_type = person_type.with_required_attributes("age", "email")
    
    # Verify original type is unchanged
    assert len(person_type.optional_attributes) == 3
    assert "age" in person_type.optional_attributes
    assert "active" in person_type.optional_attributes
    assert "email" in person_type.optional_attributes
    
    # Verify new type has updated optional attributes
    assert len(new_type.optional_attributes) == 1
    assert "active" in new_type.optional_attributes
    assert "age" not in new_type.optional_attributes
    assert "email" not in new_type.optional_attributes
    
    # Try to make already required attribute required again
    with pytest.raises(AttributeValidationError) as excinfo:
        new_type.with_required_attributes("name")
    
    # Check error message
    error_msg = str(excinfo.value)
    assert "Attributes already required: name" in error_msg

@pytest.mark.asyncio
async def test_with_attribute():
    """Test adding a new attribute."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )
    
    # Add new attribute
    new_type = person_type.with_attribute(
        "email", CtyString(),
        optional=True
    )
    
    # Verify original type is unchanged
    assert len(person_type.attribute_types) == 2
    assert "email" not in person_type.attribute_types
    
    # Verify new type has new attribute
    assert len(new_type.attribute_types) == 3
    assert "email" in new_type.attribute_types
    assert isinstance(new_type.attribute_types["email"], CtyString)
    
    # Verify attribute flags
    assert "email" in new_type.optional_attributes
    
    # Try to add existing attribute
    with pytest.raises(AttributeValidationError) as excinfo:
        new_type.with_attribute("email", CtyString())
    
    # Check error message
    error_msg = str(excinfo.value)
    assert "Attribute already exists: email" in error_msg

# 🐍🏗️🧪
