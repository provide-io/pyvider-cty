#
# pyvider/cty/exceptions/encoding.py
#

from typing import Optional

from pyvider.cty.exceptions.base import CtyError

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
    def __init__(self, message: str, schema: object = None):
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
    def __init__(self, message: str, invalid_type: object = None):
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
    def __init__(self, message: str, path: object = None, value: object = None):
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
        encoding: The name of the encoding format that was being used
    """
    def __init__(self, message: str, data: object = None, encoding: str | None = None):
        self.data = data
        self.encoding = encoding

        # Add format information to the message if available
        if encoding is not None:
            message = f"{encoding.upper()} encoding error: {message}"

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
    def __init__(self, message: str, value: object = None, format_name: str | None = None):
        self.value = value
        super().__init__(message, value, format_name)


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
    def __init__(self, message: str, data: object = None, format_name: str | None = None):
        super().__init__(message, data, format_name)


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
    def __init__(self, message: str, value: object = None):
        super().__init__(message, value, "DynamicValue")


class JsonEncodingError(EncodingError):
    """
    Raised when JSON encoding or decoding fails.

    This exception provides specific context for JSON serialization errors,
    including details about the specific JSON operation that failed.

    Attributes:
        message: A human-readable error description
        data: The data that caused the encoding error
        operation: The operation that failed (encode/decode)
    """
    def __init__(self, message: str, data: object = None, operation: str | None = None):
        self.operation = operation

        # Add operation context to the message
        if operation:
            message = f"JSON {operation} error: {message}"

        super().__init__(message, data, "json")


class MsgPackEncodingError(EncodingError):
    """
    Raised when MessagePack encoding or decoding fails.

    This exception provides specific context for MessagePack serialization errors,
    including details about the specific MessagePack operation that failed.

    Attributes:
        message: A human-readable error description
        data: The data that caused the encoding error
        operation: The operation that failed (encode/decode)
    """
    def __init__(self, message: str, data: object = None, operation: str | None = None):
        self.operation = operation

        # Add operation context to the message
        if operation:
            message = f"MessagePack {operation} error: {message}"

        super().__init__(message, data, "msgpack")


class WireFormatError(TransformationError):
    """
    Raised when wire format encoding or decoding fails.

    This exception is specific to the wire format system and provides
    additional context about the operation that failed.

    Attributes:
        message: A human-readable error description
        format_type: The wire format type that encountered an error
        operation: The operation that failed (marshal/unmarshal)
    """
    def __init__(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs
    ):
        self.format_type = format_type
        self.operation = operation

        # Format a more detailed message including the format type
        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            message = f"{message}{format_info}"

        super().__init__(message, **kwargs)


# 🐍🏗️🐣
