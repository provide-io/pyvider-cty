#
# tests/object/test_object_validation.py
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
async def test_validation_success_1():
    """Test successful validation of object values."""
    from decimal import Decimal

    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )
    
    # Valid values
    valid_values = [
        {
            "name": "Alice",
            "age": 30,
            "active": True,
        },
        {
            "name": "Bob",
            "age": Decimal("25.5"),
            "active": False,
        },
        {
            "name": "",
            "age": 0,
            "active": False,
        },
    ]
    
    # Validate each value
    for value in valid_values:
        validated = person_type.validate(value)
        assert validated is not None
        assert isinstance(validated, dict)
        assert "name" in validated
        assert "age" in validated
        assert "active" in validated
        
        # Check types and values
        assert isinstance(validated["name"], CtyString)
        assert validated["name"].value == value["name"]
        
        assert isinstance(validated["age"], CtyNumber)
        assert validated["age"].value == value["age"]
        
        assert isinstance(validated["active"], CtyBool)
        assert validated["active"].value == value["active"]

@pytest.mark.asyncio
async def test_validation_success_2():
    """Test successful validation of object values."""
    from decimal import Decimal

    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )
    
    # Valid values
    valid_values = [
        {
            "name": "Alice",
            "age": 30,
            "active": True,
        },
        {
            "name": "Bob",
            "age": Decimal("25.5"),
            "active": False,
        },
        {
            "name": "",
            "age": 0,
            "active": False,
        },
    ]
    
    # Validate each value
    for value in valid_values:
        validated = person_type.validate(value)
        assert validated is not None
        assert isinstance(validated, dict)
        assert "name" in validated
        assert "age" in validated
        assert "active" in validated
        
        # Check types (should be CtyType instances)
        assert isinstance(validated["name"], CtyString)
        assert isinstance(validated["age"], CtyNumber)
        assert isinstance(validated["active"], CtyBool)
        
        # Check values
        assert validated["name"].value == value["name"]
        assert validated["age"].value == value["age"]
        assert validated["active"].value == value["active"]

@pytest.mark.asyncio
async def test_validation_valid_object():
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
    
    # Check that result is a dict
    assert isinstance(result, dict)
    
    # Check types and values
    assert isinstance(result["name"], CtyString)
    assert result["name"].value == "Alice"
    
    assert isinstance(result["age"], CtyNumber)
    assert result["age"].value == 30
    
    assert isinstance(result["active"], CtyBool)
    assert result["active"].value is True

@pytest.mark.asyncio
async def test_validation_invalid_object_type():
    """Test validation fails for non-dict values."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    with pytest.raises(ValidationError):
        obj.validate({"name": "Alice"})

@pytest.mark.asyncio
async def test_validation_with_optional_attributes():
    """Test validation with optional attributes."""
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        },
        optional_attributes=frozenset(["age"])
    )
    result = obj.validate({"name": "Alice"})
    
    # Check that result is a dict
    assert isinstance(result, dict)
    
    # Check name attribute
    assert isinstance(result["name"], CtyString)
    assert result["name"].value == "Alice"
    
    # Check age is None (optional attribute)
    assert result["age"] is None

@pytest.mark.asyncio
async def test_validation_unknown_attribute():
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

@pytest.mark.asyncio
async def test_validation_invalid_attribute_value():
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

@pytest.mark.asyncio
async def test_validation_with_null_value():
    """Test validation with null value."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )
    
    # Validate null value
    validated = person_type.validate(None)
    assert validated is None

@pytest.mark.asyncio
async def test_validation_failure_missing_required():
    """Test validation failure with missing required attributes."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )
    
    # Missing required attribute
    invalid_values = [
        {},  # Missing all attributes
        {"name": "Alice"},  # Missing age, active
        {"age": 30, "active": True},  # Missing name
    ]
    
    # Validate each invalid value
    for value in invalid_values:
        with pytest.raises(ValidationError) as excinfo:
            person_type.validate(value)
        
        # Check error message mentions missing attribute
        error_msg = str(excinfo.value)
        assert "Missing required attribute" in error_msg

@pytest.mark.asyncio
async def test_validation_failure_wrong_type():
    """Test validation failure with wrong attribute types."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )
    
    # Wrong attribute types
    invalid_values = [
        {"name": 123, "age": 30, "active": True},  # Name should be string
        {"name": "Alice", "age": "thirty", "active": True},  # Age should be number
        {"name": "Alice", "age": 30, "active": "yes"},  # Active should be bool
    ]
    
    # Validate each invalid value
    for value in invalid_values:
        with pytest.raises(ValidationError) as excinfo:
            person_type.validate(value)
        
        # Check error message mentions invalid value
        error_msg = str(excinfo.value)
        assert "Invalid value for attribute" in error_msg

@pytest.mark.asyncio
async def test_validation_failure_not_dict():
    """Test validation failure with non-dictionary value."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )
    
    # Invalid values (not dictionaries)
    invalid_values = [
        "not a dict",
        123,
        True,
        ["name", "age"],
    ]
    
    # Validate each invalid value
    for value in invalid_values:
        with pytest.raises(ValidationError) as excinfo:
            person_type.validate(value)
        
        # Check error message
        error_msg = str(excinfo.value)
        assert "Expected a dictionary" in error_msg

@pytest.mark.asyncio
async def test_validate_with_already_cty_types():
    """Test validation with values that are already CtyType instances."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )
    
    # Create values that are already CtyType instances
    value = {
        "name": CtyString(value="Alice"),
        "age": CtyNumber(value=30),
        "active": CtyBool(value=True),
    }
    
    # Validate
    validated = person_type.validate(value)
    
    # Check result
    assert validated is not None
    assert isinstance(validated, dict)
    
    # Values should be the same instances
    assert validated["name"] is value["name"]
    assert validated["age"] is value["age"]
    assert validated["active"] is value["active"]

@pytest.mark.asyncio
async def test_get_attribute_with_non_dict():
    """Test get_attribute with non-dictionary value."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )
    
    # Try to get attribute from non-dictionary value
    with pytest.raises(ValidationError) as excinfo:
        person_type.get_attribute("not a dict", "name")
    
    # Check error message
    error_msg = str(excinfo.value)
    assert "Expected a dictionary" in error_msg

@pytest.mark.asyncio
async def test_object_with_nested_optional_attrs():
    """Test validation with nested objects that have optional attributes."""
    # Create nested object type with optional attributes
    address_type = CtyObject(
        attribute_types={
            "street": CtyString(),
            "city": CtyString(),
            "zip": CtyString(),
            "country": CtyString(),
        },
        optional_attributes=frozenset(["country"])
    )
    
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "address": address_type,
        }
    )
    
    # Valid value with missing optional attribute in nested object
    value = {
        "name": "Alice",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345",
            # country is missing but optional
        }
    }
    
    # Validate
    validated = person_type.validate(value)
    
    # Check result
    assert validated is not None
    assert isinstance(validated, dict)
    assert "name" in validated
    assert "address" in validated
    
    # Check nested object
    address = validated["address"]
    assert isinstance(address, dict)
    assert "street" in address
    assert "city" in address
    assert "zip" in address
    assert "country" in address  # Should exist but be None
    assert address["country"] is None

@pytest.mark.asyncio
async def test_validate_large_object():
    """Test validation with a very large object."""
    # Create object type with many attributes
    attrs = {}
    for i in range(100):  # 100 attributes
        attrs[f"attr_{i}"] = CtyString()
    
    large_type = CtyObject(attribute_types=attrs)
    
    # Create large value
    value = {f"attr_{i}": f"value_{i}" for i in range(100)}
    
    # Validate
    validated = large_type.validate(value)
    
    # Check result
    assert validated is not None
    assert isinstance(validated, dict)
    assert len(validated) == 100
    
    # Check a few random attributes
    assert isinstance(validated["attr_0"], CtyString)
    assert validated["attr_0"].value == "value_0"
    assert isinstance(validated["attr_50"], CtyString)
    assert validated["attr_50"].value == "value_50"
    assert isinstance(validated["attr_99"], CtyString)
    assert validated["attr_99"].value == "value_99"

@pytest.mark.asyncio
async def test_validate_with_mixed_cty_types():
    """Test validation with a mix of CtyType instances and native values."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )
    
    # Create value with mix of CtyType instances and native values
    value = {
        "name": CtyString(value="Alice"),  # Already a CtyString
        "age": 30,  # Native int
        "active": CtyBool(value=True),  # Already a CtyBool
    }
    
    # Validate
    validated = person_type.validate(value)
    
    # Check result
    assert validated is not None
    assert isinstance(validated, dict)
    
    # Check types and values
    assert isinstance(validated["name"], CtyString)
    assert validated["name"].value == "Alice"
    assert validated["name"] is value["name"]  # Should be same instance
    
    assert isinstance(validated["age"], CtyNumber)
    assert validated["age"].value == 30
    
    assert isinstance(validated["active"], CtyBool)
    assert validated["active"].value is True
    assert validated["active"] is value["active"]  # Should be same instance


# 🐍🏗️🧪
