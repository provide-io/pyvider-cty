#
# tests/object/test_object_validation.py
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
async def test_validation_success():
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
        assert isinstance(validated, CtyValue)
        assert validated.type == person_type

        # Check value is a CtyValue that's known and not null
        assert not validated.is_unknown
        assert not validated.is_null

        # Check all expected attributes exist in validated.value
        assert "name" in validated.value
        assert "age" in validated.value
        assert "active" in validated.value
        
        # Check attribute types
        assert isinstance(validated.value["name"].type, CtyString)
        assert isinstance(validated.value["age"].type, CtyNumber)
        assert isinstance(validated.value["active"].type, CtyBool)
        
        # Check values
        assert validated.value["name"].value == value["name"]
        assert validated.value["age"].value == value["age"]
        assert validated.value["active"].value == value["active"]

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
    assert isinstance(result, CtyValue)
    assert result.type == obj
    
    # Check types and values
    assert isinstance(result.value["name"].type, CtyString)
    assert result.value["name"].value == "Alice"
    
    assert isinstance(result.value["age"].type, CtyNumber)
    assert result.value["age"].value == 30
    
    assert isinstance(result.value["active"].type, CtyBool)
    assert result.value["active"].value is True

@pytest.mark.asyncio
async def test_validation_invalid_object_type():
    """Test validation fails for non-dict values."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    with pytest.raises(CtyValidationError):
        obj.validate({"name": "Alice"})  # Missing required "age"

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
    assert isinstance(result, CtyValue)
    assert result.type == obj
    
    # Check attributes in value dictionary
    assert "name" in result.value
    assert "age" in result.value
    
    # Check name attribute
    assert isinstance(result.value["name"].type, CtyString)
    assert result.value["name"].value == "Alice"
    
    # Check age is null (optional attribute)
    assert result.value["age"].is_null

@pytest.mark.asyncio
async def test_validation_unknown_attribute():
    """Test validation fails for unknown attributes."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    with pytest.raises(CtyValidationError) as excinfo:
        obj.validate({
            "name": "Alice",
            "age": 30,
            "unknown": "value"
        })
    
    # Check error message mentions unknown attribute
    assert "Unknown attributes: unknown" in str(excinfo.value)

@pytest.mark.asyncio
async def test_validation_invalid_attribute_value():
    """Test validation fails for invalid attribute values."""
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    with pytest.raises(CtyValidationError) as excinfo:
        obj.validate({
            "name": "Alice",
            "age": "thirty"  # Should be a number
        })
    
    # Check error message mentions invalid value
    assert "Invalid value for attribute 'age'" in str(excinfo.value)

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
    assert isinstance(validated, CtyValue)
    assert validated.type == person_type
    assert validated.is_null

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
        with pytest.raises(CtyValidationError) as excinfo:
            person_type.validate(value)
        
        # Check error message mentions missing attribute
        error_msg = str(excinfo.value)
        assert "Missing required attribute" in error_msg

##############

# In google-pyv/pyvider-cty/tests/object/test_object_validation.py [cite: 577]

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

    # Wrong attribute types - REMOVED the case with "active": "yes"
    # Also added a truly invalid string for 'active'
    invalid_values = [
        {"name": 123, "age": 30, "active": True},         # Name should be string
        {"name": "Alice", "age": "thirty", "active": True}, # Age should be number
        # REMOVED: {"name": "Alice", "age": 30, "active": "yes"}, # "yes" IS valid for CtyBool
        {"name": "Alice", "age": 30, "active": "maybe"},    # "maybe" is NOT valid for CtyBool
        {"name": "Alice", "age": 30, "active": [True]},    # List is NOT valid for CtyBool
    ]

    # Validate each invalid value
    for value in invalid_values:
        print(f"Testing invalid value: {value}") # Added for debugging
        with pytest.raises(CtyValidationError) as excinfo:
            person_type.validate(value)

        # Check error message mentions invalid value
        error_msg = str(excinfo.value)
        print(f"  -> Received expected error: {error_msg[:100]}...") # Added for debugging
        # Error message might be about the specific attribute or a general object failure
        assert "Invalid value for attribute" in error_msg or "Object validation failed" in error_msg

    # --- Optional: Add separate assertions for cases that SHOULD pass ---
    valid_bool_inputs = [
         {"name": "Alice", "age": 30, "active": "yes"},
         {"name": "Alice", "age": 30, "active": "true"},
         {"name": "Alice", "age": 30, "active": "1"},
         {"name": "Alice", "age": 30, "active": 1},
         {"name": "Alice", "age": 30, "active": 0},
         {"name": "Alice", "age": 30, "active": "false"},
         {"name": "Alice", "age": 30, "active": "no"},
         {"name": "Alice", "age": 30, "active": "0"},
    ]
    for value in valid_bool_inputs:
         print(f"Testing valid bool value conversion: {value}")
         try:
             person_type.validate(value)
         except CtyValidationError as e:
             pytest.fail(f"Validation unexpectedly failed for {value}: {e}")
    # --- End Optional Add ---

##########


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
        with pytest.raises(CtyValidationError) as excinfo:
            person_type.validate(value)
        
        # Check error message
        error_msg = str(excinfo.value)
        assert "Expected a dictionary" in error_msg

@pytest.mark.asyncio
async def test_validate_with_already_cty_types():
    """Test validation with values that are already CtyValue instances."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )
    
    # Create CtyValue instances for attributes
    name_val = CtyValue(vtype=CtyString(), value="Alice")
    age_val = CtyValue(vtype=CtyNumber(), value=30)
    active_val = CtyValue(vtype=CtyBool(), value=True)
    
    # Create value with CtyValue instances
    value = {
        "name": name_val,
        "age": age_val,
        "active": active_val,
    }
    
    # Validate
    validated = person_type.validate(value)
    assert isinstance(validated, CtyValue)
    assert validated.type == person_type
    
    # Values should be the same instances
    assert validated.value["name"] is name_val
    assert validated.value["age"] is age_val
    assert validated.value["active"] is active_val

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
    assert validated.value["active"].is_null

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
    assert validated.value["active"].is_null

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
    assert isinstance(validated, CtyValue)
    assert validated.type == large_type
    
    # Check result
    assert len(validated.value) == 100
    
    # Check a few random attributes
    assert isinstance(validated.value["attr_0"].type, CtyString)
    assert validated.value["attr_0"].value == "value_0"
    assert isinstance(validated.value["attr_50"].type, CtyString)
    assert validated.value["attr_50"].value == "value_50"
    assert isinstance(validated.value["attr_99"].type, CtyString)
    assert validated.value["attr_99"].value == "value_99"

@pytest.mark.asyncio
async def test_validate_with_mixed_cty_types():
    """Test validation with a mix of CtyValue instances and native values."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool(),
        }
    )
    
    # Create CtyValue instances for some attributes
    name_val = CtyValue(vtype=CtyString(), value="Alice")
    active_val = CtyValue(vtype=CtyBool(), value=True)
    
    # Create value with mix of CtyValue instances and native values
    value = {
        "name": name_val,  # Already a CtyValue
        "age": 30,         # Native int
        "active": active_val,  # Already a CtyValue
    }
    
    # Validate
    validated = person_type.validate(value)
    assert isinstance(validated, CtyValue)
    assert validated.type == person_type
    
    # Check CtyValue instances are preserved
    assert validated.value["name"] is name_val
    assert validated.value["active"] is active_val
    
    # Check native value was converted to CtyValue
    assert isinstance(validated.value["age"], CtyValue)
    assert isinstance(validated.value["age"].type, CtyNumber)
    assert validated.value["age"].value == 30

@pytest.mark.asyncio
async def test_validate_error_propagation():
    """Test that validation errors from nested types are properly propagated."""
    address_type = CtyObject(attribute_types={
        "street": CtyString(),
        "city": CtyString(),
        "zip": CtyNumber(),  # Expecting a number
    })
    person_type = CtyObject(attribute_types={
        "name": CtyString(),
        "address": address_type,
    })

    # Use an invalid value for zip
    value = {
        "name": "Alice",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "not-a-valid-number",  # Should be a number
        }
    }

    # Validate should fail
    with pytest.raises(CtyValidationError) as excinfo:
        person_type.validate(value)

    # Check the error message contains context
    error_msg = str(excinfo.value)
    assert "Invalid value for attribute 'address'" in error_msg
    assert "'zip'" in error_msg
    # The exact error message might vary, so check general context
    assert "not-a-valid-number" in error_msg

# 🐍🏗️🧪
