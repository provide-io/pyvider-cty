
# pyvider/cty/encoding/exceptions.py

"""
Exception hierarchy for Cty serialization.

This module defines a comprehensive set of exceptions for handling
serialization and deserialization errors with appropriate context
and detailed error messages.
"""

from typing import Any, Optional, Type


class SerializationError(Exception):
    """Base exception for all serialization-related errors."""
    
    def __init__(
        self, 
        message: str, 
        value: Optional[Any] = None, 
        *args, 
        **kwargs
    ) -> None:
        """
        Initialize with context about the serialization operation.
        
        Args:
            message: Error message
            value: The value that caused the error (if available)
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.value = value
        value_str = f" (value: {repr(value)[:100]})" if value is not None else ""
        super().__init__(f"{message}{value_str}", *args, **kwargs)


class DeserializationError(Exception):
    """Base exception for all deserialization-related errors."""
    
    def __init__(
        self, 
        message: str, 
        data: Optional[bytes] = None,
        format_name: Optional[str] = None,
        *args, 
        **kwargs
    ) -> None:
        """
        Initialize with context about the deserialization operation.
        
        Args:
            message: Error message
            data: The raw bytes that caused the error (if available)
            format_name: The serialization format being used (if known)
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.data = data
        self.format_name = format_name
        
        # Add context to the message
        context = []
        if format_name:
            context.append(f"format: {format_name}")
        if data:
            # Safely show a preview of the data, handling potentially large binary data
            try:
                data_preview = data[:20].decode('utf-8', errors='backslashreplace')
                if len(data) > 20:
                    data_preview += "..."
                context.append(f"data: {data_preview}")
            except Exception:
                context.append(f"data: {repr(data[:20])}...")
                
        context_str = f" ({', '.join(context)})" if context else ""
        super().__init__(f"{message}{context_str}", *args, **kwargs)


class UnsupportedTypeError(SerializationError):
    """Raised when attempting to serialize an unsupported type."""
    
    def __init__(
        self, 
        value_type: Type, 
        format_name: Optional[str] = None, 
        value: Optional[Any] = None,
        *args, 
        **kwargs
    ) -> None:
        """
        Initialize with information about the unsupported type.
        
        Args:
            value_type: The type that couldn't be serialized
            format_name: The serialization format being used (if known)
            value: The value that caused the error (if available)
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.value_type = value_type
        format_info = f" in {format_name} format" if format_name else ""
        super().__init__(
            f"Cannot serialize type {value_type.__name__}{format_info}", 
            value, 
            *args, 
            **kwargs
        )


class TypeMismatchError(DeserializationError):
    """Raised when deserialized data doesn't match the expected type."""
    
    def __init__(
        self, 
        expected_type: Type, 
        actual_type: Type, 
        *args, 
        **kwargs
    ) -> None:
        """
        Initialize with information about the type mismatch.
        
        Args:
            expected_type: The type that was expected
            actual_type: The type that was actually found
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.expected_type = expected_type
        self.actual_type = actual_type
        super().__init__(
            f"Expected type {expected_type.__name__}, found {actual_type.__name__}", 
            *args, 
            **kwargs
        )


class InvalidFormatError(DeserializationError):
    """Raised when the serialized data is in an invalid format."""
    
    def __init__(
        self, 
        format_name: str, 
        details: Optional[str] = None, 
        *args, 
        **kwargs
    ) -> None:
        """
        Initialize with information about the invalid format.
        
        Args:
            format_name: The serialization format that was being used
            details: Additional details about the format error
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        message = f"Invalid {format_name} format"
        if details:
            message += f": {details}"
        super().__init__(message, format_name=format_name, *args, **kwargs)


class NoSuitableSerializerError(SerializationError):
    """Raised when no suitable serializer is found for a value or format."""
    
    def __init__(
        self, 
        format_name: Optional[str] = None, 
        value_type: Optional[Type] = None, 
        *args, 
        **kwargs
    ) -> None:
        """
        Initialize with information about the missing serializer.
        
        Args:
            format_name: The requested serialization format (if known)
            value_type: The type that needs serialization (if known)
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        type_info = f" for {value_type.__name__}" if value_type else ""
        format_info = f" in {format_name} format" if format_name else ""
        super().__init__(
            f"No suitable serializer found{type_info}{format_info}", 
            *args, 
            **kwargs
        )

