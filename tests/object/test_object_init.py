#
# tests/object/test_object_init.py
#

"""
Tests for CtyObject type implementation.
"""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyNumber,
    CtyObject,
    CtyString,
)
from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
)


@pytest.mark.asyncio
async def test_object_init_empty() -> None:
    """Test creating an empty object type."""
    obj = CtyObject()
    assert obj.attribute_types == {}
    assert obj.optional_attributes == frozenset()


@pytest.mark.asyncio
async def test_object_init_with_attributes() -> None:
    """Test creating an object type with attributes."""
    obj = CtyObject({"name": CtyString(), "age": CtyNumber(), "active": CtyBool()})
    assert set(obj.attribute_types.keys()) == {"name", "age", "active"}
    assert isinstance(obj.attribute_types["name"], CtyString)
    assert isinstance(obj.attribute_types["age"], CtyNumber)
    assert isinstance(obj.attribute_types["active"], CtyBool)
    assert obj.optional_attributes == frozenset()


@pytest.mark.asyncio
async def test_object_init_with_optional_attributes() -> None:
    """Test creating an object type with optional attributes."""
    obj = CtyObject(
        attribute_types={"name": CtyString(), "age": CtyNumber(), "active": CtyBool()},
        optional_attributes=frozenset(["age", "active"]),
    )
    assert set(obj.attribute_types.keys()) == {"name", "age", "active"}
    assert obj.optional_attributes == frozenset(["age", "active"])


@pytest.mark.asyncio
async def test_object_init_invalid_attribute_type() -> None:
    """Test validation fails for invalid attribute types."""
    with pytest.raises(CtyAttributeValidationError):
        CtyObject({"name": CtyString(), "age": "not a type"})


@pytest.mark.asyncio
async def test_object_init_invalid_optional_attribute() -> None:
    """Test validation fails for invalid optional attributes."""
    with pytest.raises(CtyAttributeValidationError):
        CtyObject(
            attribute_types={"name": CtyString(), "age": CtyNumber()},
            optional_attributes=frozenset(["unknown"]),
        )


@pytest.mark.asyncio
async def test_object_creation() -> None:
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

    # Verify required attributes
    required = person_type.required_attributes()
    assert len(required) == 3
    assert "name" in required
    assert "age" in required
    assert "active" in required


# 🐍🏗️🧪
