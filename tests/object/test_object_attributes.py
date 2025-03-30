#
# tests/object/test_object_attributes.py
#

"""
Tests for CtyObject type implementation.
"""

import pytest

from pyvider.cty import (
    CtyValue,
    CtyBool,
    CtyNumber,
    CtyString,
    CtyList,
    CtyMap,
    CtyObject,
)

from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyValidationError,
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
    assert isinstance(data, CtyValue)
    assert data.type == obj

    # Access attribute
    attr_value = obj.get_attribute(data.value, "title")
    
    # Verify attribute value is a CtyValue containing a CtyString type
    assert isinstance(attr_value, CtyValue)
    assert isinstance(attr_value.type, CtyString)
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
    assert isinstance(data, CtyValue)
    assert data.type == obj

    # Try to access non-existent attribute
    with pytest.raises(CtyAttributeValidationError):
        obj.get_attribute(data.value, "unknown")

@pytest.mark.asyncio
async def test_object_get_attribute_invalid_value():
    """Test attribute access fails for invalid values."""
    # Setup object type
    obj = CtyObject({
        "title": CtyString(),
        "level": CtyNumber()
    })

    # Try to access attribute on non-dict value
    with pytest.raises(CtyValidationError):
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
    with pytest.raises(CtyAttributeValidationError):
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
    with pytest.raises(CtyAttributeValidationError):
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
    with pytest.raises(CtyAttributeValidationError):
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
async def test_object_with_optional_attribute():
    """Test with_attribute method with optional flag."""
    # Setup base object
    obj = CtyObject({
        "name": CtyString()
    })
    # Add new optional attribute
    obj2 = obj.with_attribute("email", CtyString(), optional=True)
    # Verify attribute was added as optional
    assert "email" in obj2.attribute_types
    assert isinstance(obj2.attribute_types["email"], CtyString)
    assert "email" in obj2.optional_attributes
    # Original object should be unchanged
    assert "email" not in obj.attribute_types

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
    assert isinstance(value, CtyValue)
    assert value.type == person_type
    
    # Get attributes
    name = person_type.get_attribute(value.value, "name")
    age = person_type.get_attribute(value.value, "age")
    active = person_type.get_attribute(value.value, "active")
    
    # Verify attributes are CtyValues with correct types
    assert isinstance(name, CtyValue)
    assert isinstance(name.type, CtyString)
    assert name.value == "Alice"
    
    assert isinstance(age, CtyValue)
    assert isinstance(age.type, CtyNumber)
    assert age.value == 30
    
    assert isinstance(active, CtyValue)
    assert isinstance(active.type, CtyBool)
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
    assert isinstance(value, CtyValue)
    assert value.type == person_type
    
    # Try to get unknown attribute
    with pytest.raises(CtyAttributeValidationError) as excinfo:
        person_type.get_attribute(value.value, "unknown")
    
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
    with pytest.raises(CtyAttributeValidationError) as excinfo:
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
    with pytest.raises(CtyAttributeValidationError) as excinfo:
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
    with pytest.raises(CtyAttributeValidationError) as excinfo:
        new_type.with_attribute("email", CtyString())
    
    # Check error message
    error_msg = str(excinfo.value)
    assert "Attribute already exists: email" in error_msg

@pytest.mark.asyncio
async def test_get_attribute_from_cty_value():
    """Test getting attribute from CtyValue wrapper."""
    # Create object type
    obj_type = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    
    # Create validated value
    value = obj_type.validate({
        "name": "Alice",
        "age": 30
    })
    
    validated = obj_type.validate(value)
    assert isinstance(validated, CtyValue)
    assert validated.type == value

    # Get attribute using CtyValue's __getitem__
    name_attr = value["name"]
    assert name_attr.value == "Alice"

    # Access a non-existent attribute
    with pytest.raises(CtyAttributeValidationError):
        non_existent = value["non_existent"]

@pytest.mark.asyncio
async def test_object_null_attribute_access():
    """Test accessing attributes on null value."""
    # Create object type with optional attribute
    obj_type = CtyObject({
        "name": CtyString(),
        "email": CtyString()
    }, optional_attributes=frozenset(["email"]))
    
    # Create value without optional attribute
    value = obj_type.validate({
        "name": "Alice"
    })
    
    # Access the null attribute
    email_attr = value["email"]
    
    # Verify it's a null CtyValue
    assert isinstance(email_attr, CtyValue)
    assert email_attr.is_null
    assert isinstance(email_attr.type, CtyString)

@pytest.mark.asyncio
async def test_object_unknown_attribute_access():
    """Test accessing attribute on unknown value."""
    # Create object type
    obj_type = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    
    # Create unknown value
    unknown_val = CtyValue.unknown(obj_type)
    
    # Try to access attribute
    with pytest.raises(CtyAttributeValidationError) as excinfo:
        obj_type.get_attribute(unknown_val, "name")
    
    # Check error message
    assert "Cannot get attribute from unknown value" in str(excinfo.value)

@pytest.mark.asyncio
async def test_object_attribute_iteration():
    """Test iterating over object attributes."""
    # Create object type
    obj_type = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool()
    })
    
    # Test iteration
    attrs = list(obj_type)
    
    # Verify iteration returns attribute names
    assert len(attrs) == 3
    assert set(attrs) == {"name", "age", "active"}

@pytest.mark.asyncio
async def test_object_len():
    """Test getting length of object type."""
    # Create object type
    obj_type = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool()
    })
    
    # Verify length is number of attributes
    assert len(obj_type) == 3
    
    # Empty object
    empty_obj = CtyObject({})
    assert len(empty_obj) == 0

@pytest.mark.asyncio
async def test_object_getitem():
    """Test getting attribute type via __getitem__."""
    # Create object type
    obj_type = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    
    validated = obj_type.validate(obj_type)
    assert isinstance(validated, CtyValue)
    assert validated.type == obj_type

    name_type = obj_type.value["name"]

    # Verify correct type returned
    assert isinstance(name_type, CtyString)
    
    # Try with non-string key
    with pytest.raises(TypeError):
        obj_type[123]

# 🐍🏗️🧪
