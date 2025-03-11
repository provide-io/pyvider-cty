
# pyvider/cty/encoding/protobuf.py

"""
Converts between CTY types and Terraform protobuf type representations.
"""

from typing import Any, Union

from pyvider.telemetry import logger
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyObject, CtyDynamic, CtyTuple

# Type mapping registry
_TYPE_TO_PROTO = {
    CtyString: b'"string"',
    CtyNumber: b'"number"',
    CtyBool: b'"bool"',
    CtyList: b'"list"',
    CtyMap: b'"map"',
    CtySet: b'"set"',
    CtyObject: b'"object"',
    CtyDynamic: b'"dynamic"',
    CtyTuple: b'"tuple"',
}

def get_proto_type(value: Union[CtyType, type, str, bytes]) -> bytes:
    """
    Convert any CTY type reference to its protobuf representation.
    
    Args:
        value: A CtyType instance, class, name, or bytes representation
        
    Returns:
        bytes: Protobuf representation of the type
        
    Raises:
        ValueError: If the type cannot be converted
    """
    logger.debug(f"🧰🔄✅ Converting CTY type to protobuf: {value!r}")
    
    # Handle CtyType instances
    if isinstance(value, CtyType):
        value_type = type(value)
        if value_type in _TYPE_TO_PROTO:
            return _TYPE_TO_PROTO[value_type]
    
    # Handle CtyType classes
    if isinstance(value, type) and issubclass(value, CtyType):
        if value in _TYPE_TO_PROTO:
            return _TYPE_TO_PROTO[value]
    
    # Handle string names
    if isinstance(value, str):
        lowercase = value.lower()
        for cty_type, proto_bytes in _TYPE_TO_PROTO.items():
            type_name = cty_type.__name__.lower()
            if type_name == lowercase or type_name.replace('cty', '') == lowercase:
                return proto_bytes
    
    # Handle bytes (already in protobuf format)
    if isinstance(value, bytes) and value.startswith(b'"') and value.endswith(b'"'):
        return value
        
    # Default to dynamic
    logger.warning(f"🧰🔄⚠️ Unknown type {value!r}, defaulting to dynamic")
    return _TYPE_TO_PROTO[CtyDynamic]
