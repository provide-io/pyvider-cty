#
# tests/object/test_object_complex.py
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
    assert validated is not None
    assert isinstance(validated, dict)
    
    # Check top-level attributes
    assert isinstance(validated["name"], CtyString)
    assert validated["name"].value == "web-server"
    
    assert isinstance(validated["size"], CtyString)
    assert validated["size"].value == "t3.large"
    
    # Check network block
    assert isinstance(validated["network"], dict)
    
    assert isinstance(validated["network"]["subnet"], CtyString)
    assert validated["network"]["subnet"].value == "subnet-123456"
    
    assert isinstance(validated["network"]["vpc_id"], CtyString)
    assert validated["network"]["vpc_id"].value == "vpc-123456"
    
    assert isinstance(validated["network"]["security_groups"], CtyList)
    
    # Check security_groups list elements
    security_groups = validated["network"]["security_groups"].value
    assert isinstance(security_groups, list)
    assert len(security_groups) == 2
    assert all(isinstance(item, CtyString) for item in security_groups)
    assert security_groups[0].value == "sg-1"
    assert security_groups[1].value == "sg-2"
    
    # Check disks block
    assert isinstance(validated["disks"], CtyList)
    disks = validated["disks"].value
    assert isinstance(disks, list)
    assert len(disks) == 2
    
    # Check first disk
    assert isinstance(disks[0]["size_gb"], CtyNumber)
    assert disks[0]["size_gb"].value == 100
    
    assert isinstance(disks[0]["type"], CtyString)
    assert disks[0]["type"].value == "gp3"
    
    assert isinstance(disks[0]["iops"], CtyNumber)
    assert disks[0]["iops"].value == 3000
    
    # Check second disk
    assert isinstance(disks[1]["size_gb"], CtyNumber)
    assert disks[1]["size_gb"].value == 500
    
    assert isinstance(disks[1]["type"], CtyString)
    assert disks[1]["type"].value == "io2"
    
    assert disks[1]["iops"] is None  # Optional attribute
    
    # Check tags
    assert isinstance(validated["tags"], CtyMap)
    tags = validated["tags"].value
    
    assert isinstance(tags["Environment"], CtyString)
    assert tags["Environment"].value == "production"
    
    assert isinstance(tags["Owner"], CtyString)
    assert tags["Owner"].value == "devops"

@pytest.mark.asyncio
async def test_validation_performance_large_object():
    """Test validation performance with large object."""
    # Create large object type with many attributes
    import asyncio

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
    
    # Verify each attribute is correctly wrapped in CtyString
    for i in range(attr_count):
        key = f"attr_{i}"
        assert isinstance(validated[key], CtyString)
        assert validated[key].value == f"value_{i}"
    
    # Validation should be reasonably fast (even for large objects)
    # This is just a sanity check, not a strict performance test
    duration = end_time - start_time
    assert duration < 1.0  # Should complete in under a second

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
    assert validated is not None
    assert isinstance(validated, dict)
    
    # Check top-level attributes
    assert isinstance(validated["name"], CtyString)
    assert validated["name"].value == "web-server"
    
    assert isinstance(validated["size"], CtyString)
    assert validated["size"].value == "t3.large"
    
    # Check network block
    assert isinstance(validated["network"], dict)
    
    assert isinstance(validated["network"]["subnet"], CtyString)
    assert validated["network"]["subnet"].value == "subnet-123456"
    
    assert isinstance(validated["network"]["vpc_id"], CtyString)
    assert validated["network"]["vpc_id"].value == "vpc-123456"
    
    assert isinstance(validated["network"]["security_groups"], CtyList)
    
    # Check security_groups list elements
    security_groups = validated["network"]["security_groups"].value
    assert isinstance(security_groups, list)
    assert len(security_groups) == 2
    assert all(isinstance(item, CtyString) for item in security_groups)
    assert security_groups[0].value == "sg-1"
    assert security_groups[1].value == "sg-2"
    
    # Check disks block
    assert isinstance(validated["disks"], CtyList)
    disks = validated["disks"].value
    assert isinstance(disks, list)
    assert len(disks) == 2
    
    # Check first disk
    assert isinstance(disks[0]["size_gb"], CtyNumber)
    assert disks[0]["size_gb"].value == 100
    
    assert isinstance(disks[0]["type"], CtyString)
    assert disks[0]["type"].value == "gp3"
    
    assert isinstance(disks[0]["iops"], CtyNumber)
    assert disks[0]["iops"].value == 3000
    
    # Check second disk
    assert isinstance(disks[1]["size_gb"], CtyNumber)
    assert disks[1]["size_gb"].value == 500
    
    assert isinstance(disks[1]["type"], CtyString)
    assert disks[1]["type"].value == "io2"
    
    assert disks[1]["iops"] is None  # Optional attribute
    
    # Check tags - iterate through map to find values
    assert isinstance(validated["tags"], CtyMap)
    tags = validated["tags"].value
    
    # Find the Environment key (must look for a CtyString with value "Environment")
    environment_value = None
    owner_value = None
    
    for k, v in tags.items():
        if isinstance(k, CtyString) and k.value == "Environment":
            environment_value = v
        elif isinstance(k, CtyString) and k.value == "Owner":
            owner_value = v
    
    assert environment_value is not None
    assert isinstance(environment_value, CtyString)
    assert environment_value.value == "production"
    
    assert owner_value is not None
    assert isinstance(owner_value, CtyString)
    assert owner_value.value == "devops"

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
    
    # Check result
    assert validated is not None
    assert "simple_map" in validated
    assert isinstance(validated["simple_map"], CtyMap)
    
    # Get the map value
    map_value = validated["simple_map"].value
    
    # Check map keys and values
    keys_found = []
    values_found = []
    
    for k, v in map_value.items():
        assert isinstance(k, CtyString)
        assert isinstance(v, CtyNumber)
        keys_found.append(k.value)
        values_found.append(v.value)
    
    # Check that all keys and values are present
    assert sorted(keys_found) == ["one", "three", "two"]
    assert sorted(values_found) == [1, 2, 3]
    
    # Test lookup by finding a key with specific value
    one_value = None
    for k, v in map_value.items():
        if k.value == "one":
            one_value = v
            break
            
    assert one_value is not None
    assert isinstance(one_value, CtyNumber)
    assert one_value.value == 1

# 🐍🏗️🧪
