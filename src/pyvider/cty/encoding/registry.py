
# pyvider/cty/encoding/registry.py

"""
Registry for serialization formats.

This module provides a central registry for all serialization formats
supported by the Cty system. It handles registration, discovery, and
format auto-detection.
"""

import functools
from typing import Callable, Dict, List, Optional, Type, TypeVar, cast

from pyvider.telemetry import logger
from pyvider.cty.encoding.protocols import SerializerProtocol
from pyvider.cty.encoding.exceptions import NoSuitableSerializerError

T = TypeVar('T', bound=SerializerProtocol)


class SerializerRegistry:
    """
    Registry for serializer implementations.
    
    This registry manages the available serialization formats and provides
    methods for finding appropriate serializers based on format name or
    content.
    """
    
    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._serializers: Dict[str, Type[SerializerProtocol]] = {}
        logger.debug("🧰🔄✅ Initialized empty serializer registry")
    
    def register(self, serializer_class: Type[SerializerProtocol]) -> Type[SerializerProtocol]:
        """
        Register a serializer class with the registry.
        
        Args:
            serializer_class: The serializer class to register
            
        Returns:
            The registered serializer class (for decorator usage)
            
        Raises:
            ValueError: If the serializer doesn't have a format_name
        """
        if not hasattr(serializer_class, 'format_name') or not serializer_class.format_name:
            error_msg = f"Serializer class {serializer_class.__name__} must have a format_name attribute"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise ValueError(error_msg)
            
        format_name = serializer_class.format_name
        self._serializers[format_name] = serializer_class
        logger.debug(f"🧰✅🔄 Registered serializer for format: {format_name}")
        return serializer_class
    
    def unregister(self, format_name: str) -> None:
        """
        Unregister a serializer by format name.
        
        Args:
            format_name: The name of the format to unregister
            
        Raises:
            KeyError: If the format is not registered
        """
        if format_name not in self._serializers:
            error_msg = f"Format {format_name} is not registered"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise KeyError(error_msg)
            
        del self._serializers[format_name]
        logger.debug(f"🧰✅🔄 Unregistered serializer for format: {format_name}")
    
    def get_serializer(self, format_name: str) -> Type[SerializerProtocol]:
        """
        Get a serializer class by format name.
        
        Args:
            format_name: The name of the format to get
            
        Returns:
            The serializer class
            
        Raises:
            NoSuitableSerializerError: If the format is not registered
        """
        if format_name not in self._serializers:
            error_msg = f"No serializer registered for format: {format_name}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise NoSuitableSerializerError(format_name=format_name)
            
        serializer_class = self._serializers[format_name]
        logger.debug(f"🧰✅🔄 Retrieved serializer for format: {format_name}")
        return serializer_class
    
    def get_serializer_for_data(self, data: bytes) -> Type[SerializerProtocol]:
        """
        Auto-detect and get a suitable serializer for the given data.
        
        This method tries each registered serializer to find one that
        supports the given data, based on content detection.
        
        Args:
            data: The serialized data to get a serializer for
            
        Returns:
            The most appropriate serializer class
            
        Raises:
            NoSuitableSerializerError: If no suitable serializer is found
        """
        logger.debug(f"🧰🔄🔍 Auto-detecting serializer for {len(data)} bytes")
        
        # Find all serializers that support this data
        supported_serializers = []
        for format_name, serializer_class in self._serializers.items():
            try:
                if serializer_class.supports_format(data):
                    supported_serializers.append(serializer_class)
                    logger.debug(f"🧰✅🔍 Format {format_name} supports the data")
            except Exception as e:
                logger.debug(f"🧰⚠️🔍 Error checking format support for {format_name}: {e}")
        
        if not supported_serializers:
            error_msg = "No suitable serializer found for the given data"
            logger.error(f"🧰❌🔍 {error_msg}")
            raise NoSuitableSerializerError()
        
        # Return the highest priority serializer
        serializer_class = max(supported_serializers, key=lambda s: s.format_priority())
        logger.debug(f"🧰✅🔍 Selected {serializer_class.format_name} as the best serializer")
        return serializer_class
    
    def list_formats(self) -> List[str]:
        """
        Get a list of all registered format names.
        
        Returns:
            List of format names
        """
        formats = sorted(self._serializers.keys())
        logger.debug(f"🧰✅🔄 Listed {len(formats)} registered formats")
        return formats
    
    def register_decorator(self) -> Callable[[Type[T]], Type[T]]:
        """
        Get a decorator for registering serializers.
        
        Returns:
            A decorator function
        """
        def decorator(serializer_class: Type[T]) -> Type[T]:
            """Register a serializer class with the registry."""
            self.register(cast(Type[SerializerProtocol], serializer_class))
            return serializer_class
        return decorator


# Create a global registry instance
registry = SerializerRegistry()
register_serializer = registry.register_decorator()


@functools.lru_cache(maxsize=32)
def get_serializer(format_name: Optional[str] = None, data: Optional[bytes] = None) -> Type[SerializerProtocol]:
    """
    Get a serializer class by format name or auto-detect from data.
    
    This function provides a convenient way to get a serializer either by
    explicitly specifying a format or by auto-detecting from data content.
    
    Args:
        format_name: The name of the format to get, or None for auto-detection
        data: The serialized data to auto-detect, required if format_name is None
        
    Returns:
        The serializer class
        
    Raises:
        NoSuitableSerializerError: If no suitable serializer can be found
        ValueError: If neither format_name nor data is provided
    """
    if format_name is not None:
        return registry.get_serializer(format_name)
    elif data is not None:
        return registry.get_serializer_for_data(data)
    else:
        error_msg = "Either format_name or data must be provided"
        logger.error(f"🧰❌🔄 {error_msg}")
        raise ValueError(error_msg)


def create_serializer(format_name: Optional[str] = None, data: Optional[bytes] = None) -> SerializerProtocol:
    """
    Create a serializer instance by format name or auto-detect from data.
    
    This function provides a convenient way to create a serializer instance
    either by explicitly specifying a format or by auto-detecting from data.
    
    Args:
        format_name: The name of the format to use, or None for auto-detection
        data: The serialized data to auto-detect, required if format_name is None
        
    Returns:
        A serializer instance
    """
    serializer_class = get_serializer(format_name, data)
    return serializer_class()
