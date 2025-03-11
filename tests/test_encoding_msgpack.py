
# tests/cty/encoding/test_msgpack_integration.py

"""
Integration tests for CTY MessagePack encoding module.

This test suite verifies the serialization and deserialization of CTY values
to/from MessagePack format. It covers all CTY types, special values (null and unknown),
and ensures proper round-trip encoding/decoding.
"""

import asyncio
import json
import pytest
from decimal import Decimal
from typing import Dict, List, Set, Any

import msgpack

from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyObject, CtyTuple, CtyDynamic
from pyvider.cty.values.base import Value
from pyvider.cty.encoding.msgpack import (
    encode_value, decode_value, encode_type, decode_type,
    marshal, unmarshal, MsgpackEncodeError, MsgpackDecodeError
)


class TestCtyMsgpackIntegration:
    """Integration tests for CTY MessagePack encoding and decoding."""
    
    @pytest.mark.asyncio
    async def test_encode_decode_string(self):
        """Test encoding and decoding string values."""
        # Create string values
        string_type = CtyString()
        test_values = [
            "Hello, world!",
            "",
            "Special chars: ñáéíóú",
            "Symbols: !@#$%^&*()",
            "1234567890"
        ]
        
        for value in test_values:
            # Create a CTY string value
            cty_value = Value(string_type, raw_value=value)
            
            # Encode to MessagePack
            encoded = await encode_value(cty_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, string_type)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == CtyString
            assert decoded.raw_value == value
    
    @pytest.mark.asyncio
    async def test_encode_decode_number(self):
        """Test encoding and decoding number values."""
        # Create number values
        number_type = CtyNumber()
        test_values = [
            0,
            42,
            -42,
            3.14159,
            -3.14159,
            Decimal("123456789.987654321"),
            Decimal("-123456789.987654321")
        ]
        
        for value in test_values:
            # Convert to Decimal for consistency
            decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
            
            # Create a CTY number value
            cty_value = Value(number_type, raw_value=decimal_value)
            
            # Encode to MessagePack
            encoded = await encode_value(cty_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, number_type)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == CtyNumber
            
            # Compare with appropriate precision
            if isinstance(value, int):
                assert decoded.raw_value == decimal_value
            else:
                # Allow for floating point imprecision
                # We're comparing the encoded/decoded values, not raw to decoded
                # So unpacking the original message is the right comparison
                unpacked = msgpack.unpackb(encoded)
                if isinstance(unpacked, int):
                    assert int(decoded.raw_value) == unpacked
                else:
                    assert float(decoded.raw_value) == pytest.approx(unpacked)
    
    @pytest.mark.asyncio
    async def test_encode_decode_bool(self):
        """Test encoding and decoding boolean values."""
        # Create boolean values
        bool_type = CtyBool()
        test_values = [True, False]
        
        for value in test_values:
            # Create a CTY boolean value
            cty_value = Value(bool_type, raw_value=value)
            
            # Encode to MessagePack
            encoded = await encode_value(cty_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, bool_type)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == CtyBool
            assert decoded.raw_value == value
    
    @pytest.mark.asyncio
    async def test_encode_decode_list(self):
        """Test encoding and decoding list values."""
        # Create list values
        string_type = CtyString()
        list_type = CtyList(element_type=string_type)
        
        test_values = [
            [],
            ["one"],
            ["one", "two", "three"],
            ["", "empty", ""],
            ["special", "chars: !@#$"]
        ]
        
        for value in test_values:
            # Create CTY list value with string elements
            elements = [Value(string_type, raw_value=item) for item in value]
            cty_value = Value(list_type, raw_value=elements)
            
            # Encode to MessagePack
            encoded = await encode_value(cty_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, list_type)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == CtyList
            
            # Compare the list elements
            assert len(decoded.raw_value) == len(elements)
            for i, item in enumerate(decoded.raw_value):
                assert item.raw_value == elements[i].raw_value
    
    @pytest.mark.asyncio
    async def test_encode_decode_map(self):
        """Test encoding and decoding map values."""
        # Create map values
        string_type = CtyString()
        number_type = CtyNumber()
        map_type = CtyMap(key_type=string_type, value_type=number_type)
        
        test_values = [
            {},
            {"one": 1},
            {"one": 1, "two": 2, "three": 3},
            {"pi": Decimal("3.14159"), "e": Decimal("2.71828")}
        ]
        
        for value in test_values:
            # Create CTY map value
            elements = {
                Value(string_type, raw_value=k): Value(number_type, raw_value=Decimal(str(v)))
                for k, v in value.items()
            }
            cty_value = Value(map_type, raw_value=elements)
            
            # Encode to MessagePack
            encoded = await encode_value(cty_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, map_type)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == CtyMap
            
            # Compare the map elements
            assert len(decoded.raw_value) == len(elements)
            for k, v in elements.items():
                # Find matching key
                found = False
                for dk, dv in decoded.raw_value.items():
                    if dk.raw_value == k.raw_value:
                        assert dv.raw_value == v.raw_value
                        found = True
                        break
                assert found, f"Key {k.raw_value} not found in decoded map"
    
    @pytest.mark.asyncio
    async def test_encode_decode_set(self):
        """Test encoding and decoding set values."""
        # Create set values
        string_type = CtyString()
        set_type = CtySet(element_type=string_type)
        
        test_values = [
            set(),
            {"one"},
            {"one", "two", "three"},
            {"", "empty"},
            {"special", "chars: !@#$"}
        ]
        
        for value in test_values:
            # Create CTY set value
            elements = {Value(string_type, raw_value=item) for item in value}
            cty_value = Value(set_type, raw_value=elements)
            
            # Encode to MessagePack
            encoded = await encode_value(cty_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, set_type)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == CtySet
            
            # Compare the set elements
            assert len(decoded.raw_value) == len(elements)
            decoded_values = {item.raw_value for item in decoded.raw_value}
            expected_values = {item.raw_value for item in elements}
            assert decoded_values == expected_values
    
    @pytest.mark.asyncio
    async def test_encode_decode_object(self):
        """Test encoding and decoding object values."""
        # Create object type with mixed attributes
        object_type = CtyObject(attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool()
        })
        
        test_values = [
            {
                "name": "Alice",
                "age": Decimal("30"),
                "active": True
            },
            {
                "name": "Bob",
                "age": Decimal("25"),
                "active": False
            },
            {
                "name": "",
                "age": Decimal("0"),
                "active": False
            }
        ]
        
        for value in test_values:
            # Create CTY object value
            attributes = {
                "name": Value(CtyString(), raw_value=value["name"]),
                "age": Value(CtyNumber(), raw_value=value["age"]),
                "active": Value(CtyBool(), raw_value=value["active"])
            }
            cty_value = Value(object_type, raw_value=attributes)
            
            # Encode to MessagePack
            encoded = await encode_value(cty_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, object_type)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == CtyObject
            
            # Compare the object attributes
            assert len(decoded.raw_value) == len(attributes)
            for attr_name, attr_value in attributes.items():
                assert attr_name in decoded.raw_value
                assert decoded.raw_value[attr_name].raw_value == attr_value.raw_value
    
    @pytest.mark.asyncio
    async def test_encode_decode_tuple(self):
        """Test encoding and decoding tuple values."""
        # Create tuple type with mixed element types
        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))
        
        test_values = [
            ("Alice", Decimal("30"), True),
            ("Bob", Decimal("25"), False),
            ("", Decimal("0"), False)
        ]
        
        for value in test_values:
            # Create CTY tuple value
            elements = (
                Value(CtyString(), raw_value=value[0]),
                Value(CtyNumber(), raw_value=value[1]),
                Value(CtyBool(), raw_value=value[2])
            )
            cty_value = Value(tuple_type, raw_value=elements)
            
            # Encode to MessagePack
            encoded = await encode_value(cty_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, tuple_type)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == CtyTuple
            
            # Compare the tuple elements
            assert len(decoded.raw_value) == len(elements)
            for i, element in enumerate(elements):
                assert decoded.raw_value[i].raw_value == element.raw_value
    
    @pytest.mark.asyncio
    async def test_encode_decode_dynamic(self):
        """Test encoding and decoding dynamic values."""
        # Create dynamic type
        dynamic_type = CtyDynamic()
        
        test_values = [
            "string value",
            42,
            3.14159,
            True,
            ["list", "of", "values"],
            {"key": "value"},
            None
        ]
        
        for value in test_values:
            # Create CTY dynamic value
            cty_value = Value(dynamic_type, raw_value=value)
            
            # Encode to MessagePack
            encoded = await encode_value(cty_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, dynamic_type)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == CtyDynamic
            
            # Compare the values (with special handling for None)
            if value is None:
                assert decoded.raw_value is None
            else:
                assert decoded.raw_value == value
    
    @pytest.mark.asyncio
    async def test_encode_decode_null_values(self):
        """Test encoding and decoding null values of various types."""
        # Create test types
        string_type = CtyString()
        number_type = CtyNumber()
        bool_type = CtyBool()
        list_type = CtyList(element_type=string_type)
        map_type = CtyMap(key_type=string_type, value_type=number_type)
        
        test_types = [string_type, number_type, bool_type, list_type, map_type]
        
        for type_ in test_types:
            # Create null value
            null_value = Value(type_, is_null=True)
            
            # Encode to MessagePack
            encoded = await encode_value(null_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, type_)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == type_.__class__
            assert decoded.is_null
    
    @pytest.mark.asyncio
    async def test_encode_decode_unknown_values(self):
        """Test encoding and decoding unknown values of various types."""
        # Create test types
        string_type = CtyString()
        number_type = CtyNumber()
        bool_type = CtyBool()
        list_type = CtyList(element_type=string_type)
        map_type = CtyMap(key_type=string_type, value_type=number_type)
        
        test_types = [string_type, number_type, bool_type, list_type, map_type]
        
        for type_ in test_types:
            # Create unknown value
            unknown_value = Value(type_, is_unknown=True)
            
            # Encode to MessagePack
            encoded = await encode_value(unknown_value)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode from MessagePack
            decoded = await decode_value(encoded, type_)
            assert decoded is not None
            assert isinstance(decoded, Value)
            assert decoded.type.__class__ == type_.__class__
            assert not decoded.is_known
    
    @pytest.mark.asyncio
    async def test_encode_decode_marked_values(self):
        """Test encoding and decoding values with marks."""
        # Create string value with marks
        string_type = CtyString()
        string_value = Value(string_type, raw_value="Hello")
        marked_value = string_value.mark("mark1").mark("mark2")
        
        # Encode to MessagePack
        encoded = await encode_value(marked_value)
        assert encoded is not None
        assert isinstance(encoded, bytes)
        
        # Decode from MessagePack
        decoded = await decode_value(encoded, string_type)
        assert decoded is not None
        assert isinstance(decoded, Value)
        assert decoded.type.__class__ == CtyString
        assert decoded.raw_value == "Hello"
        
        # Check marks
        assert decoded.has_mark("mark1")
        assert decoded.has_mark("mark2")
        assert not decoded.has_mark("mark3")
    
    @pytest.mark.asyncio
    async def test_encode_decode_type(self):
        """Test encoding and decoding type definitions."""
        # Create test types
        string_type = CtyString()
        number_type = CtyNumber()
        list_type = CtyList(element_type=string_type)
        map_type = CtyMap(key_type=string_type, value_type=number_type)
        object_type = CtyObject(attribute_types={
            "name": string_type,
            "age": number_type
        })
        
        test_types = [string_type, number_type, list_type, map_type, object_type]
        
        for type_ in test_types:
            # Encode type
            encoded = await encode_type(type_)
            assert encoded is not None
            assert isinstance(encoded, bytes)
            
            # Decode type
            decoded = await decode_type(encoded)
            assert decoded is not None
            assert isinstance(decoded, CtyType)
            assert decoded.__class__ == type_.__class__
            
            # Check additional type properties
            if hasattr(type_, "element_type"):
                assert hasattr(decoded, "element_type")
                assert decoded.element_type.__class__ == type_.element_type.__class__
            
            if hasattr(type_, "key_type") and hasattr(type_, "value_type"):
                assert hasattr(decoded, "key_type")
                assert hasattr(decoded, "value_type")
                assert decoded.key_type.__class__ == type_.key_type.__class__
                assert decoded.value_type.__class__ == type_.value_type.__class__
            
            if hasattr(type_, "attribute_types"):
                assert hasattr(decoded, "attribute_types")
                assert len(decoded.attribute_types) == len(type_.attribute_types)
                for name, attr_type in type_.attribute_types.items():
                    assert name in decoded.attribute_types
                    assert decoded.attribute_types[name].__class__ == attr_type.__class__
    
    @pytest.mark.asyncio
    async def test_marshal_unmarshal_roundtrip(self):
        """Test round-trip marshaling and unmarshaling of CTY values."""
        # Create complex object
        object_type = CtyObject(attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "tags": CtyList(element_type=CtyString()),
            "active": CtyBool(),
            "metadata": CtyMap(key_type=CtyString(), value_type=CtyDynamic())
        })
        
        # Create value
        object_value = {
            "name": Value(CtyString(), raw_value="Alice"),
            "age": Value(CtyNumber(), raw_value=Decimal("30")),
            "tags": Value(CtyList(element_type=CtyString()), raw_value=[
                Value(CtyString(), raw_value="tag1"),
                Value(CtyString(), raw_value="tag2")
            ]),
            "active": Value(CtyBool(), raw_value=True),
            "metadata": Value(CtyMap(key_type=CtyString(), value_type=CtyDynamic()), raw_value={
                Value(CtyString(), raw_value="created"): Value(CtyDynamic(), raw_value="2025-03-09")
            })
        }
        
        cty_value = Value(object_type, raw_value=object_value)
        
        # Marshal to MessagePack
        marshaled = await marshal(cty_value)
        assert marshaled is not None
        assert isinstance(marshaled, bytes)
        
        # Unmarshal from MessagePack
        unmarshaled = await unmarshal(marshaled)
        assert unmarshaled is not None
        assert isinstance(unmarshaled, Value)
        assert unmarshaled.type.__class__ == object_type.__class__
        
        # Check the unmarshaled value matches the original
        unmarshaled_obj = unmarshaled.raw_value
        assert len(unmarshaled_obj) == len(object_value)
        
        assert unmarshaled_obj["name"].raw_value == "Alice"
        assert unmarshaled_obj["age"].raw_value == Decimal("30")
        assert unmarshaled_obj["active"].raw_value is True
        
        assert len(unmarshaled_obj["tags"].raw_value) == 2
        assert unmarshaled_obj["tags"].raw_value[0].raw_value == "tag1"
        assert unmarshaled_obj["tags"].raw_value[1].raw_value == "tag2"
        
        metadata = unmarshaled_obj["metadata"].raw_value
        assert len(metadata) == 1
        
        # Find the metadata key (since dictionaries in Python are unordered)
        found_key = None
        for k in metadata:
            if k.raw_value == "created":
                found_key = k
                break
        
        assert found_key is not None
        assert metadata[found_key].raw_value == "2025-03-09"
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling during encoding and decoding."""
        # Test encoding with invalid value
        string_type = CtyString()
        invalid_value = "Not a Value object"
        
        with pytest.raises(MsgpackEncodeError):
            await encode_value(invalid_value)
        
        # Test decoding with invalid data
        invalid_data = b"Not valid MessagePack data"
        
        with pytest.raises(MsgpackDecodeError):
            await decode_value(invalid_data, string_type)
        
        # Test type mismatch during decoding
        string_value = Value(string_type, raw_value="test")
        encoded = await encode_value(string_value)
        
        # Try to decode as number
        number_type = CtyNumber()
        with pytest.raises(MsgpackDecodeError):
            await decode_value(encoded, number_type)
