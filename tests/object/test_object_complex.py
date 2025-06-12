#
# tests/object/test_object_complex.py
#

"""
Tests for CtyObject type implementation with complex nested structures.
"""

import pytest
import asyncio

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
async def test_complex_nested_object():
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
    assert isinstance(validated, CtyValue)
    assert validated.type == server_type

    # Check top-level attributes exist
    assert "name" in validated.value
    assert "size" in validated.value
    assert "network" in validated.value
    assert "disks" in validated.value
    assert "tags" in validated.value
    
    # Check top-level attribute values
    assert validated.value["name"].value == "web-server"
    assert validated.value["size"].value == "t3.large"
    
    # Verify top-level attribute types
    assert isinstance(validated.value["name"].type, CtyString)
    assert isinstance(validated.value["size"].type, CtyString)
    
    # Check network block
    network = validated.value["network"]
    assert isinstance(network, CtyValue)
    assert isinstance(network.type, CtyObject)
    
    # Check network attributes
    assert "subnet" in network.value
    assert "vpc_id" in network.value
    assert "security_groups" in network.value
    
    assert network.value["subnet"].value == "subnet-123456"
    assert network.value["vpc_id"].value == "vpc-123456"
    
    # Check security_groups
    security_groups = network.value["security_groups"]
    assert isinstance(security_groups, CtyValue)
    assert isinstance(security_groups.type, CtyList)
    
    # Check security_groups list elements
    assert len(security_groups.value) == 2
    assert security_groups.value[0].value == "sg-1"
    assert security_groups.value[1].value == "sg-2"
    assert all(isinstance(item.type, CtyString) for item in security_groups.value)
    
    # Check disks block
    disks = validated.value["disks"]
    assert isinstance(disks, CtyValue)
    assert isinstance(disks.type, CtyList)
    assert len(disks.value) == 2
    
    # Check first disk
    disk1 = disks.value[0]
    assert isinstance(disk1, CtyValue)
    assert isinstance(disk1.type, CtyObject)
    
    assert "size_gb" in disk1.value
    assert "type" in disk1.value
    assert "iops" in disk1.value
    
    assert disk1.value["size_gb"].value == 100
    assert disk1.value["type"].value == "gp3"
    assert disk1.value["iops"].value == 3000
    
    # Check second disk
    disk2 = disks.value[1]
    assert isinstance(disk2, CtyValue)
    assert isinstance(disk2.type, CtyObject)
    
    assert "size_gb" in disk2.value
    assert "type" in disk2.value
    assert "iops" in disk2.value
    
    assert disk2.value["size_gb"].value == 500
    assert disk2.value["type"].value == "io2"
    assert disk2.value["iops"].is_null == True  # Optional attribute is null
    
    # Check tags
    tags = validated.value["tags"]
    assert isinstance(tags, CtyValue)
    assert isinstance(tags.type, CtyMap)
    
    # Find specific keys in the map (need to iterate)
    environment_found = False
    owner_found = False
    
    for k, v in tags.value.items():
        assert isinstance(k, str) # Map keys are native Python types (str, int, etc.)
        assert isinstance(v, CtyValue)
        # k.type is not applicable directly as k is now a Python str
        assert isinstance(v.type, CtyString)
        
        if k == "Environment": # k is now a str
            environment_found = True
            assert v.value == "production"
        elif k == "Owner": # k is already a str
            owner_found = True
            assert v.value == "devops"
    
    assert environment_found, "Missing 'Environment' key in tags"
    assert owner_found, "Missing 'Owner' key in tags"

@pytest.mark.asyncio
async def test_validation_performance_large_object():
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
    assert isinstance(validated, CtyValue)
    assert validated.type == large_type
    
    end_time = asyncio.get_event_loop().time()
    
    # Check attribute count
    assert len(validated.value) == attr_count
    
    # Verify attributes are correctly typed and valued
    for i in range(attr_count):
        key = f"attr_{i}"
        assert key in validated.value
        assert isinstance(validated.value[key], CtyValue)
        assert isinstance(validated.value[key].type, CtyString)
        assert validated.value[key].value == f"value_{i}"
    
    # Validation should be reasonably fast
    duration = end_time - start_time
    assert duration < 1.0  # Should complete in under a second

@pytest.mark.asyncio
async def test_map_key_handling():
    """Test specific handling of map keys in CtyObject validation."""
    # Create object with a map attribute
    obj_type = CtyObject(
        attribute_types={
            "simple_map": CtyMap(
                key_type=CtyString(),
                value_type=CtyNumber()
            )
        }
    )
    
    # Create value
    value = {
        "simple_map": {
            "one": 1,
            "two": 2,
            "three": 3
        }
    }
    
    # Validate
    validated = obj_type.validate(value)
    assert isinstance(validated, CtyValue)
    assert validated.type == obj_type
    
    # Check simple_map attribute
    assert "simple_map" in validated.value
    simple_map = validated.value["simple_map"]
    assert isinstance(simple_map, CtyValue)
    assert isinstance(simple_map.type, CtyMap)
    
    # Check map entries
    keys_found = set()
    values_found = set()
    
    for k, v in simple_map.value.items():
        assert isinstance(k, str) # Map keys are native Python types
        assert isinstance(v, CtyValue)
        # k.type is not applicable directly as k is now a Python str
        assert isinstance(v.type, CtyNumber)
        
        keys_found.add(k) # k is now a str
        values_found.add(v.value)
    
    # Check that all keys and values are present
    assert keys_found == {"one", "two", "three"}
    assert values_found == {1, 2, 3}
    
    # Test lookup by finding a key with specific value
    one_value = None
    for k, v in simple_map.value.items():
        if k == "one": # k is now a str
            one_value = v
            break
    
    assert one_value is not None
    assert isinstance(one_value, CtyValue)
    assert isinstance(one_value.type, CtyNumber)
    assert one_value.value == 1

@pytest.mark.asyncio
async def test_null_handling():
    """Test handling of null values in complex objects."""
    # Create object type with optional attributes
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "contact": CtyObject(
                attribute_types={
                    "email": CtyString(),
                    "phone": CtyString(),
                },
                optional_attributes=frozenset(["phone"])
            ),
            "preferences": CtyObject(
                attribute_types={
                    "theme": CtyString(),
                    "notifications": CtyBool(),
                },
                optional_attributes=frozenset(["theme", "notifications"])
            )
        },
        optional_attributes=frozenset(["preferences"])
    )
    
    # Create value with missing optional attributes at different levels
    value = {
        "name": "Alice",
        "contact": {
            "email": "alice@example.com",
            # phone is missing (optional)
        },
        # preferences is missing (optional)
    }
    
    # Validate
    validated = person_type.validate(value)
    assert isinstance(validated, CtyValue)
    assert validated.type == person_type
    
    # Check name
    assert "name" in validated.value
    assert validated.value["name"].value == "Alice"
    
    # Check contact
    assert "contact" in validated.value
    contact = validated.value["contact"]
    assert isinstance(contact, CtyValue)
    assert isinstance(contact.type, CtyObject)
    
    # Check contact attributes
    assert "email" in contact.value
    assert "phone" in contact.value
    assert contact.value["email"].value == "alice@example.com"
    assert contact.value["phone"].is_null == True  # Optional attribute is null
    
    # Check preferences (should be null since it's optional and missing)
    assert "preferences" in validated.value
    preferences = validated.value["preferences"]
    assert preferences.is_null == True

@pytest.mark.asyncio
async def test_nested_validation_error_propagation():
    """Test that validation errors from nested types are properly propagated."""
    # Create nested object types
    address_type = CtyObject(
        attribute_types={
            "street": CtyString(),
            "city": CtyString(),
            "zip": CtyNumber(),  # Expecting a number for zip
        }
    )
    
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "address": address_type,
        }
    )
    
    # Create value with invalid zip (should be a number)
    value = {
        "name": "Alice",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "not-a-number",  # This will fail validation
        }
    }
    
    # Validate should fail
    with pytest.raises(CtyValidationError) as excinfo:
        person_type.validate(value)
    
    # Check that error message contains context about which attribute failed
    error_msg = str(excinfo.value)
    assert "Invalid value for attribute 'address'" in error_msg
    assert "zip" in error_msg

@pytest.mark.asyncio
async def test_attribute_access_error_handling():
    """Test error handling during attribute access."""
    # Create object type
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
        }
    )
    
    # Create and validate value
    value = {
        "name": "Alice",
        "age": 30,
    }
    validated = person_type.validate(value)
    
    # Test accessing unknown attribute
    with pytest.raises(CtyAttributeValidationError):
        person_type.get_attribute(validated.value, "unknown")
    
    # Test accessing attribute on non-object
    with pytest.raises(CtyValidationError):
        person_type.get_attribute("not an object", "name")
    
    # Test accessing attribute on null object
    null_obj = CtyValue.null(person_type)
    with pytest.raises(CtyAttributeValidationError):
        person_type.get_attribute(null_obj, "name")

# 🐍🏗️🧪
