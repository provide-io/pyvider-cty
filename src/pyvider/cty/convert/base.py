
# pyvider/cty/convert/base.py

from typing import Optional, Callable, Type
from pyvider.cty import CtyType
from pyvider.cty.values.base import Value

class Conversion:
    """Represents a conversion from one type to another."""
    
    def __init__(self, 
                 source_type: CtyType,
                 target_type: CtyType,
                 converter: Callable[[Value], Value],
                 is_safe: bool = False):
        self.source_type = source_type
        self.target_type = target_type
        self.converter = converter
        self.is_safe = is_safe
    
    def convert(self, value: Value) -> Value:
        """Convert a value from the source type to the target type."""
        return self.converter(value)

# Global conversion registries
_SAFE_CONVERSIONS: dict[tuple[Type[CtyType], Type[CtyType]], Conversion] = {}
_UNSAFE_CONVERSIONS: dict[tuple[Type[CtyType], Type[CtyType]], Conversion] = {}

def register_conversion(source_type: CtyType, 
                        target_type: CtyType, 
                        converter: Callable[[Value], Value],
                        is_safe: bool = False) -> None:
    """Register a conversion."""
    conv = Conversion(source_type, target_type, converter, is_safe)
    key = (type(source_type), type(target_type))
    
    if is_safe:
        _SAFE_CONVERSIONS[key] = conv
    
    _UNSAFE_CONVERSIONS[key] = conv

def get_conversion(source_type: CtyType, target_type: CtyType) -> Optional[Conversion]:
    """Get a safe conversion between types if available."""
    key = (type(source_type), type(target_type))
    return _SAFE_CONVERSIONS.get(key)

def get_conversion_unsafe(source_type: CtyType, target_type: CtyType) -> Optional[Conversion]:
    """Get any conversion between types if available."""
    key = (type(source_type), type(target_type))
    return _UNSAFE_CONVERSIONS.get(key)

def convert(value: Value, target_type: CtyType) -> Value:
    """Convert a value to the target type (safe only)."""
    if value.type.equals(target_type):
        return value
    
    conversion = get_conversion(value.type, target_type)
    if conversion is None:
        raise CtyTypeError(f"Cannot convert from {value.type} to {target_type}")
    
    return conversion.convert(value)

def convert_unsafe(value: Value, target_type: CtyType) -> Value:
    """Convert a value to the target type, allowing unsafe conversions."""
    if value.type.equals(target_type):
        return value
    
    conversion = get_conversion_unsafe(value.type, target_type)
    if conversion is None:
        raise CtyTypeError(f"Cannot convert from {value.type} to {target_type}")
    
    return conversion.convert(value)
