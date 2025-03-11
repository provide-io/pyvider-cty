
# pyvider/cty/encoding/msgpack.py

"""
MessagePack encoder/decoder for CTY values.

This module provides functions to serialize CTY values to MessagePack format
and deserialize MessagePack data to CTY values. MessagePack is used by Terraform
as a compact binary serialization format for its DynamicValue protocol buffer messages.

MessagePack encoding preserves CTY type information and special values like null and unknown,
allowing for precise round-trip serialization.
"""

import asyncio
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

import msgpack
from msgpack import ExtType

from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyBool, CtyNumber, CtyString
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyDynamic, CtyObject, CtyTuple
from pyvider.cty.values.base import Value

# Extension type codes for special CTY value representations
EXT_UNKNOWN = 0
EXT_NULL = 1
EXT_MARKED = 2
EXT_TYPE_PATH = 3

# Default encoder/decoder options
DEFAULT_ENCODE_OPTIONS = {
    "use_bin_type": True,
    "use_single_float": False,
    "datetime": True,
    "strict_types": True,
}

DEFAULT_DECODE_OPTIONS = {
    "raw": False,
    "use_list": True,
    "strict_map_key": False,
}


class MsgpackEncodeError(Exception):
    """Error during MessagePack encoding of a CTY value."""
    pass


class MsgpackDecodeError(Exception):
    """Error during MessagePack decoding to a CTY value."""
    pass


async def encode_value(value: Value, options: Optional[Dict[str, Any]] = None) -> bytes:
    """
    Encode a CTY value to MessagePack format.
    
    Args:
        value: The CTY value to encode
        options: Optional MessagePack encoding options
        
    Returns:
        bytes: MessagePack encoded data
        
    Raises:
        MsgpackEncodeError: If encoding fails
    """
    logger.debug(f"🧮📤🔄 Encoding CTY value to MessagePack: {value}")
    
    # Merge with default options
    opts = {**DEFAULT_ENCODE_OPTIONS}
    if options:
        opts.update(options)
    
    try:
        # Special handling for unknown and null values
        if not value.is_known:
            logger.debug("🧮📤ℹ️ Encoding unknown value")
            type_bytes = await encode_type(value.type)
            ext_data = msgpack.packb({
                "type": type_bytes,
                "path": []  # For future path support
            })
            return msgpack.packb(ExtType(EXT_UNKNOWN, ext_data), **opts)
        
        if value.is_null:
            logger.debug("🧮📤ℹ️ Encoding null value")
            type_bytes = await encode_type(value.type)
            return msgpack.packb(ExtType(EXT_NULL, type_bytes), **opts)
        
        # Handle marked values
        if value.marks:
            logger.debug(f"🧮📤ℹ️ Encoding marked value with {len(value.marks)} marks")
            unmarked_value, marks = value.unmark()
            data = {
                "value": await encode_value(unmarked_value),
                "marks": [str(mark) for mark in marks]
            }
            return msgpack.packb(ExtType(EXT_MARKED, msgpack.packb(data)), **opts)
        
        # Type-specific encoding
        type_name = type(value.type).__name__
        
        # Primitive types
        if type_name == "CtyString":
            return msgpack.packb(value.raw_value, **opts)
        
        elif type_name == "CtyNumber":
            # Ensure numbers are encoded as ints when possible
            if isinstance(value.raw_value, Decimal):
                if value.raw_value == value.raw_value.to_integral_value():
                    return msgpack.packb(int(value.raw_value), **opts)
            return msgpack.packb(float(value.raw_value), **opts)
        
        elif type_name == "CtyBool":
            return msgpack.packb(bool(value.raw_value), **opts)
        
        # Collection types
        elif type_name == "CtyList":
            elements = []
            for element in value.raw_value:
                element_data = await encode_value(element)
                elements.append(element_data)
            return msgpack.packb(elements, **opts)
        
        elif type_name == "CtyMap":
            items = {}
            for key, val in value.raw_value.items():
                key_str = str(key)  # Keys must be strings in MessagePack
                val_data = await encode_value(val)
                items[key_str] = val_data
            return msgpack.packb(items, **opts)
        
        elif type_name == "CtySet":
            elements = []
            for element in value.raw_value:
                element_data = await encode_value(element)
                elements.append(element_data)
            # Sets are encoded as arrays with special marker
            return msgpack.packb({
                "_cty_set": True,
                "elements": elements
            }, **opts)
        
        # Structural types
        elif type_name == "CtyObject":
            attributes = {}
            for attr_name, attr_val in value.raw_value.items():
                attr_data = await encode_value(attr_val)
                attributes[attr_name] = attr_data
            return msgpack.packb(attributes, **opts)
        
        elif type_name == "CtyTuple":
            elements = []
            for element in value.raw_value:
                element_data = await encode_value(element)
                elements.append(element_data)
            # Tuples are encoded as arrays with special marker
            return msgpack.packb({
                "_cty_tuple": True,
                "elements": elements
            }, **opts)
        
        # Dynamic values - let MessagePack determine format
        elif type_name == "CtyDynamic":
            return msgpack.packb(value.raw_value, **opts)
        
        # Unknown type
        else:
            logger.warning(f"🧮📤⚠️ Unknown CTY type: {type_name}, using default encoding")
            return msgpack.packb(value.raw_value, **opts)
    
    except Exception as e:
        error_msg = f"Failed to encode CTY value: {e}"
        logger.error(f"🧮📤❌ {error_msg}", exc_info=True)
        raise MsgpackEncodeError(error_msg) from e


async def decode_value(data: bytes, type_: Union[CtyType, Type[CtyType]], options: Optional[Dict[str, Any]] = None) -> Value:
    """
    Decode MessagePack data to a CTY value.
    
    Args:
        data: MessagePack encoded data
        type_: The CTY type to decode as
        options: Optional MessagePack decoding options
        
    Returns:
        Value: The decoded CTY value
        
    Raises:
        MsgpackDecodeError: If decoding fails
    """
    logger.debug(f"🧮📥🔄 Decoding MessagePack data to {type_.__class__.__name__}")
    
    # Merge with default options
    opts = {**DEFAULT_DECODE_OPTIONS}
    if options:
        opts.update(options)
    
    # Ensure we have a type instance, not a class
    if isinstance(type_, type) and issubclass(type_, CtyType):
        type_ = type_()
    
    # Custom extension type handler
    def ext_hook(code, data):
        if code == EXT_UNKNOWN:
            logger.debug("🧮📥ℹ️ Decoding unknown value")
            return Value(type_, is_unknown=True)
        
        elif code == EXT_NULL:
            logger.debug("🧮📥ℹ️ Decoding null value")
            return Value(type_, is_null=True)
        
        elif code == EXT_MARKED:
            logger.debug("🧮📥ℹ️ Decoding marked value")
            marked_data = msgpack.unpackb(data)
            inner_value = asyncio.run(decode_value(marked_data["value"], type_))
            for mark in marked_data["marks"]:
                inner_value = inner_value.mark(mark)
            return inner_value
        
        # Return raw data for unknown extension types
        return ExtType(code, data)
    
    opts["ext_hook"] = ext_hook
    
    try:
        # Unpack data
        raw_value = msgpack.unpackb(data, **opts)
        
        # Special handling for set and tuple
        if isinstance(raw_value, dict):
            if raw_value.get("_cty_set"):
                logger.debug("🧮📥ℹ️ Decoding set value")
                elements = raw_value["elements"]
                element_type = type_.element_type
                set_values = set()
                for element_data in elements:
                    element_val = await decode_value(element_data, element_type)
                    set_values.add(element_val)
                return Value(type_, raw_value=set_values)
            
            elif raw_value.get("_cty_tuple"):
                logger.debug("🧮📥ℹ️ Decoding tuple value")
                elements = raw_value["elements"]
                tuple_types = type_.element_types
                tuple_values = []
                for i, element_data in enumerate(elements):
                    element_type = tuple_types[i] if i < len(tuple_types) else CtyDynamic()
                    element_val = await decode_value(element_data, element_type)
                    tuple_values.append(element_val)
                return Value(type_, raw_value=tuple(tuple_values))
        
        # Type-specific decoding
        type_name = type_.__class__.__name__
        
        # Primitive types
        if type_name == "CtyString":
            return Value(type_, raw_value=str(raw_value))
        
        elif type_name == "CtyNumber":
            if isinstance(raw_value, int):
                return Value(type_, raw_value=Decimal(raw_value))
            return Value(type_, raw_value=Decimal(str(raw_value)))
        
        elif type_name == "CtyBool":
            return Value(type_, raw_value=bool(raw_value))
        
        # Collection types
        elif type_name == "CtyList":
            element_type = type_.element_type
            elements = []
            for element_data in raw_value:
                element_val = await decode_value(msgpack.packb(element_data, **DEFAULT_ENCODE_OPTIONS), element_type)
                elements.append(element_val)
            return Value(type_, raw_value=elements)
        
        elif type_name == "CtyMap":
            key_type = type_.key_type
            value_type = type_.value_type
            items = {}
            for key_str, val_data in raw_value.items():
                # MessagePack requires string keys
                key_val = await decode_value(msgpack.packb(key_str, **DEFAULT_ENCODE_OPTIONS), key_type)
                val_val = await decode_value(msgpack.packb(val_data, **DEFAULT_ENCODE_OPTIONS), value_type)
                items[key_val] = val_val
            return Value(type_, raw_value=items)
        
        # Structural types
        elif type_name == "CtyObject":
            attributes = {}
            for attr_name, attr_data in raw_value.items():
                attr_type = type_.attribute_types.get(attr_name, CtyDynamic())
                attr_val = await decode_value(msgpack.packb(attr_data, **DEFAULT_ENCODE_OPTIONS), attr_type)
                attributes[attr_name] = attr_val
            return Value(type_, raw_value=attributes)
        
        # Dynamic - directly use the raw value
        elif type_name == "CtyDynamic":
            return Value(type_, raw_value=raw_value)
        
        # Default handling
        return Value(type_, raw_value=raw_value)
    
    except Exception as e:
        error_msg = f"Failed to decode MessagePack data: {e}"
        logger.error(f"🧮📥❌ {error_msg}", exc_info=True)
        raise MsgpackDecodeError(error_msg) from e


async def encode_type(type_: CtyType) -> bytes:
    """
    Encode a CTY type definition to MessagePack.
    
    Args:
        type_: The CTY type to encode
        
    Returns:
        bytes: MessagePack encoded type definition
    """
    logger.debug(f"🧮📤🔄 Encoding type: {type_.__class__.__name__}")
    
    try:
        type_info = {
            "type_name": type_.__class__.__name__
        }
        
        # Include additional type information
        if hasattr(type_, "element_type"):
            type_info["element_type"] = await encode_type(type_.element_type)
        
        if hasattr(type_, "key_type") and hasattr(type_, "value_type"):
            type_info["key_type"] = await encode_type(type_.key_type)
            type_info["value_type"] = await encode_type(type_.value_type)
        
        if hasattr(type_, "attribute_types"):
            attr_types = {}
            for name, attr_type in type_.attribute_types.items():
                attr_types[name] = await encode_type(attr_type)
            type_info["attribute_types"] = attr_types
        
        if hasattr(type_, "element_types"):
            element_types = []
            for elem_type in type_.element_types:
                element_types.append(await encode_type(elem_type))
            type_info["element_types"] = element_types
        
        return msgpack.packb(type_info, **DEFAULT_ENCODE_OPTIONS)
    
    except Exception as e:
        error_msg = f"Failed to encode type: {e}"
        logger.error(f"🧮📤❌ {error_msg}", exc_info=True)
        raise MsgpackEncodeError(error_msg) from e


async def decode_type(data: bytes) -> CtyType:
    """
    Decode MessagePack data to a CTY type.
    
    Args:
        data: MessagePack encoded type definition
        
    Returns:
        CtyType: The decoded CTY type
        
    Raises:
        MsgpackDecodeError: If decoding fails
    """
    logger.debug("🧮📥🔄 Decoding type from MessagePack")
    
    try:
        type_info = msgpack.unpackb(data, **DEFAULT_DECODE_OPTIONS)
        type_name = type_info["type_name"]
        
        # Import the required types
        if type_name == "CtyString":
            return CtyString()
        
        elif type_name == "CtyNumber":
            return CtyNumber()
        
        elif type_name == "CtyBool":
            return CtyBool()
        
        elif type_name == "CtyList":
            element_type = await decode_type(type_info["element_type"])
            return CtyList(element_type=element_type)
        
        elif type_name == "CtyMap":
            key_type = await decode_type(type_info["key_type"])
            value_type = await decode_type(type_info["value_type"])
            return CtyMap(key_type=key_type, value_type=value_type)
        
        elif type_name == "CtySet":
            element_type = await decode_type(type_info["element_type"])
            return CtySet(element_type=element_type)
        
        elif type_name == "CtyObject":
            attribute_types = {}
            for name, type_data in type_info["attribute_types"].items():
                attribute_types[name] = await decode_type(type_data)
            return CtyObject(attribute_types=attribute_types)
        
        elif type_name == "CtyTuple":
            element_types = []
            for type_data in type_info["element_types"]:
                element_types.append(await decode_type(type_data))
            return CtyTuple(element_types=tuple(element_types))
        
        elif type_name == "CtyDynamic":
            return CtyDynamic()
        
        else:
            logger.warning(f"🧮📥⚠️ Unknown type: {type_name}, returning dynamic")
            return CtyDynamic()
    
    except Exception as e:
        error_msg = f"Failed to decode type: {e}"
        logger.error(f"🧮📥❌ {error_msg}", exc_info=True)
        raise MsgpackDecodeError(error_msg) from e


async def marshal(val: Value, opts: Optional[Dict[str, Any]] = None) -> bytes:
    """
    Marshal a CTY value to MessagePack with type information.
    
    This is a more comprehensive version of encode_value that includes
    type information, allowing for accurate round-trip serialization.
    
    Args:
        val: The CTY value to marshal
        opts: Optional MessagePack encoding options
        
    Returns:
        bytes: MessagePack encoded data
    """
    logger.debug(f"🧮📤🔄 Marshaling CTY value: {val}")
    
    try:
        # Create a marshaled representation with type and value
        marshaled = {
            "type": await encode_type(val.type),
            "value": await encode_value(val, opts),
            "is_known": val.is_known,
            "is_null": val.is_null,
        }
        
        # Include marks if present
        if val.marks:
            marshaled["marks"] = [str(mark) for mark in val.marks]
        
        return msgpack.packb(marshaled, **(opts or DEFAULT_ENCODE_OPTIONS))
    
    except Exception as e:
        error_msg = f"Failed to marshal value: {e}"
        logger.error(f"🧮📤❌ {error_msg}", exc_info=True)
        raise MsgpackEncodeError(error_msg) from e


async def unmarshal(data: bytes, opts: Optional[Dict[str, Any]] = None) -> Value:
    """
    Unmarshal MessagePack data to a CTY value.
    
    This is the counterpart to marshal() and handles both type and value
    information for complete deserialization.
    
    Args:
        data: MessagePack encoded data
        opts: Optional MessagePack decoding options
        
    Returns:
        Value: The unmarshaled CTY value
    """
    logger.debug("🧮📥🔄 Unmarshaling CTY value from MessagePack")
    
    try:
        # Decode the marshaled data
        marshaled = msgpack.unpackb(data, **(opts or DEFAULT_DECODE_OPTIONS))
        
        # Extract type and value information
        type_ = await decode_type(marshaled["type"])
        is_known = marshaled.get("is_known", True)
        is_null = marshaled.get("is_null", False)
        
        # Create value based on special states
        if not is_known:
            value = Value(type_, is_unknown=True)
        elif is_null:
            value = Value(type_, is_null=True)
        else:
            value = await decode_value(marshaled["value"], type_, opts)
        
        # Apply marks if present
        if "marks" in marshaled:
            for mark in marshaled["marks"]:
                value = value.mark(mark)
        
        return value
    
    except Exception as e:
        error_msg = f"Failed to unmarshal value: {e}"
        logger.error(f"🧮📥❌ {error_msg}", exc_info=True)
        raise MsgpackDecodeError(error_msg) from e
