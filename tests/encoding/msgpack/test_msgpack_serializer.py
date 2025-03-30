#!/usr/bin/env python3
# tests/encoding/test_msgpack_serializer.py

"""
Specific tests for the MessagePack serializer.

This test suite focuses on MessagePack-specific serialization details,
extension types, format handling, and edge cases that are unique to MessagePack.
"""

import pytest
import msgpack
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
    MsgpackSerializer,
)
from pyvider.cty.encoding.msgpack_serializer import (
    CtyType,
    EXT_UNKNOWN,
    EXT_NULL,
    EXT_MARKED,
    EXT_TYPE_HINT,
    EXT_OBJECT,
    EXT_TUPLE,
    EXT_SET,
    CTY_MAGIC_BYTES,
)


class TestMsgpackSerializer:
    """Tests specific to the MessagePack serializer."""
    
    @pytest.mark.asyncio
    async def test_msgpack_format_detection(self):
        """Test MessagePack format detection."""
        serializer = MsgpackSerializer()
        
        # Valid MessagePack formats
        assert serializer.supports_format(CTY_MAGIC_BYTES + b'data')  # Magic bytes
        assert serializer.supports_format(msgpack.packb({"key": "value"}))
        assert serializer.supports_format(msgpack.packb([1, 2, 3]))
        assert serializer.supports_format(msgpack.packb("string"))
        assert serializer.supports_format(msgpack.packb(123))
        assert serializer.supports_format(msgpack.packb(True))
        assert serializer.supports_format(msgpack.packb(False))
        assert serializer.supports_format(msgpack.packb(None))
        
        # Invalid formats
        assert not serializer.supports_format(b'')
        assert not serializer.supports_format(b'invalid msgpack')
        assert not serializer.supports_format(b'{"invalid":"json"}')
    
    @pytest.mark.asyncio
    async def test_msgpack_typed_format(self):
        """Test the MessagePack typed format structure."""
        serializer = MsgpackSerializer()
        
        # Create a simple value
        string_value = CtyValue(CtyString(), "test")
        
        # Serialize with type
        serialized = serializer.serialize_with_type(string_value.value, string_value.type)
        
        # Skip magic bytes
        if serialized.startswith(CTY_MAGIC_BYTES):
            serialized = serialized[len(CTY_MAGIC_BYTES):]
        
        # Unpack the MessagePack data
        parsed = msgpack.unpackb(serialized)
        
        # Check structure
        assert "type" in parsed
        assert "value" in parsed
        assert msgpack.unpackb(parsed["type"]) == "string"
        assert parsed["value"] == "test"
    
    @pytest.mark.asyncio
    async def test_msgpack_unknown_value_format(self):
        """Test the MessagePack format for unknown values."""
        serializer = MsgpackSerializer()
        
        # Create an unknown value
        unknown_string = CtyValue(CtyString(), is_unknown=True)
        
        # Serialize
        serialized = serializer.serialize(unknown_string)
        
        # Skip magic bytes
        if serialized.startswith(CTY_MAGIC_BYTES):
            serialized = serialized[len(CTY_MAGIC_BYTES):]
        
        # Unpack the MessagePack data
        parsed = msgpack.unpackb(serialized)
        
        # Check if it's an extension type
        assert isinstance(parsed, msgpack.ExtType)
        assert parsed.code == EXT_UNKNOWN
        
        # Unpack the extension data
        ext_data = msgpack.unpackb(parsed.data)
        assert isinstance(ext_data, str)
        assert ext_data == "string"  # Type name
    
    @pytest.mark.asyncio
    async def test_msgpack_null_value_format(self):
        """Test the MessagePack format for null values."""
        serializer = MsgpackSerializer()
        
        # Create a null value
        null_string = CtyValue(CtyString(), is_null=True)
        
        # Serialize
        serialized = serializer.serialize(null_string)
        
        # Skip magic bytes
        if serialized.startswith(CTY_MAGIC_BYTES):
            serialized = serialized[len(CTY_MAGIC_BYTES):]
        
        # Unpack the MessagePack data
        parsed = msgpack.unpackb(serialized)
        
        # Check if it's an extension type
        assert isinstance(parsed, msgpack.ExtType)
        assert parsed.code == EXT_NULL
        
        # Unpack the extension data
        ext_data = msgpack.unpackb(parsed.data)
        assert isinstance(ext_data, str)
        assert ext_data == "string"  # Type name
    

    @pytest.mark.asyncio
    async def test_msgpack_extension_types(self):
        """Test MessagePack extension types for complex data structures."""
        serializer = MsgpackSerializer()
        
        # Create values that use extension types
        
        # Tuple
        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber()))
        tuple_value = CtyValue(tuple_type, (
            "test",  # Use raw values instead of CtyValue
            42
        ))
        
        # Set
        set_type = CtySet(element_type=CtyString())
        set_value = CtyValue(set_type, {
            "one",  # Use raw values instead of CtyValue 
            "two",
            "three"
        })
        
        # Object
        object_type = CtyObject(attribute_types={
            "name": CtyString(),
            "value": CtyNumber()
        })
        object_value = CtyValue(object_type, {
            "name": "test",  # Use raw values instead of CtyValue
            "value": 42
        })

        # Serialize each value
        tuple_serialized = serializer.serialize(tuple_value)
        set_serialized = serializer.serialize(set_value)
        object_serialized = serializer.serialize(object_value)
        
        # Skip magic bytes
        if tuple_serialized.startswith(CTY_MAGIC_BYTES):
            tuple_serialized = tuple_serialized[len(CTY_MAGIC_BYTES):]
        if set_serialized.startswith(CTY_MAGIC_BYTES):
            set_serialized = set_serialized[len(CTY_MAGIC_BYTES):]
        if object_serialized.startswith(CTY_MAGIC_BYTES):
            object_serialized = object_serialized[len(CTY_MAGIC_BYTES):]
        
        # Extract extension types
        tuple_ext = None
        set_ext = None
        object_ext = None
        
        # Helper function to find extension type in a MessagePack value
        def find_ext_type(value, target_code):
            if isinstance(value, msgpack.ExtType):
                if value.code == target_code:
                    return value
            elif isinstance(value, dict):
                for k, v in value.items():
                    result = find_ext_type(v, target_code)
                    if result:
                        return result
            elif isinstance(value, list):
                for item in value:
                    result = find_ext_type(item, target_code)
                    if result:
                        return result
            return None
        
        # Unpack and find extension types
        tuple_data = msgpack.unpackb(tuple_serialized)
        tuple_ext = find_ext_type(tuple_data, EXT_TUPLE)
        
        set_data = msgpack.unpackb(set_serialized)
        set_ext = find_ext_type(set_data, EXT_SET)
        
        object_data = msgpack.unpackb(object_serialized)
        object_ext = find_ext_type(object_data, EXT_OBJECT)
        
        # Check if extension types were found
        assert tuple_ext is not None
        assert set_ext is not None
        assert object_ext is not None
        
        # Check extension type codes
        assert tuple_ext.code == EXT_TUPLE
        assert set_ext.code == EXT_SET
        assert object_ext.code == EXT_OBJECT
        
        # Check extension data
        tuple_ext_data = msgpack.unpackb(tuple_ext.data)
        assert isinstance(tuple_ext_data, list)
        assert len(tuple_ext_data) == 2
        
        set_ext_data = msgpack.unpackb(set_ext.data)
        assert isinstance(set_ext_data, list)
        assert len(set_ext_data) == 3
        
        object_ext_data = msgpack.unpackb(object_ext.data)
        assert isinstance(object_ext_data, dict)
        assert "name" in object_ext_data
        assert "value" in object_ext_data
    
    @pytest.mark.asyncio
    async def test_msgpack_marshal_format(self):
        """Test the MessagePack marshal format structure."""
        # Create a simple value
        string_value = CtyValue(CtyString(), "test")
        
        # Marshal
        marshaled = marshal(string_value)
        
        # Skip magic bytes
        if marshaled.startswith(CTY_MAGIC_BYTES):
            marshaled = marshaled[len(CTY_MAGIC_BYTES):]
        
        # Unpack the marshaled data
        parsed = msgpack.unpackb(marshaled)
        
        # Check structure
        assert "type" in parsed
        assert "is_known" in parsed
        assert "is_null" in parsed
        assert "value" in parsed
        
        assert parsed["is_known"] is True
        assert parsed["is_null"] is False
        
        # Check type
        type_name = msgpack.unpackb(parsed["type"])
        assert type_name.startswith("Cty")
    
    @pytest.mark.asyncio
    async def test_msgpack_marshal_unknown_value(self):
        """Test marshaling an unknown value."""
        # Create an unknown value
        unknown_string = CtyValue(CtyString(), is_unknown=True)
        
        # Marshal
        marshaled = marshal(unknown_string)
        
        # Skip magic bytes
        if marshaled.startswith(CTY_MAGIC_BYTES):
            marshaled = marshaled[len(CTY_MAGIC_BYTES):]
        
        # Unpack the marshaled data
        parsed = msgpack.unpackb(marshaled)
        
        # Check structure
        assert "type" in parsed
        assert "is_known" in parsed
        assert parsed["is_known"] is False
        
        # Value should not be present for unknown values
        assert "value" not in parsed
    
    @pytest.mark.asyncio
    async def test_msgpack_marshal_null_value(self):
        """Test marshaling a null value."""
        # Create a null value
        null_string = CtyValue(CtyString(), is_null=True)
        
        # Marshal
        marshaled = marshal(null_string)
        
        # Skip magic bytes
        if marshaled.startswith(CTY_MAGIC_BYTES):
            marshaled = marshaled[len(CTY_MAGIC_BYTES):]
        
        # Unpack the marshaled data
        parsed = msgpack.unpackb(marshaled)
        
        # Check structure
        assert "type" in parsed
        assert "is_null" in parsed
        assert parsed["is_null"] is True
        
        # Value should not be present for null values
        assert "value" not in parsed
    
    @pytest.mark.asyncio
    async def test_msgpack_marshal_marked_value(self):
        """Test marshaling a marked value."""
        # Create a marked value
        marked_string = CtyValue(CtyString(), "test").mark("mark1").mark("mark2")
        
        # Marshal
        marshaled = marshal(marked_string)
        
        # Skip magic bytes
        if marshaled.startswith(CTY_MAGIC_BYTES):
            marshaled = marshaled[len(CTY_MAGIC_BYTES):]
        
        # Unpack the marshaled data
        parsed = msgpack.unpackb(marshaled)
        
        # Check structure
        assert "type" in parsed
        assert "is_known" in parsed
        assert "is_null" in parsed
        assert "value" in parsed
        assert "marks" in parsed
        
        assert parsed["is_known"] is True
        assert parsed["is_null"] is False
        
        # Check marks
        assert "mark1" in parsed["marks"]
        assert "mark2" in parsed["marks"]
    
    @pytest.mark.asyncio
    async def test_msgpack_primitive_values(self):
        """Test MessagePack handling of primitive values."""
        serializer = MsgpackSerializer()
        
        # Test cases for primitive values
        primitive_values = [
            (CtyString(), "test string"),
            (CtyString(), ""),  # Empty string
            (CtyString(), "Special chars: ñáéíóú"),  # Unicode
            (CtyNumber(), 42),
            (CtyNumber(), -42),
            (CtyNumber(), 3.14159),
            (CtyNumber(), Decimal("123456789.987654321")),
            (CtyNumber(), 0),
            (CtyBool(), True),
            (CtyBool(), False),
        ]
        
        for type_obj, value in primitive_values:
            # Create Cty value
            cty_value = CtyValue(type_obj, value)
            
            # Serialize
            serialized = serializer.serialize(cty_value)
            
            # Deserialize
            deserialized = serializer.deserialize(serialized)
            
            # Check type and value
            assert isinstance(deserialized, CtyValue)
            assert deserialized.type.__class__ == type_obj.__class__
            
            # For number values, compare as Decimal to handle precision
            if isinstance(value, (int, float, Decimal)):
                assert Decimal(str(deserialized.value)) == Decimal(str(value))
            else:
                assert deserialized.value == value
    
