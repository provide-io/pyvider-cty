#
# tests/object/test_object_coverage.py
#

"""
Additional tests to improve coverage for CtyObject type implementation.
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
    CtyDynamic,
)

from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyValidationError,
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
    assert isinstance(validated, CtyValue)
    assert validated.type == obj
    
    # Check that result contains all attributes
    assert "name" in validated.value
    assert "age" in validated.value
    assert "active" in validated.value
    
    # Check that missing optional attribute is null
    assert validated["active"].is_null == True

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
    assert isinstance(validated, CtyValue)
    assert validated.type == obj
    
    # Check that optional attribute is null
    assert validated["active"].is_null == True

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
async def test_validation_with_complex_nested_types_2():
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
    assert isinstance(validated, CtyValue)
    assert validated.type == person_type
    
    # Check top-level attributes
    assert "name" in validated.value
    name_val = validated.value["name"]
    assert isinstance(name_val, CtyValue)
    assert isinstance(name_val.type, CtyString)
    assert name_val.value == "Alice"
    
    assert "age" in validated.value
    age_val = validated.value["age"]
    assert isinstance(age_val, CtyValue)
    assert isinstance(age_val.type, CtyNumber)
    assert age_val.value == 30
    
    # Check nested address object
    assert "address" in validated.value
    address_val = validated.value["address"]
    assert isinstance(address_val, CtyValue)
    assert isinstance(address_val.type, CtyObject)
    
    # Check address attributes
    assert "street" in address_val.value
    street_val = address_val.value["street"]
    assert isinstance(street_val, CtyValue)
    assert isinstance(street_val.type, CtyString)
    assert street_val.value == "123 Main St"
    
    # Verify city and zip similarly
    assert "city" in address_val.value
    city_val = address_val.value["city"]
    assert isinstance(city_val, CtyValue)
    assert isinstance(city_val.type, CtyString)
    assert city_val.value == "Anytown"
    
    assert "zip" in address_val.value
    zip_val = address_val.value["zip"]
    assert isinstance(zip_val, CtyValue)
    assert isinstance(zip_val.type, CtyString)
    assert zip_val.value == "12345"
    
    # Check contacts list
    assert "contacts" in validated.value
    contacts_val = validated.value["contacts"]
    assert isinstance(contacts_val, CtyValue)
    assert isinstance(contacts_val.type, CtyList)
    assert contacts_val.type.element_type == contact_type
    
    # Check first contact object
    assert len(contacts_val.value) == 2
    contact1 = contacts_val.value[0]
    assert isinstance(contact1, CtyValue)
    assert isinstance(contact1.type, CtyObject)
    
    # Check contact attributes
    assert "type" in contact1.value
    type_val = contact1.value["type"]
    assert isinstance(type_val, CtyValue)
    assert isinstance(type_val.type, CtyString)
    assert type_val.value == "email"
    
    assert "value" in contact1.value
    value_val = contact1.value["value"]
    assert isinstance(value_val, CtyValue)
    assert isinstance(value_val.type, CtyString)
    assert value_val.value == "alice@example.com"
    
    # Check metadata map
    assert "metadata" in validated.value
    metadata_val = validated.value["metadata"]
    assert isinstance(metadata_val, CtyValue)
    assert isinstance(metadata_val.type, CtyMap)
    
    # Track metadata keys we find
    found_created = False
    found_active = False
    found_score = False
    
    # Iterate through metadata entries
    for k, v in metadata_val.value.items():
        assert isinstance(k, str) # Map keys are native Python types
        assert isinstance(v, CtyValue)
        assert isinstance(v.type, CtyDynamic) # All values in this map are CtyDynamic

        if k == "created": # k is now a str
            found_created = True
            assert isinstance(v.value, str)
            assert v.value == "2023-01-01"
        elif k == "active": # k is now a str
            found_active = True
            assert isinstance(v.value, bool)
            assert v.value is True
        elif k == "score": # k is now a str
            found_score = True
            from decimal import Decimal # Ensure Decimal is available for isinstance check
            assert isinstance(v.value, (int, Decimal))
            assert v.value == 95
    
    # Verify we found all expected keys
    assert found_created, "Missing 'created' key in metadata"
    assert found_active, "Missing 'active' key in metadata"
    assert found_score, "Missing 'score' key in metadata"

@pytest.mark.asyncio
async def test_validation_with_complex_nested_types_1():
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
    assert isinstance(validated, CtyValue)
    assert validated.type == person_type
    
    # Check result
    assert validated is not None

    # Check top-level attributes
    assert isinstance(validated["name"].type, CtyString)
    assert validated["name"].value == "Alice"
    
    assert isinstance(validated["age"].type, CtyNumber)
    assert validated["age"].value == 30
    
    # Check nested address object
    address = validated["address"]
    assert isinstance(address, CtyValue)
    assert "street" in address.value
    assert isinstance(address["street"].type, CtyString)
    assert address["street"].value == "123 Main St"
    assert isinstance(address["city"].type, CtyString)
    assert address["city"].value == "Anytown"
    assert isinstance(address["zip"].type, CtyString)
    assert address["zip"].value == "12345"
    
    # Check contacts list
    contacts = validated["contacts"]
    assert isinstance(contacts, CtyValue)
    assert isinstance(contacts.type, CtyList)
    assert contacts.type.element_type == contact_type
    contacts_list = contacts.value
    assert len(contacts_list) == 2
    
    # Check first contact
    contact1 = contacts_list[0]
    assert isinstance(contact1, CtyValue)
    assert "type" in contact1.value
    assert isinstance(contact1["type"].type, CtyString)
    assert contact1["type"].value == "email"
    assert isinstance(contact1["value"].type, CtyString)
    assert contact1["value"].value == "alice@example.com"
    
    # Check metadata map
    metadata = validated["metadata"]
    assert isinstance(metadata, CtyValue)
    assert isinstance(metadata.type, CtyMap)
    
    # Navigate metadata map entries
    for k, v in metadata.value.items():
        if isinstance(k, CtyValue) and k.value == "created":
            assert isinstance(v.type, CtyString)
            assert v.value == "2023-01-01"
        elif isinstance(k, CtyValue) and k.value == "active":
            assert isinstance(v.type, CtyBool)
            assert v.value is True
        elif isinstance(k, CtyValue) and k.value == "score":
            assert isinstance(v.type, CtyNumber)
            assert v.value == 95

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
    address_type = CtyObject(attribute_types={
        "street": CtyString(),
        "city": CtyString(),
        "zip": CtyNumber(), # Expecting a number
    })
    person_type = CtyObject(attribute_types={
        "name": CtyString(),
        "address": address_type,
    })

    # Use an invalid value that CtyNumber.validate WILL reject
    value = {
        "name": "Alice",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "not-a-valid-number", # This will cause CtyNumber validation to fail
        }
    }

    # Validate should fail and raise CtyValidationError
    with pytest.raises(CtyValidationError) as excinfo:
        person_type.validate(value) # Expecting CtyValidationError from nested failure

    # Check the combined error message reflects the nested failure
    error_msg = str(excinfo.value)
    
    # Verification using partial matching rather than exact string comparison
    assert "Invalid value for attribute 'address'" in error_msg
    assert "'zip'" in error_msg
    assert "Cannot convert" in error_msg or "not a valid number" in error_msg
