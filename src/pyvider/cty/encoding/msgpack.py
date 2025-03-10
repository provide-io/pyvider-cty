
# pyvider/cty/encoding/msgpack.py

import msgpack
from typing import Any, Optional
from pyvider_cty.types.base import Type
from pyvider_cty.values.base import Value

def marshal(val: Value, type_: Optional[Type] = None) -> bytes:
    """Marshal a value to MsgPack with type information."""
    if not val.is_known:
        # Special encoding for unknown values
        return msgpack.packb({
            "unknown": True,
            "type": _encode_type(val.type)
        })
    
    if val.is_null:
        return msgpack.packb(None)
    
    # Implement type-specific marshaling
    # ...
    
    # Default marshaling
    return msgpack.packb(val._value)

def unmarshal(data: bytes, type_: Type) -> Value:
    """Unmarshal a MsgPack value using provided type information."""
    try:
        unpacked = msgpack.unpackb(data)
        
        # Handle special cases
        if unpacked is None:
            return null_val(type_)
        
        if isinstance(unpacked, dict) and unpacked.get("unknown"):
            return unknown_val(type_)
        
        # Normal value
        validated = type_.validate(unpacked)
        return Value(type_, validated)
    except (msgpack.exceptions.UnpackException, TypeError) as e:
        raise ValueError(f"Invalid MsgPack data: {e}")
