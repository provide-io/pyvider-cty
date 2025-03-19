# pyvider/cty/convert/primitive.py

from pyvider.cty.convert.base import register_conversion
from pyvider.cty.ctypes import CtyString, CtyNumber
from pyvider.cty.values import CtyValue

# String to number conversion (unsafe)
def string_to_number(value: CtyValue) -> CtyValue:
    """Convert a string value to a number value."""
    if not value.is_known:
        return unknown_val(Number())
    
    if value.is_null:
        return null_val(Number())
    
    try:
        num_val = Decimal(value._value)
        return CtyValue(Number(), num_val, marks=value._marks)
    except (ValueError, DecimalException):
        raise ValueError(f"Cannot convert string '{value._value}' to number")

# Register conversions
register_conversion(CtyString(), CtyNumber(), string_to_number, is_safe=False)
