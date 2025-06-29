# pyvider/cty/exceptions/__init__.py
"""
Exception hierarchy for the pyvider.cty type system.
"""

from pyvider.cty.exceptions.base import CtyError
from pyvider.cty.exceptions.conversion import (
    CtyConversionError,
    CtyTypeConversionError,
    CtyTypeParseError,
)
from pyvider.cty.exceptions.base import CtyFunctionError
from pyvider.cty.exceptions.validation import ( # Ensure these are imported from validation
    CtyCollectionValidationError,
    CtyTypeValidationError,
)
from pyvider.cty.exceptions.encoding import (
    AttributePathError,
    DeserializationError,
    DynamicValueError,
    EncodingError,
    InvalidTypeError,
    JsonEncodingError,
    MsgPackEncodingError,
    SerializationError,
    TransformationError,
    WireFormatError,
)
from pyvider.cty.exceptions.validation import (
    CtyAttributeValidationError,
    CtyBoolValidationError,
    CtyListValidationError,
    CtyMapValidationError,
    CtyNumberValidationError,
    CtySetValidationError,
    CtyStringValidationError,
    CtyTupleValidationError,
    CtyTypeMismatchError,
    CtyValidationError,
)

__all__ = [
    "AttributePathError",
    "CtyAttributeValidationError",
    "CtyBoolValidationError",
    "CtyConversionError",
    "CtyError",
    "CtyFunctionError",
    "CtyCollectionValidationError", # Add to __all__
    "CtyTypeValidationError",     # Add to __all__
    "CtyListValidationError",
    "CtyMapValidationError",
    "CtyNumberValidationError",
    "CtySetValidationError",
    "CtyStringValidationError",
    "CtyTupleValidationError",
    "CtyTypeConversionError",
    "CtyTypeMismatchError",
    "CtyTypeParseError",  # Export the new exception
    "CtyValidationError",
    "DeserializationError",
    "DynamicValueError",
    "EncodingError",
    "InvalidTypeError",
    "JsonEncodingError",
    "MsgPackEncodingError",
    "SerializationError",
    "TransformationError",
    "WireFormatError",
]
