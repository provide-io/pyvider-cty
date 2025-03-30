#
# pyvider/cty/encoding/capsule_serializer.py
#

"""
Capsule serialization support for Cty values.

This module handles serialization and deserialization of capsule-typed values,
which encapsulate arbitrary Python objects. It provides a plugin architecture
for extending serialization support to different types of encapsulated objects.
"""

import base64
import importlib
import inspect
import pickle
from typing import Any, Dict, Optional, Type, ClassVar, Protocol, TypeVar, cast, runtime_checkable

import attrs

from pyvider.cty.exceptions import (
    CapsuleSerializationError,
    CapsuleDeserializationError,
    CapsuleTypeError,
    CapsuleValueError,
)
from pyvider.cty.logger import logger


@runtime_checkable
class CapsuleHandlerProtocol(Protocol):
    """
    Protocol defining the interface for capsule value handlers.
    
    Handlers are responsible for serializing and deserializing specific types
    of encapsulated values in capsule types.
    """
    
    @classmethod
    def can_handle(cls, value: Any) -> bool:
        """
        Check if this handler can handle the given value.
        
        Args:
            value: The value to check
            
        Returns:
            True if this handler can handle the value, False otherwise
        """
        ...
    
    @classmethod
    async def serialize(cls, value: Any) -> Dict[str, Any]:
        """
        Serialize a value to a dictionary representation.
        
        Args:
            value: The value to serialize
            
        Returns:
            A dictionary representation of the value
            
        Raises:
            CapsuleSerializationError: If serialization fails
        """
        ...
    
    @classmethod
    async def deserialize(cls, data: Dict[str, Any]) -> Any:
        """
        Deserialize a dictionary representation to a value.
        
        Args:
            data: The dictionary to deserialize
            
        Returns:
            The deserialized value
            
        Raises:
            CapsuleDeserializationError: If deserialization fails
        """
        ...


@attrs.define(frozen=True)
class HandlerRegistry:
    """
    Registry for capsule value handlers.
    
    This registry manages handlers for different types of encapsulated values
    and provides methods for finding the appropriate handler for a value.
    """
    _handlers: ClassVar[Dict[str, Type[CapsuleHandlerProtocol]]] = {}
    
    @classmethod
    def register(cls, name: str, handler: Type[CapsuleHandlerProtocol]) -> None:
        """
        Register a handler for a specific type name.
        
        Args:
            name: The name to register the handler under
            handler: The handler class
        """
        logger.debug(f"🧩🔧✅ Registering capsule handler: {name}")
        cls._handlers[name] = handler
    
    @classmethod
    def get_handler(cls, type_name: str) -> Optional[Type[CapsuleHandlerProtocol]]:
        """
        Get a handler by type name.
        
        Args:
            type_name: The name of the handler to get
            
        Returns:
            The handler class, or None if not found
        """
        handler = cls._handlers.get(type_name)
        if handler:
            logger.debug(f"🧩🔍✅ Found handler for type: {type_name}")
        else:
            logger.debug(f"🧩🔍⚠️ No handler found for type: {type_name}")
        return handler
    
    @classmethod
    def find_handler_for_value(cls, value: Any) -> Optional[Type[CapsuleHandlerProtocol]]:
        """
        Find a handler that can handle the given value.
        
        This method tries each registered handler until it finds one that
        can handle the given value.
        
        Args:
            value: The value to find a handler for
            
        Returns:
            The handler class, or None if no handler can handle the value
        """
        logger.debug(f"🧩🔍🔄 Finding handler for value type: {type(value).__name__}")
        
        # Try each handler
        for name, handler in cls._handlers.items():
            try:
                if handler.can_handle(value):
                    logger.debug(f"🧩🔍✅ Handler {name} can handle the value")
                    return handler
            except Exception as e:
                logger.debug(f"🧩🔍⚠️ Error checking if handler {name} can handle value: {e}")
                continue
        
        # No handler found, use pickle as fallback
        logger.debug(f"🧩🔍⚠️ No handler found, returning pickle handler")
        return PickleHandler


class SimpleAttributeHandler:
    """
    Handler for objects with simple attributes.
    
    This handler serializes objects with simple attribute values
    (strings, numbers, booleans) by capturing their attributes.
    """
    
    @classmethod
    def can_handle(cls, value: Any) -> bool:
        """
        Check if this handler can handle the given value.
        
        This handler can handle objects with __dict__ attribute
        whose values are simple types.
        
        Args:
            value: The value to check
            
        Returns:
            True if this handler can handle the value, False otherwise
        """
        if value is None or not hasattr(value, "__dict__"):
            return False
            
        # Check if all attributes are simple types
        for attr_name, attr_value in value.__dict__.items():
            if attr_name.startswith("_"):
                continue
                
            if isinstance(attr_value, (str, int, float, bool, type(None))):
                continue
                
            if isinstance(attr_value, (list, tuple)) and all(
                isinstance(item, (str, int, float, bool, type(None)))
                for item in attr_value
            ):
                continue
                
            if isinstance(attr_value, dict) and all(
                isinstance(k, str) and isinstance(v, (str, int, float, bool, type(None)))
                for k, v in attr_value.items()
            ):
                continue
                
            return False
            
        return True
    
    @classmethod
    async def serialize(cls, value: Any) -> Dict[str, Any]:
        """
        Serialize a value to a dictionary representation.
        
        Args:
            value: The value to serialize
            
        Returns:
            A dictionary representation of the value
            
        Raises:
            CapsuleSerializationError: If serialization fails
        """
        try:
            # Get the full type name including module
            python_type = f"{value.__class__.__module__}.{value.__class__.__name__}"
            
            # Extract attributes
            attributes = {}
            for attr_name, attr_value in value.__dict__.items():
                if attr_name.startswith("_"):
                    continue
                    
                attributes[attr_name] = attr_value
                
            return {
                "type": "simple_attributes",
                "python_type": python_type,
                "attributes": attributes
            }
        except Exception as e:
            error_msg = f"Failed to serialize simple attributes: {e}"
            logger.error(f"🧩❗❌ {error_msg}")
            raise CapsuleSerializationError(error_msg, value)
    
    @classmethod
    async def deserialize(cls, data: Dict[str, Any]) -> Any:
        """
        Deserialize a dictionary representation to a value.
        
        Args:
            data: The dictionary to deserialize
            
        Returns:
            The deserialized value
            
        Raises:
            CapsuleDeserializationError: If deserialization fails
        """
        try:
            # Get the class from the Python type string
            python_type = data.get("python_type", "")
            if not python_type:
                raise ValueError("Missing python_type in data")
                
            try:
                module_name, class_name = python_type.rsplit(".", 1)
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                error_msg = f"Could not import class {python_type}: {e}"
                logger.error(f"🧩❗❌ {error_msg}")
                raise CapsuleDeserializationError(error_msg, data=data)
            
            # Create a new instance without calling __init__
            instance = cls.__new__(cls)
            
            # Set the attributes
            attributes = data.get("attributes", {})
            for attr_name, attr_value in attributes.items():
                setattr(instance, attr_name, attr_value)
                
            return instance
        except CapsuleDeserializationError:
            # Re-raise CapsuleDeserializationError without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to deserialize simple attributes: {e}"
            logger.error(f"🧩❗❌ {error_msg}")
            raise CapsuleDeserializationError(error_msg, data=data)


class PickleHandler:
    """
    Handler for general Python objects using pickle.
    
    This handler uses pickle to serialize and deserialize Python objects.
    It should be used as a fallback when no other handler can handle the value.
    """
    
    @classmethod
    def can_handle(cls, value: Any) -> bool:
        """
        Check if this handler can handle the given value.
        
        This handler attempts to pickle the value to determine if it's
        serializable.
        
        Args:
            value: The value to check
            
        Returns:
            True if the value can be pickled, False otherwise
        """
        try:
            # Try to pickle the value
            pickle.dumps(value)
            return True
        except Exception:
            return False
    
    @classmethod
    async def serialize(cls, value: Any) -> Dict[str, Any]:
        """
        Serialize a value using pickle.
        
        Args:
            value: The value to serialize
            
        Returns:
            A dictionary with the pickled value
            
        Raises:
            CapsuleSerializationError: If serialization fails
        """
        try:
            # Pickle the value and encode as base64
            pickled = pickle.dumps(value)
            encoded = base64.b64encode(pickled).decode('utf-8')
            
            # Include the Python type information
            python_type = f"{type(value).__module__}.{type(value).__name__}"
            
            return {
                "type": "pickle",
                "python_type": python_type,
                "value": encoded
            }
        except Exception as e:
            error_msg = f"Failed to pickle value: {e}"
            logger.error(f"🧩❗❌ {error_msg}")
            raise CapsuleSerializationError(error_msg, value)
    
    @classmethod
    async def deserialize(cls, data: Dict[str, Any]) -> Any:
        """
        Deserialize a value using pickle.
        
        Args:
            data: The dictionary with the pickled value
            
        Returns:
            The deserialized value
            
        Raises:
            CapsuleDeserializationError: If deserialization fails
        """
        try:
            # Get the encoded value
            encoded = data.get("value", "")
            if not encoded:
                raise ValueError("Missing pickled value in data")
                
            # Decode and unpickle
            pickled = base64.b64decode(encoded)
            return pickle.loads(pickled)
        except Exception as e:
            error_msg = f"Failed to unpickle value: {e}"
            logger.error(f"🧩❗❌ {error_msg}")
            raise CapsuleDeserializationError(error_msg, data=data)


# Register default handlers
HandlerRegistry.register("pickle", PickleHandler)
HandlerRegistry.register("simple_attributes", SimpleAttributeHandler)


async def prepare_capsule_value(value: Any, capsule_type: Any) -> Dict[str, Any]:
    """
    Prepare a capsule value for serialization.
    
    This function finds the appropriate handler for the value and
    serializes it to a dictionary representation.
    
    Args:
        value: The encapsulated value to serialize
        capsule_type: The capsule type for contextual information
        
    Returns:
        A dictionary representation of the capsule value
        
    Raises:
        CapsuleSerializationError: If serialization fails
    """
    logger.debug(f"🧩📤🔄 Preparing capsule value for serialization: {capsule_type.friendly_name}")
    
    # Handle null values
    if value is None:
        logger.debug("🧩📤✅ Creating null capsule representation")
        return {
            "capsule_type": capsule_type.friendly_name,
            "is_null": True
        }
        
    # Handle unknown values (values with is_unknown=True)
    if hasattr(value, 'is_unknown') and value.is_unknown:
        logger.debug("🧩📤✅ Creating unknown capsule representation")
        return {
            "capsule_type": capsule_type.friendly_name,
            "is_unknown": True
        }
    
    try:
        # Find an appropriate handler
        handler = HandlerRegistry.find_handler_for_value(value)
        if handler is None:
            error_msg = f"No handler found for value of type {type(value).__name__}"
            logger.error(f"🧩❗❌ {error_msg}")
            raise CapsuleSerializationError(error_msg, value, capsule_type)
        
        # Serialize the value using the handler
        capsule_data = await handler.serialize(value)
        
        # Create the full capsule representation
        result = {
            "capsule_type": capsule_type.friendly_name,
            "is_null": False,
            "is_unknown": False,
            "capsule_data": capsule_data
        }
        
        logger.debug(f"🧩📤✅ Successfully prepared capsule value using {handler.__name__}")
        return result
    except CapsuleSerializationError:
        # Re-raise CapsuleSerializationError without wrapping
        raise
    except Exception as e:
        error_msg = f"Failed to prepare capsule value: {e}"
        logger.error(f"🧩❗❌ {error_msg}")
        raise CapsuleSerializationError(error_msg, value, capsule_type) from e


async def process_capsule_value(data: Dict[str, Any]) -> "CtyValue":
    """
    Process a deserialized capsule value.
    
    This function creates a CtyValue from a deserialized capsule representation.
    
    Args:
        data: The deserialized capsule data
        
    Returns:
        A CtyValue with the capsule value
        
    Raises:
        CapsuleDeserializationError: If deserialization fails
    """
    # Import here to avoid circular imports
    from pyvider.cty.values import CtyValue
    logger.debug(f"🧩📥🔄 Processing capsule value")
    
    # Get the capsule type name
    capsule_type_name = data.get("capsule_type")
    if not capsule_type_name:
        error_msg = "Missing capsule_type in capsule data"
        logger.error(f"🧩❗❌ {error_msg}")
        raise CapsuleDeserializationError(error_msg, data=data)
    
    # Find the capsule type
    from pyvider.cty.types.capsule import CtyCapsule
    capsule_type = CtyCapsule.get_registered_type(capsule_type_name)
    if capsule_type is None:
        error_msg = f"Unknown capsule type: {capsule_type_name}"
        logger.error(f"🧩❗❌ {error_msg}")
        raise CapsuleDeserializationError(error_msg, data=data)
    
    # Check for special states
    is_null = data.get("is_null", False)
    is_unknown = data.get("is_unknown", False)
    
    # Handle null values
    if is_null:
        logger.debug(f"🧩📥✅ Creating null capsule value for type {capsule_type_name}")
        return CtyValue(type_=capsule_type, is_null=True)
    
    # Handle unknown values
    if is_unknown:
        logger.debug(f"🧩📥✅ Creating unknown capsule value for type {capsule_type_name}")
        return CtyValue(type_=capsule_type, is_unknown=True)
    
    # Get the capsule data
    capsule_data = data.get("capsule_data")
    if not capsule_data:
        error_msg = "Missing capsule_data in non-null capsule value"
        logger.error(f"🧩❗❌ {error_msg}")
        raise CapsuleDeserializationError(error_msg, data=data)
    
    try:
        # Get the handler type
        handler_type = capsule_data.get("type")
        if not handler_type:
            error_msg = "Missing type in capsule_data"
            logger.error(f"🧩❗❌ {error_msg}")
            raise CapsuleDeserializationError(error_msg, data=data)
        
        # Get the handler
        handler = HandlerRegistry.get_handler(handler_type)
        if handler is None:
            error_msg = f"No handler found for type: {handler_type}"
            logger.error(f"🧩❗❌ {error_msg}")
            raise CapsuleDeserializationError(error_msg, data=data)
        
        # Deserialize the value
        value = await handler.deserialize(capsule_data)
        
        # Create the CtyValue
        result = CtyValue(type_=capsule_type, value=value)
        logger.debug(f"🧩📥✅ Successfully processed capsule value")
        return result
    except CapsuleDeserializationError:
        # Re-raise CapsuleDeserializationError without wrapping
        raise
    except Exception as e:
        error_msg = f"Failed to process capsule value: {e}"
        logger.error(f"🧩❗❌ {error_msg}")
        raise CapsuleDeserializationError(error_msg, data=data) from e


class EnumHandler:
    """
    Handler for Python enum values.
    
    This handler serializes and deserializes enum values by name.
    """
    
    @classmethod
    def can_handle(cls, value: Any) -> bool:
        """Check if this handler can handle the given value."""
        from enum import Enum
        return isinstance(value, Enum)
    
    @classmethod
    async def serialize(cls, value: Any) -> Dict[str, Any]:
        """Serialize an enum value."""
        from enum import Enum
        if not isinstance(value, Enum):
            raise CapsuleSerializationError("Value is not an enum", value)
            
        try:
            return {
                "type": "enum",
                "python_type": f"{value.__class__.__module__}.{value.__class__.__name__}",
                "name": value.name,
                "value": value.value
            }
        except Exception as e:
            raise CapsuleSerializationError(f"Failed to serialize enum: {e}", value)
    
    @classmethod
    async def deserialize(cls, data: Dict[str, Any]) -> Any:
        """Deserialize an enum value."""
        try:
            # Get the enum class
            python_type = data.get("python_type", "")
            if not python_type:
                raise ValueError("Missing python_type in data")
                
            module_name, class_name = python_type.rsplit(".", 1)
            module = importlib.import_module(module_name)
            enum_class = getattr(module, class_name)
            
            # Get the enum value by name
            name = data.get("name")
            if name is not None:
                return enum_class[name]
                
            # Fallback to value if name not available
            value = data.get("value")
            if value is not None:
                return enum_class(value)
                
            raise ValueError("Missing both name and value in enum data")
        except Exception as e:
            raise CapsuleDeserializationError(f"Failed to deserialize enum: {e}", data=data)


class DataclassHandler:
    """
    Handler for dataclass instances.
    
    This handler serializes and deserializes dataclass instances
    by extracting and setting their fields.
    """
    
    @classmethod
    def can_handle(cls, value: Any) -> bool:
        """Check if this handler can handle the given value."""
        return hasattr(value, "__dataclass_fields__")
    
    @classmethod
    async def serialize(cls, value: Any) -> Dict[str, Any]:
        """Serialize a dataclass instance."""
        try:
            from dataclasses import asdict, is_dataclass
            
            if not is_dataclass(value):
                raise CapsuleSerializationError("Value is not a dataclass", value)
                
            # Convert to dictionary and extract type info
            fields = asdict(value)
            python_type = f"{value.__class__.__module__}.{value.__class__.__name__}"
            
            return {
                "type": "dataclass",
                "python_type": python_type,
                "fields": fields
            }
        except Exception as e:
            raise CapsuleSerializationError(f"Failed to serialize dataclass: {e}", value)
    
    @classmethod
    async def deserialize(cls, data: Dict[str, Any]) -> Any:
        """Deserialize a dataclass instance."""
        try:
            from dataclasses import fields
            
            # Get the dataclass
            python_type = data.get("python_type", "")
            if not python_type:
                raise ValueError("Missing python_type in data")
                
            module_name, class_name = python_type.rsplit(".", 1)
            module = importlib.import_module(module_name)
            dataclass = getattr(module, class_name)
            
            # Create instance with fields
            field_data = data.get("fields", {})
            return dataclass(**field_data)
        except Exception as e:
            raise CapsuleDeserializationError(f"Failed to deserialize dataclass: {e}", data=data)


class AttrsHandler:
    """
    Handler for attrs instances.
    
    This handler serializes and deserializes attrs instances
    by extracting and setting their attributes.
    """
    
    @classmethod
    def can_handle(cls, value: Any) -> bool:
        """Check if this handler can handle the given value."""
        return hasattr(value, "__attrs_attrs__")
    
    @classmethod
    async def serialize(cls, value: Any) -> Dict[str, Any]:
        """Serialize an attrs instance."""
        try:
            # Check if it's an attrs instance
            if not hasattr(value, "__attrs_attrs__"):
                raise CapsuleSerializationError("Value is not an attrs instance", value)
                
            # Extract attributes
            import attrs
            attributes = {}
            for field in attrs.fields(value.__class__):
                attributes[field.name] = getattr(value, field.name)
                
            # Get type info
            python_type = f"{value.__class__.__module__}.{value.__class__.__name__}"
            
            return {
                "type": "attrs",
                "python_type": python_type,
                "attributes": attributes
            }
        except Exception as e:
            raise CapsuleSerializationError(f"Failed to serialize attrs instance: {e}", value)
    
    @classmethod
    async def deserialize(cls, data: Dict[str, Any]) -> Any:
        """Deserialize an attrs instance."""
        try:
            # Get the class
            python_type = data.get("python_type", "")
            if not python_type:
                raise ValueError("Missing python_type in data")
                
            module_name, class_name = python_type.rsplit(".", 1)
            module = importlib.import_module(module_name)
            attrs_class = getattr(module, class_name)
            
            # Create instance with attributes
            attributes = data.get("attributes", {})
            return attrs_class(**attributes)
        except Exception as e:
            raise CapsuleDeserializationError(f"Failed to deserialize attrs instance: {e}", data=data)


# Register additional handlers
HandlerRegistry.register("enum", EnumHandler)
HandlerRegistry.register("dataclass", DataclassHandler)
HandlerRegistry.register("attrs", AttrsHandler)

# 🐍🏗️🐣
