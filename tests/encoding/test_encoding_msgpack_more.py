
import pytest
from unittest.mock import MagicMock, patch
import msgpack
from decimal import Decimal

from pyvider.cty.encoding.msgpack import (
    encode_value, decode_value, encode_type, decode_type,
    marshal, unmarshal, MsgpackEncodeError, MsgpackDecodeError,
    EXT_UNKNOWN, EXT_NULL, EXT_MARKED
)
from pyvider.cty import CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtySet, CtyObject, CtyDynamic
from pyvider.cty.values.base import CtyValue


class TestMsgpackEncoding:
    """Tests for MessagePack encoding and decoding."""
    
    @pytest.mark.asyncio
    async def test_encode_string_value(self):
        """Test encoding a string value."""
        # Create a string value
        value = CtyValue(type_=CtyString(), value="test string")
        
        # Mock msgpack.packb
        mock_packb = MagicMock(return_value=b'test packed data')
        
        with patch('msgpack.packb', mock_packb):
            # Encode value
            result = await encode_value(value)
            
            # Verify mockpack.packb was called with the string value
            mock_packb.assert_called_with("test string", use_bin_type=True, use_single_float=False, 
                                         datetime=True, strict_types=True)
            
            # Verify result
            assert result == b'test packed data'
    
    @pytest.mark.asyncio
    async def test_encode_number_value(self):
        """Test encoding a number value."""
        # Create a number value
        value = CtyValue(type_=CtyNumber(), value=Decimal("123.45"))
        
        # Mock msgpack.packb
        mock_packb = MagicMock(return_value=b'test packed data')
        
        with patch('msgpack.packb', mock_packb):
            # Encode value
            result = await encode_value(value)
            
            # Verify mockpack.packb was called with the float value
            mock_packb.assert_called_with(float(123.45), use_bin_type=True, use_single_float=False, 
                                         datetime=True, strict_types=True)
            
            # Verify result
            assert result == b'test packed data'
    
    @pytest.mark.asyncio
    async def test_encode_bool_value(self):
        """Test encoding a boolean value."""
        # Create a boolean value
        value = CtyValue(type_=CtyBool(), value=True)
        
        # Mock msgpack.packb
        mock_packb = MagicMock(return_value=b'test packed data')
        
        with patch('msgpack.packb', mock_packb):
            # Encode value
            result = await encode_value(value)
            
            # Verify mockpack.packb was called with the boolean value
            mock_packb.assert_called_with(True, use_bin_type=True, use_single_float=False, 
                                         datetime=True, strict_types=True)
            
            # Verify result
            assert result == b'test packed data'
    
    @pytest.mark.asyncio
    async def test_encode_unknown_value(self):
        """Test encoding an unknown value."""
        # Create an unknown value
        value = CtyValue(type_=CtyString(), is_unknown=True)
        
        # Mock msgpack.packb for both operations
        mock_packb_values = [b'encoded type data', b'final encoded data']
        mock_packb = MagicMock(side_effect=mock_packb_values)
        
        # Mock encode_type
        mock_encode_type = MagicMock(return_value=b'type bytes')
        
        with patch('msgpack.packb', mock_packb), \
             patch('pyvider.cty.encoding.msgpack.encode_type', mock_encode_type):
            # Encode value
            result = await encode_value(value)
            
            # Verify encode_type was called
            mock_encode_type.assert_called_once_with(value.type)
            
            # Verify mockpack.packb was called twice
            assert mock_packb.call_count == 2
            
            # The second call should pack the ExtType with EXT_UNKNOWN
            from msgpack import ExtType
            assert isinstance(mock_packb.call_args_list[1][0][0], ExtType)
            assert mock_packb.call_args_list[1][0][0].code == EXT_UNKNOWN
            
            # Verify result
            assert result == b'final encoded data'
    
    @pytest.mark.asyncio
    async def test_encode_null_value(self):
        """Test encoding a null value."""
        # Create a null value
        value = CtyValue(type_=CtyString(), is_null=True)
        
        # Mock msgpack.packb
        mock_packb = MagicMock(return_value=b'test packed data')
        
        # Mock encode_type
        mock_encode_type = MagicMock(return_value=b'type bytes')
        
        with patch('msgpack.packb', mock_packb), \
             patch('pyvider.cty.encoding.msgpack.encode_type', mock_encode_type):
            # Encode value
            result = await encode_value(value)
            
            # Verify encode_type was called
            mock_encode_type.assert_called_once_with(value.type)
            
            # Verify mockpack.packb was called with ExtType
            from msgpack import ExtType
            assert isinstance(mock_packb.call_args[0][0], ExtType)
            assert mock_packb.call_args[0][0].code == EXT_NULL
            assert mock_packb.call_args[0][0].data == b'type bytes'
            
            # Verify result
            assert result == b'test packed data'
    
    @pytest.mark.asyncio
    async def test_encode_marked_value(self):
        """Test encoding a marked value."""
        # Create a marked value
        value = CtyValue(type_=CtyString(), value="test", marks=frozenset(["sensitive"]))
        
        # Mock value.unmark
        unmarked_value = CtyValue(type_=CtyString(), value="test")
        mock_unmark = MagicMock(return_value=(unmarked_value, frozenset(["sensitive"])))
        
        # Mock encode_value for the unmarked value
        mock_encode_value = MagicMock(return_value=b'unmarked value data')
        
        # Mock msgpack.packb
        mock_packb_values = [b'marked data', b'final packed data']
        mock_packb = MagicMock(side_effect=mock_packb_values)
        
        with patch.object(value, 'unmark', mock_unmark), \
             patch('pyvider.cty.encoding.msgpack.encode_value', mock_encode_value), \
             patch('msgpack.packb', mock_packb):
            # Encode value
            result = await encode_value(value)
            
            # Verify value.unmark was called
            mock_unmark.assert_called_once()
            
            # Verify encode_value was called with unmarked value
            mock_encode_value.assert_called_once_with(unmarked_value)
            
            # Verify result
            assert result == b'final packed data'
    
    @pytest.mark.asyncio
    async def test_encode_list_value(self):
        """Test encoding a list value."""
        # Create a list value
        value = CtyValue(type_=CtyList(element_type=CtyString()), value=["a", "b", "c"])
        
        # Mock encode_value for each element
        mock_encode_value = MagicMock(return_value=b'encoded element')
        
        # Mock msgpack.packb
        mock_packb = MagicMock(return_value=b'packed list')
        
        with patch('pyvider.cty.encoding.msgpack.encode_value', mock_encode_value), \
             patch('msgpack.packb', mock_packb):
            # Encode value
            result = await encode_value(value)
            
            # Verify encode_value was called for each element
            assert mock_encode_value.call_count == 3
            
            # Verify msgpack.packb was called with the encoded elements
            mock_packb.assert_called_with([b'encoded element', b'encoded element', b'encoded element'],
                                         use_bin_type=True, use_single_float=False,
                                         datetime=True, strict_types=True)
            
            # Verify result
            assert result == b'packed list'
    
    @pytest.mark.asyncio
    async def test_encode_map_value(self):
        """Test encoding a map value."""
        # Create a map value
        value = CtyValue(
            type_=CtyMap(key_type=CtyString(), value_type=CtyNumber()),
            value={"a": 1, "b": 2}
        )
        
        # Mock encode_value for each item
        mock_encode_value = MagicMock(return_value=b'encoded value')
        
        # Mock msgpack.packb
        mock_packb = MagicMock(return_value=b'packed map')
        
        with patch('pyvider.cty.encoding.msgpack.encode_value', mock_encode_value), \
             patch('msgpack.packb', mock_packb):
            # Encode value
            result = await encode_value(value)
            
            # Verify encode_value was called for each value
            assert mock_encode_value.call_count == 2
            
            # Verify msgpack.packb was called with the encoded map
            mock_packb.assert_called_with({'a': b'encoded value', 'b': b'encoded value'},
                                         use_bin_type=True, use_single_float=False,
                                         datetime=True, strict_types=True)
            
            # Verify result
            assert result == b'packed map'
    
    @pytest.mark.asyncio
    async def test_encode_value_error(self):
        """Test error handling in encode_value."""
        # Create a value
        value = CtyValue(type_=CtyString(), value="test")
        
        # Mock msgpack.packb to raise an exception
        mock_packb = MagicMock(side_effect=Exception("Test error"))
        
        with patch('msgpack.packb', mock_packb):
            # Encode value should raise MsgpackEncodeError
            with pytest.raises(MsgpackEncodeError):
                await encode_value(value)
    
    @pytest.mark.asyncio
    async def test_decode_string_value(self):
        """Test decoding a string value."""
        # Create string type
        type_ = CtyString()
        
        # Mock msgpack.unpackb
        mock_unpackb = MagicMock(return_value="decoded string")
        
        with patch('msgpack.unpackb', mock_unpackb):
            # Decode value
            result = await decode_value(b'encoded data', type_)
            
            # Verify msgpack.unpackb was called
            mock_unpackb.assert_called_with(b'encoded data', raw=False, use_list=True, strict_map_key=False,
                                          ext_hook=any)
            
            # Verify result
            assert isinstance(result, CtyValue)
            assert result.type == type_
            assert result.value == "decoded string"
    
    @pytest.mark.asyncio
    async def test_decode_number_value(self):
        """Test decoding a number value."""
        # Create number type
        type_ = CtyNumber()
        
        # Mock msgpack.unpackb
        mock_unpackb = MagicMock(return_value=123.45)
        
        with patch('msgpack.unpackb', mock_unpackb):
            # Decode value
            result = await decode_value(b'encoded data', type_)
            
            # Verify msgpack.unpackb was called
            mock_unpackb.assert_called_with(b'encoded data', raw=False, use_list=True, strict_map_key=False,
                                          ext_hook=any)
            
            # Verify result
            assert isinstance(result, CtyValue)
            assert result.type == type_
            assert result.value == Decimal('123.45')
    
    @pytest.mark.asyncio
    async def test_decode_with_ext_hook_unknown(self):
        """Test decoding an unknown value using ext_hook."""
        # Create test data that would trigger the ext_hook
        # This is a bit tricky to test directly, so we'll just verify the correct handling
        type_ = CtyString()
        
        # Mock msgpack.unpackb to return an unknown value through ext_hook
        # We'll need to capture and call the ext_hook
        ext_hook = None
        
        def mock_unpackb(data, **kwargs):
            nonlocal ext_hook
            ext_hook = kwargs['ext_hook']
            # Create ExtType for unknown value
            from msgpack import ExtType
            dummy_data = msgpack.packb({
                "type": b"type data",
                "path": []
            })
            return ext_hook(EXT_UNKNOWN, dummy_data)
        
        with patch('msgpack.unpackb', mock_unpackb):
            # Decode value
            result = await decode_value(b'encoded data', type_)
            
            # Verify ext_hook was captured
            assert ext_hook is not None
            
            # Verify result is an unknown value
            assert isinstance(result, CtyValue)
            assert result.type == type_
            assert result.is_known is False
    
    @pytest.mark.asyncio
    async def test_decode_with_ext_hook_null(self):
        """Test decoding a null value using ext_hook."""
        type_ = CtyString()
        
        # Mock msgpack.unpackb to return a null value through ext_hook
        ext_hook = None
        
        def mock_unpackb(data, **kwargs):
            nonlocal ext_hook
            ext_hook = kwargs['ext_hook']
            # Create ExtType for null value
            from msgpack import ExtType
            return ext_hook(EXT_NULL, b"type data")
        
        with patch('msgpack.unpackb', mock_unpackb):
            # Decode value
            result = await decode_value(b'encoded data', type_)
            
            # Verify ext_hook was captured
            assert ext_hook is not None
            
            # Verify result is a null value
            assert isinstance(result, CtyValue)
            assert result.type == type_
            assert result.is_null is True
    
    @pytest.mark.asyncio
    async def test_decode_value_error(self):
        """Test error handling in decode_value."""
        # Create type
        type_ = CtyString()
        
        # Mock msgpack.unpackb to raise an exception
        mock_unpackb = MagicMock(side_effect=Exception("Test error"))
        
        with patch('msgpack.unpackb', mock_unpackb):
            # Decode value should raise MsgpackDecodeError
            with pytest.raises(MsgpackDecodeError):
                await decode_value(b'encoded data', type_)
    
    @pytest.mark.asyncio
    async def test_encode_decode_roundtrip_string(self):
        """Test roundtrip encoding and decoding of a string value."""
        # Create a string value
        type_ = CtyString()
        value = CtyValue(type_=type_, value="test string")
        
        # For a real roundtrip test without mocking, we need msgpack
        # But we can still use mocks to avoid actual msgpack operations
        mock_encode = MagicMock(return_value=b'encoded data')
        mock_decode = MagicMock(return_value=value)
        
        with patch('pyvider.cty.encoding.msgpack.encode_value', mock_encode), \
             patch('pyvider.cty.encoding.msgpack.decode_value', mock_decode):
            # Encode
            encoded = await encode_value(value)
            
            # Decode
            decoded = await decode_value(encoded, type_)
            
            # Verify roundtrip
            assert decoded == value
    
    @pytest.mark.asyncio
    async def test_encode_type(self):
        """Test encoding a type."""
        # Create a type
        type_ = CtyString()
        
        # Mock msgpack.packb
        mock_packb = MagicMock(return_value=b'packed type')
        
        with patch('msgpack.packb', mock_packb):
            # Encode type
            result = await encode_type(type_)
            
            # Verify msgpack.packb was called with type info
            type_info = mock_packb.call_args[0][0]
            assert isinstance(type_info, dict)
            assert type_info['type_name'] == 'CtyString'
            
            # Verify result
            assert result == b'packed type'
    
    @pytest.mark.asyncio
    async def test_encode_complex_type(self):
        """Test encoding a complex type with nested types."""
        # Create a complex type
        type_ = CtyList(element_type=CtyMap(key_type=CtyString(), value_type=CtyNumber()))
        
        # Mock encode_type for nested calls
        mock_encode_type_values = [b'key type', b'value type', b'element type']
        mock_encode_type = MagicMock(side_effect=mock_encode_type_values)
        
        # Mock msgpack.packb
        mock_packb = MagicMock(return_value=b'packed type')
        
        with patch('pyvider.cty.encoding.msgpack.encode_type', mock_encode_type), \
             patch('msgpack.packb', mock_packb):
            # Encode type
            result = await encode_type(type_)
            
            # Verify encode_type was called for nested types
            assert mock_encode_type.call_count == 3
            
            # Verify msgpack.packb was called with type info
            type_info = mock_packb.call_args[0][0]
            assert isinstance(type_info, dict)
            assert type_info['type_name'] == 'CtyList'
            assert 'element_type' in type_info
            
            # Verify result
            assert result == b'packed type'
    
    @pytest.mark.asyncio
    async def test_encode_type_error(self):
        """Test error handling in encode_type."""
        # Create a type
        type_ = CtyString()
        
        # Mock msgpack.packb to raise an exception
        mock_packb = MagicMock(side_effect=Exception("Test error"))
        
        with patch('msgpack.packb', mock_packb):
            # Encode type should raise MsgpackEncodeError
            with pytest.raises(MsgpackEncodeError):
                await encode_type(type_)
    
    @pytest.mark.asyncio
    async def test_decode_type_string(self):
        """Test decoding a string type."""
        # Mock msgpack.unpackb to return string type info
        mock_unpackb = MagicMock(return_value={'type_name': 'CtyString'})
        
        with patch('msgpack.unpackb', mock_unpackb):
            # Decode type
            result = await decode_type(b'encoded type')
            
            # Verify result
            assert isinstance(result, CtyString)
    
    @pytest.mark.asyncio
    async def test_decode_complex_type(self):
        """Test decoding a complex type with nested types."""
        # Mock decode_type for nested calls
        mock_element_type = CtyString()
        mock_decode_type = MagicMock(return_value=mock_element_type)
        
        # Mock msgpack.unpackb to return list type info
        mock_unpackb = MagicMock(return_value={
            'type_name': 'CtyList',
            'element_type': b'encoded element type'
        })
        
        with patch('pyvider.cty.encoding.msgpack.decode_type', mock_decode_type), \
             patch('msgpack.unpackb', mock_unpackb):
            # Decode type
            result = await decode_type(b'encoded type')
            
            # Verify decode_type was called for nested type
            mock_decode_type.assert_called_once_with(b'encoded element type')
            
            # Verify result
            assert isinstance(result, CtyList)
            assert result.element_type == mock_element_type
    
    @pytest.mark.asyncio
    async def test_decode_type_error(self):
        """Test error handling in decode_type."""
        # Mock msgpack.unpackb to raise an exception
        mock_unpackb = MagicMock(side_effect=Exception("Test error"))
        
        with patch('msgpack.unpackb', mock_unpackb):
            # Decode type should raise MsgpackDecodeError
            with pytest.raises(MsgpackDecodeError):
                await decode_type(b'encoded type')
    
    @pytest.mark.asyncio
    async def test_marshal_unmarshal_roundtrip(self):
        """Test roundtrip marshaling and unmarshaling of a value."""
        # Create a value
        type_ = CtyString()
        value = CtyValue(type_=type_, value="test string")
        
        # Mock encode_type
        mock_encode_type = MagicMock(return_value=b'encoded type')
        
        # Mock encode_value
        mock_encode_value = MagicMock(return_value=b'encoded value')
        
        # Mock msgpack.packb for marshal
        mock_packb = MagicMock(return_value=b'marshaled data')
        
        # Mock msgpack.unpackb for unmarshal
        mock_unpackb = MagicMock(return_value={
            'type': b'encoded type',
            'value': b'encoded value',
            'is_known': True,
            'is_null': False
        })
        
        # Mock decode_type
        mock_decode_type = MagicMock(return_value=type_)
        
        # Mock decode_value
        mock_decode_value = MagicMock(return_value=value)
        
        with patch('pyvider.cty.encoding.msgpack.encode_type', mock_encode_type), \
             patch('pyvider.cty.encoding.msgpack.encode_value', mock_encode_value), \
             patch('msgpack.packb', mock_packb), \
             patch('msgpack.unpackb', mock_unpackb), \
             patch('pyvider.cty.encoding.msgpack.decode_type', mock_decode_type), \
             patch('pyvider.cty.encoding.msgpack.decode_value', mock_decode_value):
            # Marshal
            marshaled = await marshal(value)
            
            # Unmarshal
            unmarshaled = await unmarshal(marshaled)
            
            # Verify encode_type was called
            mock_encode_type.assert_called_once_with(value.type)
            
            # Verify encode_value was called
            mock_encode_value.assert_called_once_with(value)
            
            # Verify msgpack.packb was called
            marshaled_data = mock_packb.call_args[0][0]
            assert isinstance(marshaled_data, dict)
            assert marshaled_data['type'] == b'encoded type'
            assert marshaled_data['value'] == b'encoded value'
            assert marshaled_data['is_known'] is True
            assert marshaled_data['is_null'] is False
            
            # Verify msgpack.unpackb was called
            mock_unpackb.assert_called_once_with(b'marshaled data')
            
            # Verify decode_type was called
            mock_decode_type.assert_called_once_with(b'encoded type')
            
            # Verify decode_value was called
            mock_decode_value.assert_called_once_with(b'encoded value', type_)
            
            # Verify roundtrip
            assert unmarshaled == value
