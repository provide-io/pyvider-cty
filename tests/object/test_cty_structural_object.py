
# pyvider-cty/tests/

import pytest

from pyvider.cty.exceptions import AttributeValidationError, SchemaValidationError, ValidationError
from pyvider.cty import CtyBool, CtyNumber, CtyString, CtyList, CtyObject


# --------------------------------
# Test: CtyObject Basic Validation
# --------------------------------

def test_ctyobject_validate_success():
    """Test validation with valid attributes."""
    # Setup object type and sample data
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool()
    })

    valid_data = {
        "name": "John Doe",
        "age": 30,
        "active": True
    }
    
    # Execute validation
    validated = obj.validate(valid_data)
    
    # Verify results
    assert validated == {"name": "John Doe", "age": 30, "active": True}


def test_ctyobject_validate_missing_required():
    """Test validation fails when a required attribute is missing."""
    # Setup object type and incomplete data
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
    })

    incomplete_data = {"name": "Jane Doe"}
    
    # Test validation failure
    with pytest.raises(ValidationError, match="Missing required attribute: age"):
        obj.validate(incomplete_data)


def test_ctyobject_validate_null():
    """Test that 'None' input leads to 'None' output"""
    # Setup object type
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
    })
    
    # Validate null
    validated = obj.validate(None)
    
    # Verify result
    assert validated is None


# --------------------------------
# Test: CtyObject Nested Validation
# --------------------------------

def test_ctyobject_nested_validation():
    """Test validation of nested objects."""
    # Setup nested object types
    address_type = CtyObject({
        "street": CtyString(),
        "city": CtyString(),
        "postal_code": CtyString()
    })

    user_type = CtyObject({
        "name": CtyString(),
        "address": address_type,
    })

    # Setup test data
    user_data = {
        "name": "John",
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
            "postal_code": "12345"
        }
    }
    
    # Validate nested data
    validated = user_type.validate(user_data)
    
    # Verify deeply nested field
    assert validated["address"]["city"] == "Springfield"


def test_ctyobject_nested_invalid_type():
    """Test validation fails when nested attribute has wrong type."""
    # Setup nested object types
    address_type = CtyObject({
        "street": CtyString(),
        "city": CtyString()
    })

    user_type = CtyObject({
        "name": CtyString(),
        "address": address_type,
    })

    # Setup invalid data (address should be object but is string)
    invalid_data = {
        "name": "John",
        "address": "Not an object"
    }
    
    # Test validation failure
    with pytest.raises(ValidationError, match="Invalid value for attribute 'address'"):
        user_type.validate(invalid_data)


# --------------------------------
# Test: CtyObject with Optional Attributes
# --------------------------------

def test_ctyobject_optional_attributes():
    """Test validation with optional attributes."""
    # Setup object type with optional attributes
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "email": CtyString()
        },
        optional_attributes=frozenset(["email"])
    )

    # Setup data with missing optional attribute
    data = {
        "name": "John",
        "age": 30
    }
    
    # Validate data
    validated = obj.validate(data)
    
    # Verify optional attribute is None
    assert "email" in validated
    assert validated["email"] is None


# --------------------------------
# Test: CtyObject Schema Errors
# --------------------------------

def test_ctyobject_with_invalid_block_attributes():
    """Test error when block attributes don't exist in type."""
    # Setup with invalid block attribute
    with pytest.raises(AttributeValidationError, match="Unknown block attributes: invalid_block"):
        CtyObject(
            {"age": CtyNumber()},
            block_attributes=frozenset(["invalid_block"])
        )


# --------------------------------
# Test: CtyObject Attribute Access
# --------------------------------

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
    assert attr_value == "Game Title"


def test_ctyobject_get_invalid_attribute():
    """Test attribute access fails for non-existent attributes."""
    # Setup object type and data
    obj = CtyObject({
        "username": CtyString()
    })

    data = obj.validate({"username": "user1"})

    # Test access to non-existent attribute
    with pytest.raises(AttributeValidationError, match="Unknown attribute: password"):
        obj.get_attribute(data, "password")


def test_ctyobject_has_attribute():
    """Test has_attribute method."""
    # Setup object type
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })
    
    # Check existing and non-existing attributes
    assert obj.has_attribute("name") is True
    assert obj.has_attribute("email") is False


# --------------------------------
# Test: CtyObject with Blocks
# --------------------------------

def test_ctyobject_with_blocks():
    """Test object with block attributes."""
    # Setup object with block attribute
    block_type = CtyObject({
        "id": CtyString(),
        "enabled": CtyBool()
    })

    parent = CtyObject({
        "config": block_type,
        "metadata": CtyString(),
    }, block_attributes=frozenset(["config"]))

    # Setup data
    data = {
        "config": {
            "id": "123",
            "enabled": True
        },
        "metadata": "meta"
    }
    
    # Validate data
    validated = parent.validate(data)
    
    # Verify block attribute
    assert validated["config"]["enabled"] is True


def test_ctyobject_invalid_block():
    """Test validation fails when block attribute has wrong type."""
    # Setup object with block
    block_type = CtyObject({
        "id": CtyString()
    })

    parent = CtyObject({
        "config": block_type
    }, block_attributes=frozenset(["config"]))

    # Setup invalid data
    invalid_data = {
        "config": "invalid_block"  # Should be an object
    }
    
    # Test validation failure
    with pytest.raises(ValidationError, match="Invalid value for attribute 'config'"):
        parent.validate(invalid_data)


# --------------------------------
# Test: CtyObject Equality
# --------------------------------

def test_ctyobject_equality():
    """Test equality between identical object types."""
    # Setup two identical object types
    obj1 = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })

    obj2 = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })

    # Test equality
    assert obj1.equal(obj2) is True


def test_ctyobject_inequality():
    """Test inequality between different object types."""
    # Setup two different object types
    obj1 = CtyObject({"name": CtyString()})
    obj2 = CtyObject({"email": CtyString()})

    # Test inequality
    assert obj1.equal(obj2) is False


def test_ctyobject_equality_with_different_attributes():
    """Test equality with different attribute sets."""
    # Setup objects with different attributes
    obj1 = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })

    obj2 = CtyObject({
        "name": CtyString(),
        "gender": CtyString()
    })

    # Test inequality
    assert obj1.equal(obj2) is False


def test_ctyobject_equal_different_attribute_types():
    """Test equality with same attribute names but different types."""
    # Setup objects with same attribute names but different types
    obj1 = CtyObject({
        "name": CtyString(),
        "value": CtyNumber(),
    })

    obj2 = CtyObject({
        "name": CtyString(),
        "value": CtyString(),  # Different type
    })

    # Test inequality
    assert obj1.equal(obj2) is False


def test_ctyobject_equal_different_optional():
    """Test equality with different optional attributes."""
    # Setup objects with different optional attributes
    obj1 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        },
        optional_attributes=frozenset(["age"])
    )

    obj2 = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )

    # Test inequality
    assert obj1.equal(obj2) is False


# --------------------------------
# Test: CtyObject Usable As Another Object
# --------------------------------

def test_ctyobject_usable_as_same_type():
    """Test usability with same type."""
    # Setup two identical objects
    obj1 = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })

    obj2 = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })

    # Test usability
    assert obj1.usable_as(obj2) is True
    assert obj2.usable_as(obj1) is True


def test_ctyobject_usable_as_subset_attributes():
    """Test usability with subset of attributes."""
    # Setup object with more attributes and subset object
    parent = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool(),
    })

    child = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
    })

    # Test usability
    assert parent.usable_as(child) is True
    assert child.usable_as(parent) is False  # Missing 'active'


def test_ctyobject_usable_as_required_attributes():
    """Test usability with different required attributes."""
    # Setup object with more required attributes
    parent = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "email": CtyString(),
        },
        optional_attributes=frozenset(["email"])
    )

    child = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "email": CtyString(),
        },
        optional_attributes=frozenset(["age", "email"])
    )

    # Test usability
    assert parent.usable_as(child) is True
    assert child.usable_as(parent) is False  # Child doesn't require 'age'


# --------------------------------
# Test: CtyObject Type Modification Methods
# --------------------------------

def test_ctyobject_with_optional_attributes_method():
    """Test with_optional_attributes method."""
    # Setup base object
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
        "email": CtyString()
    })

    # Make attributes optional
    obj2 = obj.with_optional_attributes("age", "email")

    # Verify attributes were made optional
    assert "age" in obj2.optional_attributes
    assert "email" in obj2.optional_attributes
    assert "name" not in obj2.optional_attributes

    # Original object should be unchanged
    assert "age" not in obj.optional_attributes
    assert "email" not in obj.optional_attributes


def test_ctyobject_with_computed_attributes_method():
    """Test with_computed_attributes method."""
    # Setup base object
    obj = CtyObject({
        "name": CtyString(),
        "id": CtyString(),
        "created_at": CtyString()
    })

    # Mark attributes as computed
    obj2 = obj.with_computed_attributes("id", "created_at")

    # Verify attributes were marked as computed
    assert "id" in obj2.computed_attributes
    assert "created_at" in obj2.computed_attributes
    assert "name" not in obj2.computed_attributes

    # Original object should be unchanged
    assert "id" not in obj.computed_attributes
    assert "created_at" not in obj.computed_attributes


def test_ctyobject_with_block_attributes_method():
    """Test with_block_attributes method."""
    # Setup base object
    block_type = CtyObject({
        "id": CtyString(),
        "enabled": CtyBool()
    })

    obj = CtyObject({
        "config": block_type,
        "user": CtyString()
    })

    # Mark attribute as block
    obj2 = obj.with_block_attributes("config")

    # Verify attribute was marked as block
    assert "config" in obj2.block_attributes
    assert "user" not in obj2.block_attributes

    # Original object should be unchanged
    assert "config" not in obj.block_attributes


def test_ctyobject_with_sensitive_attributes_method():
    """Test with_sensitive_attributes method."""
    # Setup base object
    obj = CtyObject({
        "username": CtyString(),
        "password": CtyString(),
        "api_key": CtyString()
    })

    # Mark attributes as sensitive
    obj2 = obj.with_sensitive_attributes("password", "api_key")

    # Verify attributes were marked as sensitive
    assert "password" in obj2.sensitive_attributes
    assert "api_key" in obj2.sensitive_attributes
    assert "username" not in obj2.sensitive_attributes

    # Original object should be unchanged
    assert "password" not in obj.sensitive_attributes
    assert "api_key" not in obj.sensitive_attributes


def test_ctyobject_with_attribute_method():
    """Test with_attribute method."""
    # Setup base object
    obj = CtyObject({
        "name": CtyString(),
        "age": CtyNumber()
    })

    # Add new attribute
    obj2 = obj.with_attribute(
        "email", CtyString(),
        optional=True, sensitive=True
    )

    # Verify attribute was added with flags
    assert "email" in obj2.attribute_types
    assert isinstance(obj2.attribute_types["email"], CtyString)
    assert "email" in obj2.optional_attributes
    assert "email" in obj2.sensitive_attributes
    assert "email" not in obj2.computed_attributes
    assert "email" not in obj2.block_attributes

    # Original object should be unchanged
    assert "email" not in obj.attribute_types


def test_ctyobject_with_attribute_already_exists():
    """Test with_attribute fails when attribute already exists."""
    # Setup base object
    obj = CtyObject({
        "email": CtyString()
    })

    # Try to add existing attribute
    with pytest.raises(SchemaValidationError, match="Attribute already exists: email"):
        obj.with_attribute("email", CtyString())


# --------------------------------
# Test: Miscellaneous CtyObject Tests
# --------------------------------

def test_ctyobject_invalid_constructor_types():
    """Test error when attribute_types is not a dict."""
    # Pass invalid attribute_types (not a dict)
    with pytest.raises(InvalidTypeError):
        CtyObject(attribute_types="not_a_dict")


def test_ctyobject_validate_not_dict():
    """Test validation fails when value is not a dict."""
    # Setup object
    obj = CtyObject({
        "name": CtyString()
    })

    # Validate non-dict value
    with pytest.raises(ValidationError, match="Expected a dictionary"):
        obj.validate("not_a_dict")


def test_ctyobject_to_string():
    """Test string representation of object type."""
    # Setup object
    obj = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        },
        optional_attributes=frozenset(["age"])
    )

    # Get string representation
    result = str(obj)

    # Verify it contains attribute info
    assert "name: " in result
    assert "age: " in result
    assert "(optional)" in result


def test_create_object_helper():
    """Test create_object helper function."""
    # Use helper function
    obj = create_object(
        name=CtyString(),
        age=CtyNumber(),
        active=CtyBool(),
        optional=["age", "active"],
        sensitive=["active"]
    )

    # Verify attributes
    assert set(obj.attribute_types.keys()) == {"name", "age", "active"}
    assert isinstance(obj.attribute_types["name"], CtyString)
    assert isinstance(obj.attribute_types["age"], CtyNumber)
    assert isinstance(obj.attribute_types["active"], CtyBool)

    # Verify flags
    assert set(obj.optional_attributes) == {"age", "active"}
    assert set(obj.sensitive_attributes) == {"active"}
    assert len(obj.computed_attributes) == 0
    assert len(obj.block_attributes) == 0


def test_ctyobject_get_attribute_from_non_dict():
    """Test get_attribute fails when value is not a dict."""
    # Setup object
    obj = CtyObject({
        "name": CtyString()
    })

    # Try to get attribute from non-dict
    with pytest.raises(ValidationError, match="Expected a dictionary"):
        obj.get_attribute("not_a_dict", "name")


# --------------------------------
# Test: CtyObject With Extra Attributes
# --------------------------------

def test_ctyobject_validate_with_extra_attributes():
    """Test validation fails with extra attributes."""
    # Setup object
    obj = CtyObject({
        "username": CtyString(),
    })

    # Validate with extra attributes
    with pytest.raises(ValidationError, match="Unknown attributes: role"):
        obj.validate({
            "username": "admin",
            "role": "manager"
        })


# --------------------------------
# Test: Nested CtyObject Validation
# --------------------------------

def test_ctyobject_cascading_validation_error():
    """Test nested validation errors are reported properly."""
    # Setup nested objects
    inner = CtyObject({
        "age": CtyNumber()
    })

    outer = CtyObject({
        "user": inner
    })

    # Validate with nested invalid data
    with pytest.raises(ValidationError, match="Invalid value for attribute 'user'"):
        outer.validate({
            "user": {"age": "not_a_number"}
        })


def test_ctyobject_validation_performance_large_object():
    """Test validation performance with large object."""
    # Create object with many attributes
    attr_count = 100
    attrs = {}
    
    for i in range(attr_count):
        attrs[f"attr_{i}"] = CtyString()
    
    large_type = CtyObject(attribute_types=attrs)
    
    # Create large value
    value = {f"attr_{i}": f"value_{i}" for i in range(attr_count)}
    
    # Validate
    validated = large_type.validate(value)
    
    # Check validation was successful
    assert validated is not None
    assert isinstance(validated, dict)
    assert len(validated) == attr_count


# --------------------------------
# Test: Complex Nested Objects
# --------------------------------

def test_complex_nested_object():
    """Test validation of a complex nested object."""
    # Create complex nested object type
    server_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "size": CtyString(),
            "network": CtyObject(
                attribute_types={
                    "subnet": CtyString(),
                    "vpc_id": CtyString(),
                    "security_groups": CtyList(element_type=CtyString()),
                }
            ),
            "disks": CtyList(
                element_type=CtyObject(
                    attribute_types={
                        "size_gb": CtyNumber(),
                        "type": CtyString(),
                        "iops": CtyNumber(),
                    },
                    optional_attributes=frozenset(["iops"])
                )
            ),
            "tags": CtyObject(
                attribute_types={
                    "environment": CtyString(),
                    "owner": CtyString()
                },
                optional_attributes=frozenset(["owner"])
            )
        },
        optional_attributes=frozenset(["tags"]),
        block_attributes=frozenset(["network", "disks"])
    )
    
    # Create valid complex value
    value = {
        "name": "web-server",
        "size": "t3.large",
        "network": {
            "subnet": "subnet-123456",
            "vpc_id": "vpc-123456",
            "security_groups": ["sg-1", "sg-2"]
        },
        "disks": [
            {
                "size_gb": 100,
                "type": "gp3",
                "iops": 3000
            },
            {
                "size_gb": 500,
                "type": "io2"
            }
        ],
        "tags": {
            "environment": "production",
            "owner": "devops"
        }
    }
    
    # Validate
    validated = server_type.validate(value)
    
    # Check various aspects of the validated object
    assert validated["name"] == "web-server"
    assert validated["size"] == "t3.large"
    
    assert validated["network"]["subnet"] == "subnet-123456"
    assert validated["network"]["vpc_id"] == "vpc-123456"
    assert len(validated["network"]["security_groups"]) == 2
    
    assert len(validated["disks"]) == 2
    assert validated["disks"][0]["size_gb"] == 100
    assert validated["disks"][0]["iops"] == 3000
    assert validated["disks"][1]["size_gb"] == 500
    assert validated["disks"][1]["iops"] is None  # Optional
    
    assert validated["tags"]["environment"] == "production"
    assert validated["tags"]["owner"] == "devops"

