#
# tests/capsule/test_cty_capsule_value.py
#

import pytest

from pyvider.cty.exceptions import ValidationError
from pyvider.cty.types.capsule import CtyCapsule
from pyvider.cty.values import CtyValue
from pyvider.cty.capsule import capsule_val


class TestObj:
    """Test class for encapsulation in capsule values."""
    def __init__(self, name):
        self.name = name
        
    def __eq__(self, other):
        if not isinstance(other, TestObj):
            return False
        return self.name == other.name


@pytest.fixture
async def capsule_type():
    """Create a capsule type for testing."""
    return CtyCapsule(
        friendly_name="test_obj",
        encapsulated_type=TestObj
    )


@pytest.fixture
async def test_obj():
    """Create a test object for encapsulation."""
    return TestObj("test_value")


class TestCtyCapsuleValue:
    """Tests for capsule value creation and access."""

    @pytest.mark.asyncio
    async def test_capsule_value_creation(self, capsule_type, test_obj):
        """Test creating a capsule value with capsule_val helper."""
        val = capsule_val(capsule_type, test_obj)
        
        # Check type and value
        assert val.type == capsule_type
        assert val.value == test_obj
        assert val.is_known
        assert not val.is_unknown
        assert not val.is_null
        
    @pytest.mark.asyncio
    async def test_capsule_value_direct_creation(self, capsule_type, test_obj):
        """Test creating a capsule value directly with CtyValue."""
        val = CtyValue(type_=capsule_type, value=test_obj)
        
        # Check type and value
        assert val.type == capsule_type
        assert val.value == test_obj
        
    @pytest.mark.asyncio
    async def test_capsule_null_value(self, capsule_type):
        """Test null capsule values."""
        null_val = capsule_val(capsule_type, None)
        
        # Check null state
        assert null_val.type == capsule_type
        assert null_val.is_null
        assert null_val.value is None
        
    @pytest.mark.asyncio
    async def test_capsule_unknown_value(self, capsule_type):
        """Test unknown capsule values."""
        unknown_val = CtyValue(type_=capsule_type, is_unknown=True)
        
        # Check unknown state
        assert unknown_val.type == capsule_type
        assert unknown_val.is_unknown
        assert not unknown_val.is_known
        
        # Value access should raise ValueError
        with pytest.raises(ValueError):
            unknown_val.value
            
    @pytest.mark.asyncio
    async def test_capsule_value_validation(self, capsule_type):
        """Test validation during capsule value creation."""
        # Wrong type
        with pytest.raises(ValidationError):
            capsule_val(capsule_type, "not_a_test_obj")
            
    @pytest.mark.asyncio
    async def test_encapsulated_value_access(self, capsule_type, test_obj):
        """Test accessing the encapsulated value."""
        val = capsule_val(capsule_type, test_obj)
        
        # Access encapsulated value
        encapsulated = val.encapsulated_value()
        assert encapsulated == test_obj
        assert encapsulated.name == "test_value"
        
    @pytest.mark.asyncio
    async def test_encapsulated_value_error_cases(self, capsule_type):
        """Test error cases when accessing encapsulated values."""
        # Null value returns None
        null_val = capsule_val(capsule_type, None)
        assert null_val.encapsulated_value() is None
        
        # Unknown value raises ValueError
        unknown_val = CtyValue(type_=capsule_type, is_unknown=True)
        with pytest.raises(ValueError):
            unknown_val.encapsulated_value()
            
    @pytest.mark.asyncio
    async def test_capsule_value_equality(self, capsule_type, test_obj):
        """Test equality comparison for capsule values."""
        val1 = capsule_val(capsule_type, test_obj)
        val2 = capsule_val(capsule_type, test_obj)
        
        # Values with same encapsulated object should be equal
        assert val1 == val2
        
        # Different encapsulated objects should not be equal
        val3 = capsule_val(capsule_type, TestObj("different"))
        assert val1 != val3
        
        # Null values of same type should be equal
        null1 = capsule_val(capsule_type, None)
        null2 = capsule_val(capsule_type, None)
        assert null1 == null2
