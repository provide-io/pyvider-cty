# pyvider/cty/exceptions.py

"""
Exceptions for the pyvider.cty module.

This module contains all the exceptions that can be raised by the pyvider.cty
module, keeping them separate from the main pyvider.cty.exceptions module.
"""

class CtyError(Exception):
    """Base exception for all pyvider.cty errors."""
    pass


class ValidationError(CtyError):
    """Raised when a value fails type validation."""
    pass


class TypeMismatchError(ValidationError):
    """Raised when a value doesn't match the expected type."""
    pass


class AttributeValidationError(ValidationError):
    """Raised when an attribute fails validation in an object."""
    pass


class SchemaValidationError(ValidationError):
    """Raised when a schema fails validation."""
    pass


class InvalidTypeError(CtyError):
    """Raised when an invalid type is used in a type definition."""
    pass


class SerializationError(CtyError):
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
