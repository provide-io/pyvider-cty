#
# tests/object/test_object_coverage.py
#

"""
Additional tests to improve coverage for CtyObject type implementation.
"""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyNumber,
    CtyString,
    CtyList,
    CtyMap,
    CtyObject,
    CtyDynamic,
)

from pyvider.cty.exceptions import (
    AttributeValidationError,
    ValidationError,
    InvalidTypeError,
)

@pytest.mark.asyncio
async def test_object_init_invalid_attribute_types_dict():
    """Test validation fails for non-dictionary attribute_types."""
    with pytest.raises(InvalidTypeError):
        CtyObject(attribute_types="not a dict")

@pytest.mark.asyncio
async def test_object_optional_attribute_fully_missing():
    """Test behavior when an optional attribute is completely missing from input."""
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        },
        optional_attributes=frozenset(["active"])
    )
    
    # Create value without the optional attribute
    value = {
        "name": "Alice",
        "age": 30,
        # active is missing
    }
    
    # Validate
    validated = obj.validate(value)
    
    # Check that result contains all attributes
    assert "name" in validated
    assert "age" in validated
    assert "active" in validated
    
    # Check that missing optional attribute is None
    assert validated["active"] is None

@pytest.mark.asyncio
async def test_object_optional_attribute_as_none():
    """Test behavior when an optional attribute is explicitly None."""
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        },
        optional_attributes=frozenset(["active"])
    )
    
    # Create value with optional attribute set to None
    value = {
        "name": "Alice",
        "age": 30,
        "active": None,
    }
    
    # Validate
    validated = obj.validate(value)
    
    # Check that optional attribute is None
    assert validated["active"] is None

@pytest.mark.asyncio
async def test_string_representation():
    """Test string representation of CtyObject."""
    # Simple object type
    obj1 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )
    
    # Object type with optional attributes
    obj2 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        },
        optional_attributes=frozenset(["age"])
    )
    
    # Check string representations
    str1 = str(obj1)
    assert "object" in str1
    assert "name: CtyString" in str1
    assert "age: CtyNumber" in str1
    
    str2 = str(obj2)
    assert "object" in str2
    assert "name: CtyString" in str2
    assert "age: CtyNumber (optional)" in str2

@pytest.mark.asyncio
async def test_validation_with_complex_nested_types():
    """Test validation with complex nested types."""
    # Create a complex type with nested objects, lists, and maps
    address_type = CtyObject(
        attribute_types={
            "street": CtyString(),
            "city": CtyString(),
            "zip": CtyString(),
        }
    )
    
    contact_type = CtyObject(
        attribute_types={
            "type": CtyString(),
            "value": CtyString(),
        }
    )
    
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "address": address_type,
            "contacts": CtyList(element_type=contact_type),
            "metadata": CtyMap(key_type=CtyString(), value_type=CtyDynamic()),
        },
        optional_attributes=frozenset(["metadata"])
    )
    
    # Create valid data
    value = {
        "name": "Alice",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345",
        },
        "contacts": [
            {
                "type": "email",
                "value": "alice@example.com",
            },
            {
                "type": "phone",
                "value": "555-1234",
            },
        ],
        "metadata": {
            "created": "2023-01-01",
            "active": True,
            "score": 95,
        },
    }
    
    # Validate
    validated = person_type.validate(value)
    
    # Check result
    assert validated is not None
    assert isinstance(validated, dict)
    
    # Check top-level attributes
    assert isinstance(validated["name"], CtyString)
    assert validated["name"].value == "Alice"
    
    assert isinstance(validated["age"], CtyNumber)
    assert validated["age"].value == 30
    
    # Check nested address object
    address = validated["address"]
    assert isinstance(address, dict)
    assert isinstance(address["street"], CtyString)
    assert address["street"].value == "123 Main St"
    assert isinstance(address["city"], CtyString)
    assert address["city"].value == "Anytown"
    assert isinstance(address["zip"], CtyString)
    assert address["zip"].value == "12345"
    
    # Check contacts list
    contacts = validated["contacts"]
    assert isinstance(contacts, CtyList)
    contacts_list = contacts.value
    assert len(contacts_list) == 2
    
    # Check first contact
    contact1 = contacts_list[0]
    assert isinstance(contact1, dict)
    assert isinstance(contact1["type"], CtyString)
    assert contact1["type"].value == "email"
    assert isinstance(contact1["value"], CtyString)
    assert contact1["value"].value == "alice@example.com"
    
    # Check metadata map
    metadata = validated["metadata"]
    assert isinstance(metadata, CtyMap)
    
    # Find specific keys in metadata (must iterate to find by key value)
    created_value = None
    active_value = None
    score_value = None
    
    for k, v in metadata.value.items():
        if k.value == "created":
            created_value = v
        elif k.value == "active":
            active_value = v
        elif k.value == "score":
            score_value = v
    
    assert created_value is not None
    assert isinstance(created_value, CtyString)
    assert created_value.value == "2023-01-01"
    
    assert active_value is not None
    assert isinstance(active_value, CtyBool)
    assert active_value.value is True
    
    assert score_value is not None
    assert isinstance(score_value, CtyNumber)
    assert score_value.value == 95

@pytest.mark.asyncio
async def test_usable_as_complex_types():
    """Test usable_as method with complex type hierarchies."""
    # Create a common address type
    address_type = CtyObject(
        attribute_types={
            "street": CtyString(),
            "city": CtyString(),
            "zip": CtyString(),
        }
    )
    
    # Create two person types with different structures
    basic_person = CtyObject(
        attribute_types={
            "name": CtyString(),
            "address": address_type,
        }
    )
    
    detailed_person = CtyObject(
        attribute_types={
            "name": CtyString(),
            "address": address_type,
            "age": CtyNumber(),
            "email": CtyString(),
        },
        optional_attributes=frozenset(["email"])
    )
    
    # Test usability
    assert detailed_person.usable_as(basic_person) is True
    assert basic_person.usable_as(detailed_person) is False

@pytest.mark.asyncio
async def test_validate_error_propagation():
    """Test that validation errors from nested types are properly propagated."""
    # Create object type with nested object
    address_type = CtyObject(
        attribute_types={
            "street": CtyString(),
            "city": CtyString(),
            "zip": CtyNumber(),  # Intentionally using Number for zip
        }
    )
    
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "address": address_type,
        }
    )
    
    # Create value with invalid nested value
    value = {
        "name": "Alice",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345",  # String instead of number
        }
    }
    
    # Validate should fail
    with pytest.raises(ValidationError) as excinfo:
        person_type.validate(value)
    
    # Check error message
    error_msg = str(excinfo.value)
    assert "Invalid value for attribute 'address'" in error_msg

# 🐍🏗️🧪

