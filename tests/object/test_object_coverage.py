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

    # Validate should fail and raise ValidationError
    with pytest.raises(ValidationError) as excinfo:
        person_type.validate(value) # Expecting ValidationError from nested failure

    # Check the combined error message reflects the nested failure
    error_msg = str(excinfo.value)
    
    # Verification using partial matching rather than exact string comparison
    assert "Invalid value for attribute 'address'" in error_msg
    assert "'zip'" in error_msg
    assert "Cannot convert" in error_msg or "not a valid number" in error_msg

print("wtf")
