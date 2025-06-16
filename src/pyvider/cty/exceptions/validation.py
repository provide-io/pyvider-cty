#
# pyvider/cty/exceptions/validation.py
#

from pyvider.cty.exceptions.base import CtyError


class CtyError(Exception):
    """
    Base exception for all pyvider.cty errors.

    This is the root exception for all errors that occur within the cty type
    system. It provides a foundation for more specific error types and can
    be used to catch any cty-related error.

    Attributes:
        message: A human-readable error description
    """
    def __init__(self, message: str = "An error occurred in the cty type system") -> None:
        self.message = message
        super().__init__(self.message)

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
    def __init__(self, message: str, value: object = None, type_name: str | None = None) -> None:
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
    def __init__(self, message: str, value: object = None) -> None:
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
    def __init__(self, message: str, value: object = None) -> None:
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
    def __init__(self, message: str, value: object = None) -> None:
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
    def __init__(self, message: str, value: object = None, index: int | None = None) -> None:
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
    def __init__(self, message: str, value: object = None, key: object | None = None) -> None:
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
    def __init__(self, message: str, value: object = None) -> None:
        super().__init__(message, value, "Set")

class CtyTupleValidationError(CtyValidationError):
    def __init__(self, message: str, value: object = None) -> None:
        super().__init__(message, value, "Tuple")

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
    def __init__(self, message: str, actual_type: object = None, expected_type: object = None) -> None:
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
    def __init__(self, message: str, attribute_name: str | None = None, value: object = None) -> None:
        self.attribute_name = attribute_name

        # Add attribute information to the message if available
        if attribute_name is not None:
            message = f"Attribute '{attribute_name}': {message}"

        super().__init__(message, value, "Object")

# 🐍🏗️🐣
