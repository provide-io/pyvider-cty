# pyvider/cty/exceptions.py

from typing import Any, Optional

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

class CapsuleError(CtyError):
    """Base exception for capsule-related errors."""
    pass


class CapsuleTypeError(CapsuleError):
    """Raised when a capsule type is invalid or incompatible."""
    
    def __init__(self, message: str, capsule_type: Optional['CtyCapsule'] = None):
        self.capsule_type = capsule_type
        super().__init__(message)


class CapsuleValueError(CapsuleError):
    """Raised when a capsule value is invalid or incompatible."""
    
    def __init__(self, message: str, value: Any = None, capsule_type: Optional['CtyCapsule'] = None):
        self.value = value
        self.capsule_type = capsule_type
        super().__init__(message)


class CapsuleSerializationError(CapsuleError, SerializationError):
    """Raised when capsule serialization fails."""
    pass


class CapsuleDeserializationError(CapsuleError, DeserializationError):
    """Raised when capsule deserialization fails."""
    pass