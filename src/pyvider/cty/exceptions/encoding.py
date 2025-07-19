#
# pyvider/cty/exceptions/encoding.py
#
"""
Defines exceptions related to CTY schema transformations, path errors,
and general encoding/serialization processes.
"""

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
        target_type: The intended target type of a transformation, if applicable
    """

    def __init__(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments.
        """
        self.schema = schema
        self.target_type = target_type

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

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

    def __init__(self, message: str, invalid_type: object = None) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
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

    def __init__(self, message: str, path: object = None, value: object = None) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
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

    def __init__(
        self, message: str, data: object = None, encoding: str | None = None
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
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

    def __init__(
        self, message: str, value: object = None, format_name: str | None = None
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
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

    def __init__(
        self, message: str, data: object = None, format_name: str | None = None
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
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

    def __init__(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
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

    def __init__(
        self, message: str, data: object = None, operation: str | None = None
    ) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = self.args[0]
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(
                f"{self.encoding.upper()} encoding error: ", "", 1
            )
            formatted_message = (
                f"{self.encoding.upper()} {operation} error: {base_message}"
            )
            self.args = (formatted_message, *self.args[1:])


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

    def __init__(
        self, message: str, data: object = None, operation: str | None = None
    ) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = self.args[0]
            base_message = current_message.replace(
                f"{self.encoding.upper()} encoding error: ", "", 1
            )
            formatted_message = (
                f"{self.encoding.upper()} {operation} error: {base_message}"
            )
            self.args = (formatted_message, *self.args[1:])


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
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(
            message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type")
        )

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = self.args[0]

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])


# 🐍🏗️🐣
