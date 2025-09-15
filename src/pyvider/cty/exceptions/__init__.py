from __future__ import annotations

from pyvider.cty.exceptions.base import CtyError, CtyFunctionError
from pyvider.cty.exceptions.conversion import (
    CtyConversionError,
    CtyTypeConversionError,
    CtyTypeParseError,
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
    CtyCollectionValidationError,
    CtyListValidationError,
    CtyMapValidationError,
    CtyNumberValidationError,
    CtySetValidationError,
    CtyStringValidationError,
    CtyTupleValidationError,
    CtyTypeMismatchError,
    CtyTypeValidationError,
    CtyValidationError,
)

"""
Exception hierarchy for the pyvider.cty type system.
"""

__all__ = [
    "AttributePathError",
    "CtyAttributeValidationError",
    "CtyBoolValidationError",
    "CtyCollectionValidationError",
    "CtyConversionError",
    "CtyError",
    "CtyFunctionError",
    "CtyListValidationError",
    "CtyMapValidationError",
    "CtyNumberValidationError",
    "CtySetValidationError",
    "CtyStringValidationError",
    "CtyTupleValidationError",
    "CtyTypeConversionError",
    "CtyTypeMismatchError",
    "CtyTypeParseError",
    "CtyTypeValidationError",
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
