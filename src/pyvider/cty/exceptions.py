# pyvider/cty/exceptions.py

from typing import Any, Optional

"""
Exceptions for the pyvider.cty module.

This module contains all the exceptions that can be raised by the pyvider.cty
module, keeping them separate from the main pyvider.cty.exceptions module.
"""

class PyviderError(Exception):
    pass

class CtyError(Exception):
    """Base exception for all pyvider.cty errors."""
    pass


################################################################################
# Validation Errors
#
class CtyValidationError(CtyError):
    pass

class CtyBoolValidationError(CtyValidationError):
    pass

class CtyNumberValidationError(CtyValidationError):
    pass

class CtyStringValidationError(CtyValidationError):
    pass

class CtyListValidationError(CtyValidationError):
    pass

class CtyMapValidationError(CtyValidationError):
    pass

class CtyTypeMismatchError(CtyValidationError):
    pass

class CtyAttributeValidationError(CtyValidationError):
    pass

#
################################################################################

class TransformationError(CtyError):
    """Raised when a schema fails validation."""
    pass

class InvalidTypeError(CtyError):
    """Raised when an invalid type is used in a type definition."""
    pass


class EncodingError(CtyError):
    """Raised when serialization or deserialization fails."""
    pass

class SerializationError(EncodingError):
    """Raised when serialization or deserialization fails."""
    pass

class DeserializationError(EncodingError):
    """Raised when serialization or deserialization fails."""
    pass

class AttributePathError(CtyError):
    """Raised when there's an error with an attribute path."""
    pass

class PyviderError(CtyError):
    """Legacy error for backward compatibility."""
    pass

class DynamicValueError(SerializationError):
    """Raised when there's an error encoding or decoding a DynamicValue."""
    pass


class ConversionError(CtyError):
    """Raised when type conversion fails."""
    pass
