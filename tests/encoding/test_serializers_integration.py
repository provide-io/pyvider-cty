#
# tests/encoding/json/test_serializers_integration.py
#

"""
Integration tests for Cty serialization.

This test suite comprehensively verifies the functionality of both
JSON and MessagePack serializers, ensuring they can correctly handle
all Cty types and special value states in a variety of scenarios.
"""

import pytest
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyObject, CtyTuple, CtyDynamic
from pyvider.cty.values import CtyValue

from pyvider.cty.encoding import (
    serialize,
    deserialize,
    serialize_with_type,
    deserialize_with_type,
    marshal,
    unmarshal,
    JsonSerializer,
    MsgpackSerializer,
)


# Test fixtures for common test data
@pytest.fixture
def primitive_values():
    """Fixture providing primitive Cty values for testing."""
    return [
        CtyValue(CtyString(), "hello world"),
        CtyValue(CtyString(), ""),  # Empty string
        CtyValue(CtyString(), "Special chars: ñáéíóú"),  # Unicode
        CtyValue(CtyString(), "Symbols: !@#$%^&*()"),  # Symbols
        CtyValue(CtyNumber(), 42),
        CtyValue(CtyNumber(), -42),
        CtyValue(CtyNumber(), 3.14159),
        CtyValue(CtyNumber(), Decimal("123456789.987654321")),  # High precision
        CtyValue(CtyNumber(), 0),  # Zero
        CtyValue(CtyBool(), True),
        CtyValue(CtyBool(), False),
    ]


@pytest.fixture
def collection_values():
    """Fixture providing collection Cty values for testing."""
    string_type = CtyString()
    number_type = CtyNumber()
    bool_type = CtyBool()
    
    # List values
    string_list_type = CtyList(element_type=string_type)
    string_list_value = [
        CtyValue(string_type, "one"),
        CtyValue(string_type, "two"),
        CtyValue(string_type, "three"),
    ]
    
    # Map values
    string_number_map_type = CtyMap(key_type=string_type, value_type=number_type)
    string_number_map_value = {
        CtyValue(string_type, "one"): CtyValue(number_type, 1),
        CtyValue(string_type, "two"): CtyValue(number_type, 2),
        CtyValue(string_type, "three"): CtyValue(number_type, 3),
    }
    
    # Set values
    bool_set_type = CtySet(element_type=bool_type)
    bool_set_value = {
        CtyValue(bool_type, True),
        CtyValue(bool_type, False),
    }
    
    # Empty collections
    empty_list_type = CtyList(element_type=string_type)
    empty_map_type = CtyMap(key_type=string_type, value_type=number_type)
    empty_set_type = CtySet(element_type=bool_type)
    
    return [
        # Non-empty collections
        CtyValue(string_list_type, string_list_value),
        CtyValue(string_number_map_type, string_number_map_value),
        CtyValue(bool_set_type, bool_set_value),
        
        # Empty collections
        CtyValue(empty_list_type, []),
        CtyValue(empty_map_type, {}),
        CtyValue(empty_set_type, set()),
    ]


@pytest.fixture
def structural_values():
    """Fixture providing structural Cty values for testing."""
    # Object types and values
    person_type = CtyObject(attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool(),
    })
    
    person_value = {
        "name": CtyValue(CtyString(), "Alice"),
        "age": CtyValue(CtyNumber(), 30),
        "active": CtyValue(CtyBool(), True),
    }
    
    empty_object_type = CtyObject(attribute_types={})
    
    # Tuple types and values
    point_type = CtyTuple(element_types=(CtyNumber(), CtyNumber(), CtyString()))
    
    point_value = (
        CtyValue(CtyNumber(), 10.5),
        CtyValue(CtyNumber(), 20.3),
        CtyValue(CtyString(), "point_a"),
    )
    
    empty_tuple_type = CtyTuple(element_types=())
    
    # Dynamic type and values
    dynamic_type = CtyDynamic()
    
    return [
        # Object values
        CtyValue(person_type, person_value),
        CtyValue(empty_object_type, {}),
        
        # Tuple values
        CtyValue(point_type, point_value),
        CtyValue(empty_tuple_type, ()),
        
        # Dynamic values
        CtyValue(dynamic_type, "dynamic string"),
        CtyValue(dynamic_type, 42),
        CtyValue(dynamic_type, True),
        CtyValue(dynamic_type, ["list", "of", "values"]),
        CtyValue(dynamic_type, {"key": "value"}),
    ]


@pytest.fixture
def special_state_values():
    """Fixture providing Cty values with special states."""
    # Unknown values
    unknown_string = CtyValue(CtyString(), is_unknown=True)
    unknown_number = CtyValue(CtyNumber(), is_unknown=True)
    unknown_bool = CtyValue(CtyBool(), is_unknown=True)
    unknown_list = CtyValue(CtyList(element_type=CtyString()), is_unknown=True)
    unknown_object = CtyValue(
        CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()}),
        is_unknown=True
    )
    
    # Null values
    null_string = CtyValue(CtyString(), is_null=True)
    null_number = CtyValue(CtyNumber(), is_null=True)
    null_bool = CtyValue(CtyBool(), is_null=True)
    null_list = CtyValue(CtyList(element_type=CtyString()), is_null=True)
    null_object = CtyValue(
        CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()}),
        is_null=True
    )
    
    # Marked values
    marked_string = CtyValue(CtyString(), "sensitive data").mark("sensitive")
    marked_number = CtyValue(CtyNumber(), 42).mark("computed").mark("internal")
    
    return [
        # Unknown values
        unknown_string,
        unknown_number,
        unknown_bool,
        unknown_list,
        unknown_object,
        
        # Null values
        null_string,
        null_number,
        null_bool,
        null_list,
        null_object,
        
        # Marked values
        marked_string,
        marked_number,
    ]


@pytest.fixture
def complex_nested_value():
    """Fixture providing a complex nested Cty value for testing."""
    # Define types
    string_type = CtyString()
    number_type = CtyNumber()
    bool_type = CtyBool()
    
    # Define nested structure
    server_config_type = CtyObject(attribute_types={
        "hostname": string_type,
        "port": number_type,
        "settings": CtyObject(attribute_types={
            "debug": bool_type,
            "timeout": number_type,
            "retry_attempts": number_type,
        }),
        "endpoints": CtyList(element_type=string_type),
        "security": CtyObject(attribute_types={
            "enabled": bool_type,
            "certificates": CtyList(element_type=
                CtyObject(attribute_types={
                    "name": string_type,
                    "expiry": string_type,
                    "active": bool_type,
                })
            ),
        }),
        "tags": CtySet(element_type=string_type),
        "environment": CtyMap(key_type=string_type, value_type=string_type),
    })
    
    # Create complex value
    server_config_value = {
        "hostname": CtyValue(string_type, "api.example.com"),
        "port": CtyValue(number_type, 443),
        "settings": CtyValue(
            CtyObject(attribute_types={
                "debug": bool_type,
                "timeout": number_type,
                "retry_attempts": number_type,
            }),
            {
                "debug": CtyValue(bool_type, False),
                "timeout": CtyValue(number_type, 30),
                "retry_attempts": CtyValue(number_type, 3),
            }
        ),
        "endpoints": CtyValue(
            CtyList(element_type=string_type),
            [
                CtyValue(string_type, "/api/v1/users"),
                CtyValue(string_type, "/api/v1/products"),
                CtyValue(string_type, "/api/v1/orders"),
            ]
        ),
        "security": CtyValue(
            CtyObject(attribute_types={
                "enabled": bool_type,
                "certificates": CtyList(element_type=
                    CtyObject(attribute_types={
                        "name": string_type,
                        "expiry": string_type,
                        "active": bool_type,
                    })
                ),
            }),
            {
                "enabled": CtyValue(bool_type, True),
                "certificates": CtyValue(
                    CtyList(element_type=
                        CtyObject(attribute_types={
                            "name": string_type,
                            "expiry": string_type,
                            "active": bool_type,
                        })
                    ),
                    [
                        CtyValue(
                            CtyObject(attribute_types={
                                "name": string_type,
                                "expiry": string_type,
                                "active": bool_type,
                            }),
                            {
                                "name": CtyValue(string_type, "api.example.com"),
                                "expiry": CtyValue(string_type, "2025-12-31"),
                                "active": CtyValue(bool_type, True),
                            }
                        ),
                        CtyValue(
                            CtyObject(attribute_types={
                                "name": string_type,
                                "expiry": string_type,
                                "active": bool_type,
                            }),
                            {
                                "name": CtyValue(string_type, "*.example.com"),
                                "expiry": CtyValue(string_type, "2025-12-31"),
                                "active": CtyValue(bool_type, False),
                            }
                        ),
                    ]
                ),
            }
        ),
        "tags": CtyValue(
            CtySet(element_type=string_type),
            {
                CtyValue(string_type, "production"),
                CtyValue(string_type, "api"),
                CtyValue(string_type, "secure"),
            }
        ),
        "environment": CtyValue(
            CtyMap(key_type=string_type, value_type=string_type),
            {
                CtyValue(string_type, "NODE_ENV"): CtyValue(string_type, "production"),
                CtyValue(string_type, "LOG_LEVEL"): CtyValue(string_type, "info"),
                CtyValue(string_type, "API_VERSION"): CtyValue(string_type, "v1"),
            }
        ),
    }
    
    return CtyValue(server_config_type, server_config_value)


# Integration Tests for both serializers
@pytest.mark.parametrize("serializer_class", [JsonSerializer, MsgpackSerializer])
class TestSerializerIntegration:
    """Integration tests for Cty serializers."""
    
    @pytest.mark.asyncio
    async def test_primitive_values_roundtrip(self, serializer_class, primitive_values):
        """Test serialization and deserialization of primitive values."""
        serializer = serializer_class()
        
        for value in primitive_values:
            # Serialize
            serialized = await serializer.serialize(value)
            assert isinstance(serialized, bytes)
            assert len(serialized) > 0
            
            # Deserialize
            deserialized = await serializer.deserialize(serialized)
            
            # Check value is preserved
            assert isinstance(deserialized, CtyValue)
            assert deserialized.type.__class__ == value.type.__class__
            
            # For number values, compare as Decimal to handle precision
            if isinstance(value.value, (int, float, Decimal)):
                assert Decimal(str(deserialized.value)) == Decimal(str(value.value))
            else:
                assert deserialized.value == value.value
            
            # Check special states are preserved
            assert deserialized.is_known == value.is_known
            assert deserialized.is_null == value.is_null
    
    @pytest.mark.asyncio
    async def test_collection_values_roundtrip(self, serializer_class, collection_values):
        """Test serialization and deserialization of collection values."""
        serializer = serializer_class()
        
        for value in collection_values:
            # Serialize
            serialized = await serializer.serialize(value)
            assert isinstance(serialized, bytes)
            assert len(serialized) > 0
            
            # Deserialize
            deserialized = await serializer.deserialize(serialized)
            
            # Check type is preserved
            assert isinstance(deserialized, CtyValue)
            assert deserialized.type.__class__ == value.type.__class__
            
            # Check collection length
            if isinstance(value.value, list):
                assert len(deserialized.value) == len(value.value)
            elif isinstance(value.value, dict):
                assert len(deserialized.value) == len(value.value)
            elif isinstance(value.value, set):
                assert len(deserialized.value) == len(value.value)
            
            # Check special states are preserved
            assert deserialized.is_known == value.is_known
            assert deserialized.is_null == value.is_null
    
    @pytest.mark.asyncio
    async def test_structural_values_roundtrip(self, serializer_class, structural_values):
        """Test serialization and deserialization of structural values."""
        serializer = serializer_class()
        
        for value in structural_values:
            # Serialize
            serialized = await serializer.serialize(value)
            assert isinstance(serialized, bytes)
            assert len(serialized) > 0
            
            # Deserialize
            deserialized = await serializer.deserialize(serialized)
            
            # Check type is preserved
            assert isinstance(deserialized, CtyValue)
            assert deserialized.type.__class__ == value.type.__class__
            
            # Check special states are preserved
            assert deserialized.is_known == value.is_known
            assert deserialized.is_null == value.is_null
    
    @pytest.mark.asyncio
    async def test_special_state_values_roundtrip(self, serializer_class, special_state_values):
        """Test serialization and deserialization of values with special states."""
        serializer = serializer_class()
        
        for value in special_state_values:
            # Serialize
            serialized = await serializer.serialize(value)
            assert isinstance(serialized, bytes)
            assert len(serialized) > 0
            
            # Deserialize
            deserialized = await serializer.deserialize(serialized)
            
            # Check type is preserved
            assert isinstance(deserialized, CtyValue)
            assert deserialized.type.__class__ == value.type.__class__
            
            # Check special states are preserved
            assert deserialized.is_known == value.is_known
            assert deserialized.is_null == value.is_null
            
            # Check marks are preserved if applicable
            if hasattr(value, 'marks') and value.marks:
                for mark in value.marks:
                    assert deserialized.has_mark(mark)
    
    @pytest.mark.asyncio
    async def test_complex_nested_value_roundtrip(self, serializer_class, complex_nested_value):
        """Test serialization and deserialization of a complex nested value."""
        serializer = serializer_class()
        
        # Serialize
        serialized = await serializer.serialize(complex_nested_value)
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0
        
        # Deserialize
        deserialized = await serializer.deserialize(serialized)
        
        # Check type is preserved
        assert isinstance(deserialized, CtyValue)
        assert deserialized.type.__class__ == complex_nested_value.type.__class__
        
        # Check special states are preserved
        assert deserialized.is_known == complex_nested_value.is_known
        assert deserialized.is_null == complex_nested_value.is_null
        
        # Check structure is preserved
        value = deserialized.value
        assert "hostname" in value
        assert "port" in value
        assert "settings" in value
        assert "endpoints" in value
        assert "security" in value
        assert "tags" in value
        assert "environment" in value
        
        # Check nested structure
        assert "debug" in value["settings"].value
        assert "timeout" in value["settings"].value
        assert "retry_attempts" in value["settings"].value
        
        assert "enabled" in value["security"].value
        assert "certificates" in value["security"].value
        
        # Check value contents (sampling a few)
        assert value["hostname"].value == "api.example.com"
        assert value["port"].value == 443
        assert value["settings"].value["debug"].value is False
        assert value["settings"].value["timeout"].value == 30
        assert value["security"].value["enabled"].value is True
    
    @pytest.mark.asyncio
    async def test_typed_serialization_roundtrip(self, serializer_class, primitive_values):
        """Test typed serialization and deserialization."""
        # Skip if serializer doesn't support typed serialization
        if not hasattr(serializer_class, 'serialize_with_type'):
            pytest.skip(f"{serializer_class.__name__} doesn't support typed serialization")
        
        serializer = serializer_class()
        
        for value in primitive_values:
            # Serialize with type
            serialized = await serializer.serialize_with_type(value.value, value.type)
            assert isinstance(serialized, bytes)
            assert len(serialized) > 0
            
            # Deserialize with type
            deserialized = await serializer.deserialize_with_type(serialized, value.type)
            
            # For number values, compare as Decimal to handle precision
            if isinstance(value.value, (int, float, Decimal)):
                assert Decimal(str(deserialized)) == Decimal(str(value.value))
            else:
                assert deserialized == value.value


# MessagePack-specific tests
class TestMsgpackSpecific:
    """Tests specific to the MessagePack serializer."""
    
    @pytest.mark.asyncio
    async def test_marshal_unmarshal_roundtrip(self, primitive_values):
        """Test marshal and unmarshal functions."""
        for value in primitive_values:
            # Marshal
            marshaled = marshal(value)
            assert isinstance(marshaled, bytes)
            assert len(marshaled) > 0
            
            # Unmarshal
            unmarshaled = unmarshal(marshaled)
            
            # Check value is preserved
            assert isinstance(unmarshaled, CtyValue)
            assert unmarshaled.type.__class__ == value.type.__class__
            
            # For number values, compare as Decimal to handle precision
            if isinstance(value.value, (int, float, Decimal)):
                assert Decimal(str(unmarshaled.value)) == Decimal(str(value.value))
            else:
                assert unmarshaled.value == value.value
            
            # Check special states are preserved
            assert unmarshaled.is_known == value.is_known
            assert unmarshaled.is_null == value.is_null
    
    @pytest.mark.asyncio
    async def test_marshal_unmarshal_special_states(self, special_state_values):
        """Test marshal and unmarshal with special state values."""
        for value in special_state_values:
            # Marshal
            marshaled = marshal(value)
            assert isinstance(marshaled, bytes)
            assert len(marshaled) > 0
            
            # Unmarshal
            unmarshaled = unmarshal(marshaled)
            
            # Check type is preserved
            assert isinstance(unmarshaled, CtyValue)
            assert unmarshaled.type.__class__ == value.type.__class__
            
            # Check special states are preserved
            assert unmarshaled.is_known == value.is_known
            assert unmarshaled.is_null == value.is_null
            
            # Check marks are preserved if applicable
            if hasattr(value, 'marks') and value.marks:
                for mark in value.marks:
                    assert unmarshaled.has_mark(mark)
    
    @pytest.mark.asyncio
    async def test_msgpack_magic_bytes(self):
        """Test MessagePack magic bytes detection."""
        serializer = MsgpackSerializer()
        
        # Create a simple value
        value = CtyValue(CtyString(), "test")
        
        # Serialize
        serialized = await serializer.serialize(value)
        
        # Check magic bytes
        assert len(serialized) > 5
        assert serialized[:5] == bytes([80, 67, 84, 89, 1])  # "PCTY" + version (1)
        
        # Deserialize with magic bytes
        deserialized = await serializer.deserialize(serialized)
        assert isinstance(deserialized, CtyValue)
        assert deserialized.value == "test"
        
        # Deserialize without magic bytes (should still work)
        deserialized = await serializer.deserialize(serialized[5:])
        assert isinstance(deserialized, CtyValue)
        assert deserialized.value == "test"


# Utility functions tests
class TestSerializationUtils:
    """Tests for the serialization utility functions."""
    
    @pytest.mark.asyncio
    async def test_serialize_deserialize(self, primitive_values):
        """Test serialize and deserialize utility functions."""
        for value in primitive_values:
            # Test with JSON format
            json_data = await serialize(value, format_name="json")
            assert isinstance(json_data, bytes)
            
            json_result = await deserialize(json_data)
            assert isinstance(json_result, CtyValue)
            assert json_result.type.__class__ == value.type.__class__
            
            # Test with MessagePack format
            msgpack_data = await serialize(value, format_name="msgpack")
            assert isinstance(msgpack_data, bytes)
            
            msgpack_result = await deserialize(msgpack_data)
            assert isinstance(msgpack_result, CtyValue)
            assert msgpack_result.type.__class__ == value.type.__class__
            
            # Test auto-detection
            auto_result = await deserialize(json_data)
            assert isinstance(auto_result, CtyValue)
            assert auto_result.type.__class__ == value.type.__class__
    
    @pytest.mark.asyncio
    async def test_serialize_with_type_deserialize_with_type(self, primitive_values):
        """Test serialize_with_type and deserialize_with_type utility functions."""
        for value in primitive_values:
            # Test with JSON format
            json_data = await serialize_with_type(value.value, value.type, format_name="json")
            assert isinstance(json_data, bytes)
            
            json_result = await deserialize_with_type(json_data, value.type)
            
            # For number values, compare as Decimal to handle precision
            if isinstance(value.value, (int, float, Decimal)):
                assert Decimal(str(json_result)) == Decimal(str(value.value))
            else:
                assert json_result == value.value
            
            # Test with MessagePack format
            msgpack_data = await serialize_with_type(value.value, value.type, format_name="msgpack")
            assert isinstance(msgpack_data, bytes)
            
            msgpack_result = await deserialize_with_type(msgpack_data, value.type)
            
            # For number values, compare as Decimal to handle precision
            if isinstance(value.value, (int, float, Decimal)):
                assert Decimal(str(msgpack_result)) == Decimal(str(value.value))
            else:
                assert msgpack_result == value.value
            
            # Test auto-detection
            auto_result = await deserialize_with_type(json_data, value.type)
            
            # For number values, compare as Decimal to handle precision
            if isinstance(value.value, (int, float, Decimal)):
                assert Decimal(str(auto_result)) == Decimal(str(value.value))
            else:
                assert auto_result == value.value


# Edge case tests
class TestEdgeCases:
    """Tests for edge cases in serialization and deserialization."""
    
    @pytest.mark.asyncio
    async def test_empty_data(self):
        """Test deserializing empty data."""
        with pytest.raises(Exception):
            await deserialize(b"")
    
    @pytest.mark.asyncio
    async def test_invalid_json(self):
        """Test deserializing invalid JSON."""
        with pytest.raises(Exception):
            await deserialize(b"{invalid:json}")
    
    @pytest.mark.asyncio
    async def test_invalid_msgpack(self):
        """Test deserializing invalid MessagePack."""
        with pytest.raises(Exception):
            serializer = MsgpackSerializer()
            await serializer.deserialize(b"\x00\x01\x02invalid")
    
    @pytest.mark.skip
    async def test_unsupported_type(self):
        """Test serializing unsupported types."""
        class UnsupportedType:
            def __repr__(self):
                return "UnsupportedType()"
        
        with pytest.raises(Exception):
            await serialize(UnsupportedType())
    
    @pytest.mark.asyncio
    async def test_type_mismatch(self):
        """Test type mismatch in typed deserialization."""
        # Create a string value
        string_value = CtyValue(CtyString(), "test")
        
        # Serialize with type
        serialized = await serialize_with_type(string_value.value, string_value.type)
        
        # Try to deserialize with wrong type
        with pytest.raises(Exception):
            await deserialize_with_type(serialized, CtyNumber())

# 🐍🏗️🐣
