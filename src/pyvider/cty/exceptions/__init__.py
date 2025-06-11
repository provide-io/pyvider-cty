#
# pyvider/cty/exceptions/__init__.py
#

"""
Exception hierarchy for the pyvider.cty type system.

This module defines the comprehensive exception hierarchy used throughout the
pyvider.cty package. Each exception provides specific error information,
making it easier to diagnose problems during type validation, conversion,
serialization, and other operations.

The exception hierarchy is structured to reflect the subsystems of the cty
package:
- Base exceptions (CtyError)
- Validation exceptions (CtyValidationError and subtypes)
- Encoding exceptions (EncodingError and subtypes)
- Transformation and path exceptions
"""

from pyvider.cty.exceptions.base import CtyError

from pyvider.cty.exceptions.validation import (
    CtyError,
    CtyValidationError,
    CtyBoolValidationError,
    CtyNumberValidationError,
    CtyStringValidationError,
    CtyListValidationError,
    CtyMapValidationError,
    CtySetValidationError,
    CtyTupleValidationError,
    CtyTypeMismatchError,
    CtyAttributeValidationError,
)

from pyvider.cty.exceptions.conversion import (
    CtyConversionError
)

from pyvider.cty.exceptions.encoding import (
    TransformationError,
    InvalidTypeError,
    AttributePathError,
    EncodingError,
    SerializationError,
    DeserializationError,
    DynamicValueError,
    JsonEncodingError,
    MsgPackEncodingError,
    WireFormatError,
)

__all__ = [
    "CtyError",
    "CtyValidationError",
    "CtyBoolValidationError",
    "CtyNumberValidationError",
    "CtyStringValidationError",
    "CtyListValidationError",
    "CtyMapValidationError",
    "CtySetValidationError",
    "CtyTupleValidationError",
    "CtyTypeMismatchError",
    "CtyAttributeValidationError",

    "CtyConversionError",

    "TransformationError",
    "InvalidTypeError",
    "AttributePathError",
    "EncodingError",
    "SerializationError",
    "DeserializationError",
    "DynamicValueError",
    "JsonEncodingError",
    "MsgPackEncodingError",
    "WireFormatError",
]

