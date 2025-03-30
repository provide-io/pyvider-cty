#
# tests/capsule/test_cty_capsule_type.py
#

import pytest

from pyvider.cty.exceptions import ValidationError
from pyvider.cty.types.capsule import CtyCapsule


class TestObj:
    """Test class for encapsulation in capsule types."""
    def __init__(self, name):
        self.name = name
        
    def __eq__(self, other):
        if not isinstance(other, TestObj):
            return False
        return self.name == other.name


@pytest.fixture
async def capsule_type_basic():
    """Create a basic capsule type for testing."""
    return CtyCapsule(
        friendly_name="test_obj",
        encapsulated_type=TestObj
    )


@pytest.fixture
async def capsule_type_with_ops():
    """Create a capsule type with operations for testing."""
    def uppercase_op(value):
        return value.name.upper()
        
    return CtyCapsule(
        friendly_name="test_ops",
        encapsulated_type=TestObj,
        operations={"uppercase": uppercase_op}
    )


class TestCtyCapsuleType:
    """Tests for CtyCapsule type creation and properties."""

    @pytest.mark.asyncio
    async def test_capsule_type_creation(self, capsule_type_basic):
        """Test creating a basic capsule type."""
        assert capsule_type_basic.friendly_name == "test_obj"
        assert capsule_type_basic.encapsulated_type == TestObj
        assert len(capsule_type_basic.operations) == 0
        
    @pytest.mark.asyncio
    async def test_capsule_type_with_operations(self, capsule_type_with_ops):
        """Test creating a capsule type with operations."""
        assert capsule_type_with_ops.friendly_name == "test_ops"
        assert capsule_type_with_ops.encapsulated_type == TestObj
        assert "uppercase" in capsule_type_with_ops.operations
        
    @pytest.mark.asyncio
    async def test_capsule_type_validation_errors(self):
        """Test validation during capsule type creation."""
        # Empty friendly name
        with pytest.raises(ValidationError):
            CtyCapsule(friendly_name="", encapsulated_type=TestObj)
            
        # None encapsulated type
        with pytest.raises(ValidationError):
            CtyCapsule(friendly_name="test", encapsulated_type=None)
            
        # Invalid operation
        with pytest.raises(ValidationError):
            CtyCapsule(
                friendly_name="test",
                encapsulated_type=TestObj,
                operations={"invalid": "not_callable"}
            )
    
    @pytest.mark.asyncio
    async def test_capsule_type_equality(self, capsule_type_basic):
        """Test that capsule types compare by identity."""
        # Same instance equals itself
        assert capsule_type_basic.equal(capsule_type_basic)
        
        # Different instance with same params is NOT equal
        other_type = CtyCapsule(
            friendly_name="test_obj",
            encapsulated_type=TestObj
        )
        assert not capsule_type_basic.equal(other_type)
        
    @pytest.mark.asyncio
    async def test_capsule_type_registry(self, capsule_type_basic):
        """Test the capsule type registry."""
        # Should be able to retrieve the registered type
        retrieved = CtyCapsule.get_registered_type("test_obj")
        assert retrieved is capsule_type_basic
        
        # Non-existent type returns None
        assert CtyCapsule
