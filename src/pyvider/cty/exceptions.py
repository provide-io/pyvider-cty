# pyvider/cty/exceptions.py
#
# pyvider/cty/exceptions.py
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

Applications using pyvider.cty should catch these exceptions specifically
rather than catching generic Python exceptions to properly handle
type-related errors.
"""

from typing import Any, Optional, Union


class CtyError(Exception):
    """
    Base exception for all pyvider.cty errors.

    This is the root exception for all errors that occur within the cty type
    system. It provides a foundation for more specific error types and can
    be used to catch any cty-related error.

    Attributes:
        message: A human-readable error description
    """
    def __init__(self, message: str = "An error occurred in the cty type system"):
        self.message = message
        super().__init__(self.message)


class PyviderError(CtyError):
    """
    Legacy error for backward compatibility.

    This exception is maintained for backward compatibility with older code
    that might catch PyviderError instead of CtyError. New code should use
    CtyError and its subclasses.

    Attributes:
        message: A human-readable error description
    """
    def __init__(self, message: str = "An error occurred in the Pyvider system"):
        super().__init__(message)


################################################################################
# Validation Errors
################################################################################

class CtyValidationError(CtyError):
    """
    Base exception for all validation errors.

    Raised when a value fails validation against a type's constraints. This
    serves as the parent class for more specific validation errors related
    to particular types.

    Attributes:
        message: A human-readable error description
        value: The value that failed validation (if available)
        type_name: The name of the type that validation was attempted against
    """
    def __init__(self, message: str, value: Any = None, type_name: Optional[str] = None):
        self.value = value
        self.type_name = type_name

        # Add type and value information to the message if available
        if type_name is not None:
            message = f"{type_name} validation error: {message}"

        super().__init__(message)


class CtyBoolValidationError(CtyValidationError):
    """
    Raised when a value cannot be validated as a boolean.

    This exception occurs when a value cannot be converted to or used as a
    boolean value according to CtyBool's validation rules. For example, it
    might be raised when attempting to validate a complex object as a boolean.

    Args:
        message: A human-readable error description
        value: The value that failed validation
    """
    def __init__(self, message: str, value: Any = None):
        super().__init__(message, value, "Boolean")


class CtyNumberValidationError(CtyValidationError):
    """
    Raised when a value cannot be validated as a number.

    This exception occurs when a value cannot be converted to or used as a
    numeric value according to CtyNumber's validation rules. It might be raised
    for invalid numeric strings, complex objects, or values that would lose
    precision during conversion.

    Args:
        message: A human-readable error description
        value: The value that failed validation
    """
    def __init__(self, message: str, value: Any = None):
        super().__init__(message, value, "Number")


class CtyStringValidationError(CtyValidationError):
    """
    Raised when a value cannot be validated as a string.

    This exception occurs when a value cannot be converted to or used as a
    string according to CtyString's validation rules. While many values can
    be converted to strings, this might be raised for complex objects with no
    clear string representation.

    Args:
        message: A human-readable error description
        value: The value that failed validation
    """
    def __init__(self, message: str, value: Any = None):
        super().__init__(message, value, "String")


class CtyListValidationError(CtyValidationError):
    """
    Raised when a value cannot be validated as a list.

    This exception occurs when a list validation fails. This could happen if:
    - The input is not a list-like object
    - One or more elements fail validation against the element_type
    - The list operation (append, slice, etc.) is invalid

    Args:
        message: A human-readable error description
        value: The value that failed validation
        index: Optional index where validation failed (for element validation)
    """
    def __init__(self, message: str, value: Any = None, index: Optional[int] = None):
        self.index = index

        # Add index information to the message if available
        if index is not None:
            message = f"At index {index}: {message}"

        super().__init__(message, value, "List")


class CtyMapValidationError(CtyValidationError):
    """
    Raised when a value cannot be validated as a map.

    This exception occurs when map validation fails. This could happen if:
    - The input is not a dict-like object
    - Keys or values fail validation against their respective types
    - Map operations (get, set, delete) are invalid

    Args:
        message: A human-readable error description
        value: The value that failed validation
        key: Optional key where validation failed
    """
    def __init__(self, message: str, value: Any = None, key: Optional[Any] = None):
        self.key = key

        # Add key information to the message if available
        if key is not None:
            message = f"For key '{key}': {message}"

        super().__init__(message, value, "Map")


class CtySetValidationError(CtyValidationError):
    """
    Raised when a value cannot be validated as a set.

    This exception occurs when set validation fails. This could happen if:
    - The input is not a set-like object
    - One or more elements fail validation against the element_type
    - The set operation (add, remove, etc.) is invalid

    Args:
        message: A human-readable error description
        value: The value that failed validation
    """
    def __init__(self, message: str, value: Any = None):
        super().__init__(message, value, "Set")


class CtyTypeMismatchError(CtyValidationError):
    """
    Raised when there is a type mismatch during validation.

    This exception indicates that a value's type doesn't match the expected
    type during validation, often occurring when checking type compatibility
    or when validating nested structures.

    Args:
        message: A human-readable error description
        actual_type: The actual type encountered
        expected_type: The type that was expected
    """
    def __init__(self, message: str, actual_type: Any = None, expected_type: Any = None):
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type information to the message if available
        if actual_type is not None and expected_type is not None:
            type_info = f"Expected {expected_type}, got {actual_type}"
            message = f"{message} ({type_info})"

        super().__init__(message)


class CtyAttributeValidationError(CtyValidationError):
    """
    Raised when an object attribute fails validation.

    This exception occurs during validation of object attributes, such as:
    - When an attribute is missing but required
    - When an attribute has an invalid value
    - When accessing an attribute that doesn't exist

    Args:
        message: A human-readable error description
        attribute_name: The name of the attribute that failed validation
        value: The value that failed validation
    """
    def __init__(self, message: str, attribute_name: Optional[str] = None, value: Any = None):
        self.attribute_name = attribute_name

        # Add attribute information to the message if available
        if attribute_name is not None:
            message = f"Attribute '{attribute_name}': {message}"

        super().__init__(message, value, "Object")


################################################################################
# Transformation and Path Errors
################################################################################

class TransformationError(CtyError):
    """
    Raised when a schema transformation fails.

    This exception occurs when a schema cannot be transformed from one
    representation to another, such as during conversion between different
    schema formats or when applying schema transformations.

    Attributes:
        message: A human-readable error description
        schema: The schema that failed transformation
    """
    def __init__(self, message: str, schema: Any = None):
        self.schema = schema
        super().__init__(message)


class InvalidTypeError(CtyError):
    """
    Raised when an invalid type is used in a type definition.

    This exception occurs when attempting to create a type with invalid
    parameters or constraints, such as using a non-CtyType instance when
    a CtyType is required.

    Attributes:
        message: A human-readable error description
        invalid_type: The invalid type that caused the error
    """
    def __init__(self, message: str, invalid_type: Any = None):
        self.invalid_type = invalid_type
        super().__init__(message)


class AttributePathError(CtyError):
    """
    Raised when there's an error with an attribute path.

    This exception occurs when a path operation fails, such as:
    - When a path cannot be applied to a value
    - When a path step refers to a non-existent attribute or index
    - When a path operation is applied to an incompatible value type

    Attributes:
        message: A human-readable error description
        path: The path that caused the error
        value: The value the path was being applied to
    """
    def __init__(self, message: str, path: Any = None, value: Any = None):
        self.path = path
        self.value = value
        super().__init__(message)


################################################################################
# Encoding Errors
################################################################################

class EncodingError(CtyError):
    """
    Base exception for all encoding/serialization errors.

    This exception serves as the parent class for more specific errors
    related to serialization and deserialization of Cty values.

    Attributes:
        message: A human-readable error description
        data: The data that caused the encoding error
    """
    def __init__(self, message: str, data: Any = None):
        self.data = data
        super().__init__(message)


class SerializationError(EncodingError):
    """
    Raised when serialization of a value fails.

    This exception occurs when a Cty value cannot be serialized to a
    particular format, such as when a value contains types that aren't
    supported by the serialization format.

    Attributes:
        message: A human-readable error description
        value: The value that failed to serialize
        format_name: The name of the format that was being used
    """
    def __init__(self, message: str, value: Any = None, format_name: Optional[str] = None):
        self.value = value
        self.format_name = format_name

        # Add format information to the message if available
        if format_name is not None:
            message = f"{format_name} serialization error: {message}"

        super().__init__(message, value)


class DeserializationError(EncodingError):
    """
    Raised when deserialization of data fails.

    This exception occurs when serialized data cannot be converted back into
    a Cty value, such as when the data is corrupt or in an incompatible format.

    Attributes:
        message: A human-readable error description
        data: The data that failed to deserialize
        format_name: The name of the format that was being used
    """
    def __init__(self, message: str, data: Any = None, format_name: Optional[str] = None):
        self.format_name = format_name

        # Add format information to the message if available
        if format_name is not None:
            message = f"{format_name} deserialization error: {message}"

        super().__init__(message, data)


class DynamicValueError(SerializationError):
    """
    Raised when there's an error encoding or decoding a DynamicValue.

    This exception is specific to the handling of dynamic values in
    serialization contexts, where type information might be unknown
    or ambiguous.

    Attributes:
        message: A human-readable error description
        value: The dynamic value that caused the error
    """
    def __init__(self, message: str, value: Any = None):
        super().__init__(message, value, "DynamicValue")


class ConversionError(CtyError):
    """
    Raised when type conversion fails.

    This exception occurs when a value cannot be converted from one type
    to another, such as when attempting to convert between incompatible
    types or when conversion would result in data loss.

    Attributes:
        message: A human-readable error description
        source_type: The source type in the conversion
        target_type: The target type in the conversion
        value: The value that failed conversion
    """
    def __init__(
        self,
        message: str,
        source_type: Optional[Any] = None,
        target_type: Optional[Any] = None,
        value: Any = None
    ):
        self.source_type = source_type
        self.target_type = target_type
        self.value = value

        # Add type information to the message if available
        if source_type is not None and target_type is not None:
            message = f"Cannot convert {source_type} to {target_type}: {message}"

        super().__init__(message)

# 🐍🏗️🐣
