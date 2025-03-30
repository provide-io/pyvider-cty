#
# tests/capsule/test_cty_capsule_operations.py
#

import pytest

from pyvider.cty.types.capsule import CtyCapsule
from pyvider.cty.capsule import capsule_val


class TestObj:
    """Test class for capsule operations."""
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        
    def __eq__(self, other):
        if not isinstance(other, TestObj):
            return False
        return self.name == other.name and self.value == other.value


@pytest.fixture
async def test_obj():
    """Create a test object for operations."""
    return TestObj("test_name", 42)


@pytest.fixture
async def capsule_type_with_ops():
    """Create a capsule type with various operations."""
    operations = {
        "uppercase": lambda obj: obj.name.upper(),
        "get_value": lambda obj: obj.value,
        "combine": lambda obj, suffix: f"{obj.name}_{suffix}",
        "multiply": lambda obj, factor: obj.value * factor if obj.value is not None else 0
    }
    
    return CtyCapsule(
        friendly_name="test_ops",
        encapsulated_type=TestObj,
        operations=operations
    )


class TestCtyCapsuleOperations:
    """Tests for custom operations on capsule types."""

    @pytest.mark.asyncio
    async def test_operation_access(self, capsule_type_with_ops):
        """Test accessing operations from a capsule type."""
        assert capsule_type_with_ops.has_operation("uppercase")
        assert capsule_type_with_ops.has_operation("get_value")
        assert capsule_type_with_ops.has_operation("combine")
        assert capsule_type_with_ops.has_operation("multiply")
        assert not capsule_type_with_ops.has_operation("nonexistent")
        
        # Get operations directly
        uppercase_op = capsule_type_with_ops.get_operation("uppercase")
        assert uppercase_op is not None
        
        # Nonexistent operation returns None
        assert capsule_type_with_ops.get_operation("nonexistent") is None
        
    @pytest.mark.asyncio
    async def test_operation_execution(self, capsule_type_with_ops, test_obj):
        """Test executing operations on encapsulated values."""
        # Create a capsule value
        val = capsule_val(capsule_type_with_ops, test_obj)
        
        # Execute operations
        uppercase_op = capsule_type_with_ops.get_operation("uppercase")
        get_value_op = capsule_type_with_ops.get_operation("get_value")
        combine_op = capsule_type_with_ops.get_operation("combine")
        multiply_op = capsule_type_with_ops.get_operation("multiply")
        
        # Check results
        assert uppercase_op(test_obj) == "TEST_NAME"
        assert get_value_op(test_obj) == 42
        assert combine_op(test_obj, "suffix") == "test_name_suffix"
        assert multiply_op(test_obj, 2) == 84
        
    @pytest.mark.asyncio
    async def test_operation_with_null_value(self, capsule_type_with_ops):
        """Test operations with null capsule values."""
        multiply_op = capsule_type_with_ops.get_operation("multiply")
        
        # Null object (None value) with safe operation handling
        null_obj = TestObj("null", None)
        assert multiply_op(null_obj, 5) == 0
        
    @pytest.mark.asyncio
    async def test_operations_count(self, capsule_type_with_ops):
        """Test operations count and access."""
        # Should have 4 operations
        assert len(capsule_type_with_ops.operations) == 4
        
        # Operations should be accessible by name
        for op_name in ["uppercase", "get_value", "combine", "multiply"]:
            assert op_name in capsule_type_with_ops.operations
            assert callable(capsule_type_with_ops.operations[op_name])
