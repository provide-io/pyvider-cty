#
# tests/capsule/test_cty_capsule_serialization.py
#

import pytest

from pyvider.cty.exceptions import CapsuleSerializationError
from pyvider.cty.types.capsule import CtyCapsule
from pyvider.cty.capsule import capsule_val
from pyvider.cty.values import CtyValue
from pyvider.cty.encoding import serialize, deserialize


class TestObj:
    """Serializable test class for capsule values."""
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
    def __eq__(self, other):
        if not isinstance(other, TestObj):
            return False
        return self.name == other.name and self.value == other.value


@pytest.fixture
async def capsule_type():
    """Create a capsule type for testing serialization."""
    return CtyCapsule(
        friendly_name="test_obj",
        encapsulated_type=TestObj
    )


@pytest.fixture
async def test_obj():
    """Create a test object for serialization."""
    return TestObj("test_name", 42)


@pytest.fixture
async def capsule_value(capsule_type, test_obj):
    """Create a capsule value for serialization tests."""
    return capsule_val(capsule_type, test_obj)


class TestCtyCapsuleJSONSerialization:
    """Tests for JSON serialization of capsule values."""

    @pytest.mark.asyncio
    async def test_json_serialization_roundtrip(self, capsule_value, test_obj):
        """Test JSON serialization and deserialization."""
        # Serialize to JSON
        serialized = await serialize(capsule_value, "json")
        assert isinstance(serialized, bytes)
        
        # Deserialize from JSON
        deserialized = await deserialize(serialized, "json")
        
        # Check result
        assert isinstance(deserialized, CtyValue)
        assert deserialized.type.friendly_name == "test_obj"
        
        # Check encapsulated value
        encapsulated = deserialized.encapsulated_value()
        assert isinstance(encapsulated, TestObj)
        assert encapsulated.name == "test_name"
        assert encapsulated.value == 42
        
    @pytest.mark.asyncio
    async def test_json_null_capsule_value(self, capsule_type):
        """Test JSON serialization of null capsule values."""
        # Create null capsule value
        null_value = capsule_val(capsule_type, None)
        
        # Serialize to JSON
        serialized = await serialize(null_value, "json")
        
        # Deserialize from JSON
        deserialized = await deserialize(serialized, "json")
        
        # Check result
        assert isinstance(deserialized, CtyValue)
        assert deserialized.is_null
        assert deserialized.type.friendly_name == "test_obj"
        
    @pytest.mark.asyncio
    async def test_json_non_serializable_value(self, capsule_type):
        """Test handling of non-serializable values in JSON."""
        class NonSerializable:
            """Class that can't be serialized to JSON."""
            def __reduce__(self):
                raise TypeError("Not serializable")
        
        # Create capsule type and value
        non_serializable_type = CtyCapsule(
            friendly_name="non_serializable", 
            encapsulated_type=NonSerializable
        )
        non_serializable_val = capsule_val(non_serializable_type, NonSerializable())
        
        # Attempt to serialize should raise an error
        with pytest.raises(CapsuleSerializationError):
            await serialize(non_serializable_val, "json")


class TestCtyCapsuleMsgPackSerialization:
    """Tests for MessagePack serialization of capsule values."""

    @pytest.mark.asyncio
    async def test_msgpack_serialization_roundtrip(self, capsule_value, test_obj):
        """Test MessagePack serialization and deserialization."""
        # Serialize to MessagePack
        serialized = await serialize(capsule_value, "msgpack")
        assert isinstance(serialized, bytes)
        
        # Deserialize from MessagePack
        deserialized = await deserialize(serialized, "msgpack")
        
        # Check result
        assert isinstance(deserialized, CtyValue)
        assert deserialized.type.friendly_name == "test_obj"
        
        # Check encapsulated value
        encapsulated = deserialized.encapsulated_value()
        assert isinstance(encapsulated, TestObj)
        assert encapsulated.name == "test_name"
        assert encapsulated.value == 42
        
    @pytest.mark.asyncio
    async def test_msgpack_null_capsule_value(self, capsule_type):
        """Test MessagePack serialization of null capsule values."""
        # Create null capsule value
        null_value = capsule_val(capsule_type, None)
        
        # Serialize to MessagePack
        serialized = await serialize(null_value, "msgpack")
        
        # Deserialize from MessagePack
        deserialized = await deserialize(serialized, "msgpack")
        
        # Check result
        assert isinstance(deserialized, CtyValue)
        assert deserialized.is_null
        assert deserialized.type.friendly_name == "test_obj"
        
    @pytest.mark.asyncio
    async def test_msgpack_unknown_capsule_value(self, capsule_type):
        """Test MessagePack serialization of unknown capsule values."""
        # Create unknown capsule value
        unknown_value = CtyValue(type_=capsule_type, is_unknown=True)
        
        # Serialize to MessagePack
        serialized = await serialize(unknown_value, "msgpack")
        
        # Deserialize from MessagePack
        deserialized = await deserialize(serialized, "msgpack")
        
        # Check result
        assert isinstance(deserialized, CtyValue)
        assert deserialized.is_unknown
        assert deserialized.type.friendly_name == "test_obj"
