
# tests/cty/types/structural/test_object_integration.py

"""
Integration tests for the CtyObject type implementation.

These tests verify that CtyObject correctly handles complex object definitions,
attribute validation, optional and required attributes, and integration with
the rest of the Cty type system.
"""

import asyncio
import pytest
from decimal import Decimal

from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap
from pyvider.cty.types.structural import CtyObject
from pyvider.cty.exceptions import (
    ValidationError,
    AttributeValidationError,
    SchemaValidationError,
)


class TestCtyObjectIntegration:
    """Integration tests for CtyObject type."""
    
    @pytest.mark.asyncio
    async def test_basic_object_creation(self):
        """Test creation of a basic object type."""
        # Create a simple object type
        person_type = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
                "active": CtyBool(),
            }
        )
        
        # Verify attributes
        assert len(person_type.attribute_types) == 3
        assert isinstance(person_type.attribute_types["name"], CtyString)
        assert isinstance(person_type.attribute_types["age"], CtyNumber)
        assert isinstance(person_type.attribute_types["active"], CtyBool)
        
        # Verify attribute sets
        assert len(person_type.optional_attributes) == 0
        assert len(person_type.computed_attributes) == 0
        assert len(person_type.block_attributes) == 0
        assert len(person_type.sensitive_attributes) == 0
        
        # Verify required attributes
        required = person_type.required_attributes()
        assert len(required) == 3
        assert "name" in required
        assert "age" in required
        assert "active" in required
    
    @pytest.mark.asyncio
    async def test_object_with_optional_attributes(self):
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
    async def test_object_with_computed_attributes(self):
        """Test object with computed attributes."""
        # Create object with computed attributes
        person_type = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
                "id": CtyString(),
                "created_at": CtyString(),
            },
            computed_attributes=frozenset(["id", "created_at"])
        )
        
        # Verify computed attributes
        assert len(person_type.computed_attributes) == 2
        assert "id" in person_type.computed_attributes
        assert "created_at" in person_type.computed_attributes
        
        # Verify required attributes (computed are not required)
        required = person_type.required_attributes()
        assert len(required) == 2
        assert "name" in required
        assert "age" in required
        assert "id" not in required
        assert "created_at" not in required
    
    @pytest.mark.asyncio
    async def test_object_with_block_attributes(self):
        """Test object with block attributes."""
        # Create object with block attributes
        server_type = CtyObject(
            attribute_types={
                "name": CtyString(),
                "network": CtyObject(
                    attribute_types={
                        "subnet": CtyString(),
                        "vpc_id": CtyString(),
                    }
                ),
                "disk": CtyObject(
                    attribute_types={
                        "size_gb": CtyNumber(),
                        "type": CtyString(),
                    }
                ),
            },
            block_attributes=frozenset(["network", "disk"])
        )
        
        # Verify block attributes
        assert len(server_type.block_attributes) == 2
        assert "network" in server_type.block_attributes
        assert "disk" in server_type.block_attributes
    
    @pytest.mark.asyncio
    async def test_object_with_sensitive_attributes(self):
        """Test object with sensitive attributes."""
        # Create object with sensitive attributes
        user_type = CtyObject(
            attribute_types={
                "username": CtyString(),
                "password": CtyString(),
                "api_key": CtyString(),
            },
            sensitive_attributes=frozenset(["password", "api_key"])
        )
        
        # Verify sensitive attributes
        assert len(user_type.sensitive_attributes) == 2
        assert "password" in user_type.sensitive_attributes
        assert "api_key" in user_type.sensitive_attributes
    
    @pytest.mark.asyncio
    async def test_validation_success(self):
        """Test successful validation of object values."""
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
            
            # Check types
            assert isinstance(validated["name"], str)
            assert isinstance(validated["age"], (int, float, Decimal))
            assert isinstance(validated["active"], bool)
    
    @pytest.mark.asyncio
    async def test_validation_with_optional_attributes(self):
        """Test validation with optional attributes."""
        # Create object type with optional attributes
        person_type = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
                "active": CtyBool(),
            },
            optional_attributes=frozenset(["age", "active"])
        )
        
        # Value missing optional attributes
        value = {
            "name": "Alice",
        }
        
        # Validate
        validated = person_type.validate(value)
        assert validated is not None
        assert isinstance(validated, dict)
        assert "name" in validated
        assert validated["name"] == "Alice"
        
        # Optional attributes are present as None
        assert "age" in validated
        assert validated["age"] is None
        
        assert "active" in validated
        assert validated["active"] is None
    
    @pytest.mark.asyncio
    async def test_validation_with_null_value(self):
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
    async def test_validation_failure_missing_required(self):
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
    async def test_validation_failure_wrong_type(self):
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
    async def test_validation_failure_not_dict(self):
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
    async def test_get_attribute(self):
        """Test getting attribute from object value."""
        # Create object type
        person_type = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
                "active": CtyBool(),
            }
        )
        
        # Create value
        value = {
            "name": "Alice",
            "age": 30,
            "active": True,
        }
        
        # Get attributes
        name = person_type.get_attribute(value, "name")
        age = person_type.get_attribute(value, "age")
        active = person_type.get_attribute(value, "active")
        
        # Verify attributes
        assert name == "Alice"
        assert age == 30
        assert active is True
    
    @pytest.mark.asyncio
    async def test_get_attribute_unknown(self):
        """Test getting unknown attribute."""
        # Create object type
        person_type = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
            }
        )
        
        # Create value
        value = {
            "name": "Alice",
            "age": 30,
        }
        
        # Try to get unknown attribute
        with pytest.raises(AttributeValidationError) as excinfo:
            person_type.get_attribute(value, "unknown")
        
        # Check error message
        error_msg = str(excinfo.value)
        assert "Unknown attribute: unknown" in error_msg
    
    @pytest.mark.asyncio
    async def test_has_attribute(self):
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
    async def test_with_optional_attributes(self):
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
        with pytest.raises(SchemaValidationError) as excinfo:
            person_type.with_optional_attributes("unknown")
        
        # Check error message
        error_msg = str(excinfo.value)
        assert "Unknown attributes: unknown" in error_msg
    
    @pytest.mark.asyncio
    async def test_with_required_attributes(self):
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
        with pytest.raises(SchemaValidationError) as excinfo:
            new_type.with_required_attributes("name")
        
        # Check error message
        error_msg = str(excinfo.value)
        assert "Attributes already required: name" in error_msg
    
    @pytest.mark.asyncio
    async def test_with_computed_attributes(self):
        """Test adding computed attributes."""
        # Create object type
        person_type = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
                "id": CtyString(),
                "created_at": CtyString(),
            }
        )
        
        # Add computed attributes
        new_type = person_type.with_computed_attributes("id", "created_at")
        
        # Verify original type is unchanged
        assert len(person_type.computed_attributes) == 0
        
        # Verify new type has computed attributes
        assert len(new_type.computed_attributes) == 2
        assert "id" in new_type.computed_attributes
        assert "created_at" in new_type.computed_attributes
    
    @pytest.mark.asyncio
    async def test_with_block_attributes(self):
        """Test adding block attributes."""
        # Create object type
        server_type = CtyObject(
            attribute_types={
                "name": CtyString(),
                "network": CtyObject(
                    attribute_types={
                        "subnet": CtyString(),
                        "vpc_id": CtyString(),
                    }
                ),
                "disk": CtyObject(
                    attribute_types={
                        "size_gb": CtyNumber(),
                        "type": CtyString(),
                    }
                ),
            }
        )
        
        # Add block attributes
        new_type = server_type.with_block_attributes("network", "disk")
        
        # Verify original type is unchanged
        assert len(server_type.block_attributes) == 0
        
        # Verify new type has block attributes
        assert len(new_type.block_attributes) == 2
        assert "network" in new_type.block_attributes
        assert "disk" in new_type.block_attributes
    
    @pytest.mark.asyncio
    async def test_with_sensitive_attributes(self):
        """Test adding sensitive attributes."""
        # Create object type
        user_type = CtyObject(
            attribute_types={
                "username": CtyString(),
                "password": CtyString(),
                "api_key": CtyString(),
            }
        )
        
        # Add sensitive attributes
        new_type = user_type.with_sensitive_attributes("password", "api_key")
        
        # Verify original type is unchanged
        assert len(user_type.sensitive_attributes) == 0
        
        # Verify new type has sensitive attributes
        assert len(new_type.sensitive_attributes) == 2
        assert "password" in new_type.sensitive_attributes
        assert "api_key" in new_type.sensitive_attributes
    
    @pytest.mark.asyncio
    async def test_with_attribute(self):
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
            optional=True, sensitive=True
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
        assert "email" in new_type.sensitive_attributes
        assert "email" not in new_type.computed_attributes
        assert "email" not in new_type.block_attributes
        
        # Try to add existing attribute
        with pytest.raises(SchemaValidationError) as excinfo:
            new_type.with_attribute("email", CtyString())
        
        # Check error message
        error_msg = str(excinfo.value)
        assert "Attribute already exists: email" in error_msg
    
    @pytest.mark.asyncio
    async def test_equal_same_type(self):
        """Test equality with same type."""
        # Create two identical object types
        type1 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
            }
        )
        
        type2 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
            }
        )
        
        # Check equality
        assert type1.equal(type2) is True
        assert type2.equal(type1) is True
    
    @pytest.mark.asyncio
    async def test_equal_different_attributes(self):
        """Test equality with different attributes."""
        # Create two object types with different attributes
        type1 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
            }
        )
        
        type2 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "active": CtyBool(),
            }
        )
        
        # Check equality
        assert type1.equal(type2) is False
        assert type2.equal(type1) is False
    
    @pytest.mark.asyncio
    async def test_equal_different_attribute_types(self):
        """Test equality with different attribute types."""
        # Create two object types with same attribute names but different types
        type1 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "value": CtyNumber(),
            }
        )
        
        type2 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "value": CtyString(),  # Different type
            }
        )
        
        # Check equality
        assert type1.equal(type2) is False
        assert type2.equal(type1) is False
    
    @pytest.mark.asyncio
    async def test_equal_different_optional(self):
        """Test equality with different optional attributes."""
        # Create two object types with different optional attributes
        type1 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
            },
            optional_attributes=frozenset(["age"])
        )
        
        type2 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
            }
        )
        
        # Check equality
        assert type1.equal(type2) is False
        assert type2.equal(type1) is False
    
    @pytest.mark.asyncio
    async def test_usable_as_same_type(self):
        """Test usability with same type."""
        # Create two identical object types
        type1 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
            }
        )
        
        type2 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
            }
        )
        
        # Check usability
        assert type1.usable_as(type2) is True
        assert type2.usable_as(type1) is True
    
    @pytest.mark.asyncio
    async def test_usable_as_subset_attributes(self):
        """Test usability with subset of attributes."""
        # Create object type with more attributes
        type1 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
                "active": CtyBool(),
            }
        )
        
        # Create object type with subset of attributes
        type2 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
            }
        )
        
        # Check usability
        assert type1.usable_as(type2) is True  # More attributes can be used as fewer
        assert type2.usable_as(type1) is False  # Fewer attributes cannot be used as more
    
    @pytest.mark.asyncio
    async def test_usable_as_compatible_types(self):
        """Test usability with compatible attribute types."""
        # This will be implemented when we have type conversions
        # For now, types must be exactly equal to be compatible
        pass
    
    @pytest.mark.asyncio
    async def test_usable_as_required_attributes(self):
        """Test usability with different required attributes."""
        # Create type with more required attributes
        type1 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
                "email": CtyString(),
            },
            optional_attributes=frozenset(["email"])
        )
        
        # Create type with fewer required attributes
        type2 = CtyObject(
            attribute_types={
                "name": CtyString(),
                "age": CtyNumber(),
                "email": CtyString(),
            },
            optional_attributes=frozenset(["age", "email"])
        )
        
        # Check usability
        assert type1.usable_as(type2) is True  # More required can be used as fewer required
        assert type2.usable_as(type1) is False  # Fewer required cannot be used as more required
    
    @pytest.mark.asyncio
    async def test_create_object_helper(self):
        """Test the create_object helper function."""
        from pyvider.cty.types.structural.object import create_object
        
        # Create object using helper
        person_type = create_object(
            name=CtyString(),
            age=CtyNumber(),
            active=CtyBool(),
            optional=["age", "active"],
            sensitive=["active"]
        )
        
        # Verify attributes
        assert len(person_type.attribute_types) == 3
        assert isinstance(person_type.attribute_types["name"], CtyString)
        assert isinstance(person_type.attribute_types["age"], CtyNumber)
        assert isinstance(person_type.attribute_types["active"], CtyBool)
        
        # Verify optional attributes
        assert len(person_type.optional_attributes) == 2
        assert "age" in person_type.optional_attributes
        assert "active" in person_type.optional_attributes
        
        # Verify sensitive attributes
        assert len(person_type.sensitive_attributes) == 1
        assert "active" in person_type.sensitive_attributes
    
    @pytest.mark.asyncio
    async def test_complex_nested_object(self):
        """Test complex nested object type."""
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
                    },
                    optional_attributes=frozenset(["security_groups"])
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
                "tags": CtyMap(
                    key_type=CtyString(),
                    value_type=CtyString()
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
                "Environment": "production",
                "Owner": "devops"
            }
        }
        
        # Validate
        validated = server_type.validate(value)
        assert validated is not None
        assert isinstance(validated, dict)
        
        # Check top-level attributes
        assert validated["name"] == "web-server"
        assert validated["size"] == "t3.large"
        
        # Check network block
        assert isinstance(validated["network"], dict)
        assert validated["network"]["subnet"] == "subnet-123456"
        assert validated["network"]["vpc_id"] == "vpc-123456"
        assert validated["network"]["security_groups"] == ["sg-1", "sg-2"]
        
        # Check disks block
        assert isinstance(validated["disks"], list)
        assert len(validated["disks"]) == 2
        
        assert validated["disks"][0]["size_gb"] == 100
        assert validated["disks"][0]["type"] == "gp3"
        assert validated["disks"][0]["iops"] == 3000
        
        assert validated["disks"][1]["size_gb"] == 500
        assert validated["disks"][1]["type"] == "io2"
        assert validated["disks"][1]["iops"] is None  # Optional attribute
        
        # Check tags
        assert isinstance(validated["tags"], dict)
        assert validated["tags"]["Environment"] == "production"
        assert validated["tags"]["Owner"] == "devops"
    
    @pytest.mark.asyncio
    async def test_validation_performance_large_object(self):
        """Test validation performance with large object."""
        # Create large object type with many attributes
        attr_count = 100
        attrs = {}
        
        for i in range(attr_count):
            attrs[f"attr_{i}"] = CtyString()
        
        large_type = CtyObject(attribute_types=attrs)
        
        # Create large value
        value = {f"attr_{i}": f"value_{i}" for i in range(attr_count)}
        
        # Measure validation time
        start_time = asyncio.get_event_loop().time()
        validated = large_type.validate(value)
        end_time = asyncio.get_event_loop().time()
        
        # Check validation was successful
        assert validated is not None
        assert isinstance(validated, dict)
        assert len(validated) == attr_count
        
        # Validation should be reasonably fast (even for large objects)
        # This is just a sanity check, not a strict performance test
        duration = end_time - start_time
        assert duration < 1.0  # Should complete in under a second