# pyvider/cty/convert/primitive.py

from pyvider.cty.values.base import Value
from pyvider.cty.convert.base import register_conversion
from pyvider.cty.types import CtyString, CtyNumber

# String to number conversion (unsafe)
def string_to_number(value: Value) -> Value:
    """Convert a string value to a number value."""
    if not value.is_known:
        return unknown_val(Number())
    
    if value.is_null:
        return null_val(Number())
    
    try:
        num_val = Decimal(value._value)
        return Value(Number(), num_val, marks=value._marks)
    except (ValueError, DecimalException):
        raise ValueError(f"Cannot convert string '{value._value}' to number")

# Register conversions
register_conversion(CtyString(), CtyNumber(), string_to_number, is_safe=False)
