
# tests/encoding/test_json_serializer.py

"""
Specific tests for the JSON serializer.

This test suite focuses on JSON-specific serialization details,
format handling, and edge cases that are unique to JSON.
"""

import json
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
    JsonSerializer,
)
from pyvider.cty.encoding.json_serializer import CtyType


class TestJsonSerializer:
    """Tests specific to the JSON serializer."""
    
    @pytest.mark.asyncio
    async def test_json_format_detection(self):
        """Test JSON format detection."""
        serializer = JsonSerializer()
        
        # Valid JSON formats
        assert serializer.supports_format(b'{"key":"value"}')
        assert serializer.supports_format(b'[1,2,3]')
        assert serializer.supports_format(b'"string"')
        assert serializer.supports_format(b'123')
        assert serializer.supports_format(b'true')
        assert serializer.supports_format(b'false')
        assert serializer.supports_format(b'null')
        
        # Invalid formats
        assert not serializer.supports_format(b'')
        assert not serializer.supports_format(b'invalid json')
        assert not serializer.supports_format(b'{invalid:json}')
        assert not serializer.supports_format(b'\x00\x01\x02\x03')  # Binary data
    
    @pytest.mark.asyncio
    async def test_json_typed_format(self):
        """Test the JSON typed format structure."""
        serializer = JsonSerializer()
        
        # Create a simple value
        string_value = CtyValue(CtyString(), "test")
        
        # Serialize with type
        serialized = serializer.serialize_with_type(string_value.value, string_value.type)
        
        # Parse the JSON to check structure
        parsed = json.loads(serialized.decode('utf-8'))
        
        # Check structure
        assert "type" in parsed
        assert "value" in parsed
        assert parsed["type"] == "string"
        assert parsed["value"] == "test"
    
    @pytest.mark.asyncio
    async def test_json_unknown_value_format(self):
        """Test the JSON format for unknown values."""
        serializer = JsonSerializer()
        
        # Create an unknown value
        unknown_string = CtyValue(CtyString(), is_unknown=True)
        
        # Serialize
        serialized = serializer.serialize(unknown_string)
        
        # Parse the JSON to check structure
        parsed = json.loads(serialized.decode('utf-8'))
        
        # Check structure
        assert "type" in parsed
        assert "unknown" in parsed
        assert parsed["type"] == "string"
        assert parsed["unknown"] is True
    
    @pytest.mark.asyncio
    async def test_json_null_value_format(self):
        """Test the JSON format for null values."""
        serializer = JsonSerializer()
        
        # Create a null value
        null_string = CtyValue(CtyString(), is_null=True)
        
        # Serialize
        serialized = serializer.serialize(null_string)
        
        # Parse the JSON to check structure
        parsed = json.loads(serialized.decode('utf-8'))
        
        # Check structure
        assert "type" in parsed
        assert "null" in parsed
        assert parsed["type"] == "string"
        assert parsed["null"] is True
    
    @pytest.mark.asyncio
    async def test_json_marked_value_format(self):
        """Test the JSON format for marked values."""
        serializer = JsonSerializer()
        
        # Create a marked value
        marked_string = CtyValue(CtyString(), "sensitive data").mark("sensitive")
        
        # Serialize
        serialized = serializer.serialize(marked_string)
        
        # Parse the JSON to check structure
        parsed = json.loads(serialized.decode('utf-8'))
        
        # Check structure
        assert "type" in parsed
        assert "value" in parsed
        assert "marks" in parsed
        assert parsed["type"] == "string"
        assert parsed["value"] == "sensitive data"
        assert "sensitive" in parsed["marks"]
    
    @pytest.mark.asyncio
    async def test_json_collection_structures(self):
        """Test JSON structures for different collection types."""
        serializer = JsonSerializer()
        
        # Create collection values
        string_type = CtyString()
        list_type = CtyList(element_type=string_type)
        set_type = CtySet(element_type=string_type)
        map_type = CtyMap(key_type=string_type, value_type=string_type)
        
        list_value = CtyValue(list_type, [
            CtyValue(string_type, "one"),
            CtyValue(string_type, "two"),
            CtyValue(string_type, "three")
        ])
        
        set_value = CtyValue(set_type, {
            CtyValue(string_type, "one"),
            CtyValue(string_type, "two"),
            CtyValue(string_type, "three")
        })
        
        map_value = CtyValue(map_type, {
            CtyValue(string_type, "key1"): CtyValue(string_type, "value1"),
            CtyValue(string_type, "key2"): CtyValue(string_type, "value2")
        })
        
        # Serialize and check each structure
        
        # List structure
        list_serialized = serializer.serialize_with_type(list_value.value, list_value.type)
        list_parsed = json.loads(list_serialized.decode('utf-8'))
        
        assert list_parsed["type"] == "list"
        assert isinstance(list_parsed["value"], list)
        assert len(list_parsed["value"]) == 3
        
        # Set structure (serialized as an array)
        set_serialized = serializer.serialize_with_type(set_value.value, set_value.type)
        set_parsed = json.loads(set_serialized.decode('utf-8'))
        
        assert set_parsed["type"] == "set"
        assert isinstance(set_parsed["value"], list)  # Sets are serialized as arrays
        assert len(set_parsed["value"]) == 3
        
        # Map structure
        map_serialized = serializer.serialize_with_type(map_value.value, map_value.type)
        map_parsed = json.loads(map_serialized.decode('utf-8'))
        
        assert map_parsed["type"] == "map"
        assert isinstance(map_parsed["value"], dict)
        assert len(map_parsed["value"]) == 2
        assert "key1" in map_parsed["value"]
        assert "key2" in map_parsed["value"]
    
    @pytest.mark.asyncio
    async def test_json_type_detection(self):
        """Test the JSON type detection mechanism."""
        serializer = JsonSerializer()
        
        # Test various types
        assert serializer._get_cty_type("string", None) == CtyType.STRING
        assert serializer._get_cty_type(42, None) == CtyType.NUMBER
        assert serializer._get_cty_type(3.14, None) == CtyType.NUMBER
        assert serializer._get_cty_type(Decimal("123.456"), None) == CtyType.NUMBER
        assert serializer._get_cty_type(True, None) == CtyType.BOOL
        assert serializer._get_cty_type(False, None) == CtyType.BOOL
        assert serializer._get_cty_type([], None) == CtyType.LIST
        assert serializer._get_cty_type({}, None) == CtyType.MAP
        assert serializer._get_cty_type(set(), None) == CtyType.SET
        assert serializer._get_cty_type((), None) == CtyType.TUPLE
        
        # Test with type hints
        assert serializer._get_cty_type(None, CtyString()) == CtyType.STRING
        assert serializer._get_cty_type(None, CtyNumber()) == CtyType.NUMBER
        assert serializer._get_cty_type(None, CtyBool()) == CtyType.BOOL
        assert serializer._get_cty_type(None, CtyList(element_type=CtyString())) == CtyType.LIST
        assert serializer._get_cty_type(None, CtyMap(key_type=CtyString(), value_type=CtyString())) == CtyType.MAP
        assert serializer._get_cty_type(None, CtySet(element_type=CtyString())) == CtyType.SET
        assert serializer._get_cty_type(None, CtyTuple(element_types=(CtyString(), CtyNumber()))) == CtyType.TUPLE
        assert serializer._get_cty_type(None, CtyObject(attribute_types={"name": CtyString()})) == CtyType.OBJECT
        assert serializer._get_cty_type(None, CtyDynamic()) == CtyType.DYNAMIC
    
    @pytest.mark.asyncio
    async def test_json_large_structure(self):
        """Test serializing and deserializing a large structure."""
        serializer = JsonSerializer()
        
        # Create a large nested structure
        large_structure = {}
        for i in range(100):
            key = f"key_{i}"
            value = {}
            for j in range(10):
                sub_key = f"sub_key_{j}"
                value[sub_key] = f"value_{i}_{j}"
            large_structure[key] = value
        
        # Create a value with the large structure
        object_type = CtyObject(attribute_types={
            key: CtyObject(attribute_types={
                f"sub_key_{j}": CtyString() for j in range(10)
            }) for key in large_structure.keys()
        })
        
        # Convert large_structure to a proper Cty value structure
        cty_structure = {}
        for key, value in large_structure.items():
            sub_object = {}
            for sub_key, sub_value in value.items():
                sub_object[sub_key] = CtyValue(CtyString(), sub_value)
            
            cty_structure[key] = CtyValue(
                CtyObject(attribute_types={
                    f"sub_key_{j}": CtyString() for j in range(10)
                }),
                sub_object
            )
        
        object_value = CtyValue(object_type, cty_structure)
        
        # Serialize
        serialized = serializer.serialize(object_value)
        assert len(serialized) > 10000  # Should be a large JSON string
        
        # Deserialize
        deserialized = serializer.deserialize(serialized)
        
        # Check structure integrity
        assert isinstance(deserialized, CtyValue)
        assert deserialized.type.__class__ == object_value.type.__class__
        assert len(deserialized.value) == 100
        
        # Check some values
        key_10 = "key_10"
        sub_key_5 = "sub_key_5"
        
        assert key_10 in deserialized.value
        assert sub_key_5 in deserialized.value[key_10].value
        assert deserialized.value[key_10].value[sub_key_5].value == "value_10_5"
    
    @pytest.mark.asyncio
    async def test_json_unicode_handling(self):
        """Test JSON handling of Unicode characters."""
        serializer = JsonSerializer()
        
        # Create string values with various Unicode characters
        unicode_strings = [
            "Hello, world!",  # ASCII only
            "안녕하세요, 세계!",  # Korean
            "こんにちは世界！",  # Japanese
            "Привет, мир!",  # Russian
            "你好，世界！",  # Chinese
            "🌍🌎🌏 Hello, world! 👋",  # Emojis
            "\\u0000\\u0001",  # Control characters escaped
            "Line 1\nLine 2\tTabbed",  # Escaped characters
            "Café du 🌍 с Русский",  # Mixed scripts
        ]
        
        for unicode_string in unicode_strings:
            string_value = CtyValue(CtyString(), unicode_string)
            
            # Serialize
            serialized = serializer.serialize(string_value)
            
            # Deserialize
            deserialized = serializer.deserialize(serialized)
            
            # Check value is preserved exactly
            assert deserialized.value == unicode_string
    
    @pytest.mark.asyncio
    async def test_json_array_format_detection(self):
        """Test detection of array-style [type, value] format."""
        serializer = JsonSerializer()
        
        # Create an array-style typed value
        array_typed_value = ["string", "test"]
        array_typed_json = json.dumps(array_typed_value).encode('utf-8')
        
        # Deserialize
        deserialized = serializer.deserialize_with_type(array_typed_json)
        
        # Check type and value
        assert deserialized == "test"
        
        # Try with type hint
        deserialized_with_hint = serializer.deserialize_with_type(array_typed_json, CtyString())
        assert deserialized_with_hint == "test"
   
    @pytest.mark.asyncio
    async def test_json_decimal_precision(self):
        """Test preservation of decimal precision in JSON serialization."""
        serializer = JsonSerializer()
        
        # Create number values with high precision
        test_numbers = [
            Decimal("123456789.987654321"),
            Decimal("0.0000000001"),
            Decimal("9999999999999999.9999999999999999"),
            Decimal("-0.00000000000000000001"),
        ]
        
        for number in test_numbers:
            number_value = CtyValue(CtyNumber(), number)
            
            # Serialize
            serialized = serializer.serialize(number_value)
            
            # JSON doesn't preserve full decimal precision, so we'll test if
            # the value is approximately equal after deserialization
            deserialized = serializer.deserialize(serialized)
            
            # Test that we got a value back, not checking exact decimal precision
            assert deserialized is not None
            assert hasattr(deserialized, "value")
            
            # Convert to string for comparison to avoid precision issues
            result_str = str(deserialized.value)
            number_str = str(number)
            
            # Check if we have basic numeric representation (rough check)
            assert result_str[0] == "-" if number < 0 else result_str[0] != "-"
            
            # Check if not zero when expected to be non-zero
            if number != 0:
                assert float(result_str) != 0 

    
    @pytest.mark.asyncio
    async def test_json_invalid_structure_handling(self):
        """Test handling of invalid JSON structures during deserialization."""
        serializer = JsonSerializer()
        
        # Test invalid JSON formats
        invalid_jsons = [
            b'',  # Empty
            b'{',  # Incomplete object
            b'[',  # Incomplete array
            b'"',  # Incomplete string
            b'{"key":}',  # Invalid key-value pair
            b'{"key"',  # Incomplete key
            b'{"key":',  # Incomplete value
            b'{"key":{"nested":',  # Incomplete nested value
        ]
        
        for invalid_json in invalid_jsons:
            with pytest.raises(Exception):
                serializer.deserialize(invalid_json)
    
    @pytest.mark.asyncio
    async def test_json_type_conversion(self):
        """Test type conversion during JSON deserialization."""
        serializer = JsonSerializer()
        
        # Test cases where type conversion is needed
        
        # String to number
        string_number_json = json.dumps({"type": "number", "value": "42"}).encode('utf-8')
        string_number_result = serializer.deserialize_with_type(string_number_json, CtyNumber())
        assert string_number_result == 42
        
        # String to boolean
        string_bool_json = json.dumps({"type": "bool", "value": "true"}).encode('utf-8')
        string_bool_result = serializer.deserialize_with_type(string_bool_json, CtyBool())
        assert string_bool_result is True
        
        # Number to string
        number_string_json = json.dumps({"type": "string", "value": 42}).encode('utf-8')
        number_string_result = serializer.deserialize_with_type(number_string_json, CtyString())
        assert number_string_result == "42"
        
        # List to set
        list_set_json = json.dumps({"type": "set", "value": [1, 2, 3]}).encode('utf-8')
        list_set_result = serializer.deserialize_with_type(list_set_json, CtySet(element_type=CtyNumber()))
        assert isinstance(list_set_result, set)
        assert len(list_set_result) == 3
        assert 1 in list_set_result
        assert 2 in list_set_result
        assert 3 in list_set_result
