
# pyvider/cty/encoding/json.py

import json
from typing import Any, Union, Optional

from pyvider.cty import CtyType
from pyvider.cty.values.base import Value

def marshal(val: Value, type_: Optional[CtyType] = None) -> bytes:
    """Marshal a value to JSON with type information."""
    if not val.is_known:
        raise ValueError("Cannot marshal unknown values to JSON")
    
    if val.is_null:
        return b"null"
    
    # Handle different type-specific marshaling
    # Implementation...
    
    # Default fallback
    return json.dumps(val._value).encode('utf-8')

def unmarshal(data: Union[bytes, str], type_: CtyType) -> Value:
    """Unmarshal a JSON value using provided type information."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    try:
        # For null values
        if data == b"null":
            return null_val(type_)
        
        # Parse JSON
        parsed_value = json.loads(data)
        
        # Validate and create value
        validated = type_.validate(parsed_value)
        return Value(type_, validated)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
