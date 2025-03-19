
# pyvider/cty/encoding/protocols.py

"""
Protocol definitions for Cty serialization.

This module defines the core protocols used by the serialization system,
establishing contracts for serializers to implement. Using Protocol classes
enables static type checking while maintaining runtime flexibility.
"""

from abc import abstractmethod
from typing import Any, ClassVar, Protocol, runtime_checkable


@runtime_checkable
class SerializerProtocol(Protocol):
    """
    Protocol defining the interface for value serializers.
    
    Any class implementing this protocol can be used as a serializer
    in the Cty serialization system. This enables extensibility
    without tight coupling.
    """
    format_name: ClassVar[str]  # Unique identifier for this serializer format
    
    @abstractmethod
    def serialize(self, value: Any) -> bytes:
        """
        Serialize a Python/Cty value to bytes.
        
        Args:
            value: The value to serialize (Python native or Cty)
            
        Returns:
            Serialized bytes representation
            
        Raises:
            SerializationError: If serialization fails
        """
        ...
    
    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        """
        Deserialize bytes back to a Python value.
        
        Args:
            data: The serialized bytes to deserialize
            
        Returns:
            Deserialized Python value
            
        Raises:
            DeserializationError: If deserialization fails
        """
        ...
    
    @classmethod
    @abstractmethod
    def supports_format(cls, data: bytes) -> bool:
        """
        Check if the given bytes data is in this serializer's format.
        
        This method enables format auto-detection based on content.
        
        Args:
            data: Bytes data to check
            
        Returns:
            True if this serializer can deserialize the data, False otherwise
        """
        ...
    
    @classmethod
    @abstractmethod
    def format_priority(cls) -> int:
        """
        Return the priority of this serializer for format auto-detection.
        
        Higher values indicate higher priority when multiple serializers
        support the same data. Default implementations should return 0,
        while more specialized implementations can return higher values.
        
        Returns:
            Priority value (higher means higher priority)
        """
        ...


@runtime_checkable
class TypedSerializerProtocol(SerializerProtocol, Protocol):
    """
    Extended protocol for serializers that handle type information.
    
    This protocol adds methods for explicitly handling type information
    during serialization, enabling more precise type preservation.
    """
    
    @abstractmethod
    def serialize_with_type(self, value: Any, type_hint: Any = None) -> bytes:
        """
        Serialize a value with explicit type information.
        
        Args:
            value: The value to serialize
            type_hint: Optional type hint to guide serialization
            
        Returns:
            Serialized bytes with embedded type information
        """
        ...
    
    @abstractmethod
    def deserialize_with_type(self, data: bytes, type_hint: Any = None) -> Any:
        """
        Deserialize bytes with type information.
        
        Args:
            data: The serialized bytes to deserialize
            type_hint: Optional type hint to guide deserialization
            
        Returns:
            Deserialized value with preserved type information
        """
        ...
