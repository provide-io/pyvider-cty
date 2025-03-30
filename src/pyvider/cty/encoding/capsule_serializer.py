#
# pyvider/cty/encoding/capsule_serializer.py
#

"""
Handles serialization and deserialization of capsule values.

This module provides a pluggable system for serializing capsule values,
with different strategies for different types of objects.
"""

import pickle
import base64
import types
import inspect
from typing import Any, Dict, Optional, Type, List, Union

from pyvider.cty.exceptions import SerializationError, DeserializationError, CapsuleSerializationError, CapsuleDeserializationError
from pyvider.cty.logger import logger
from pyvider.cty.types.capsule import CtyCapsule

class CapsuleHandler:
    """
    Handles serialization and deserialization of capsule values.
    
    This provides a pluggable system for serializing capsule values,
    with different strategies for different types of objects.
    """
    
    _handlers: Dict[Type, 'CapsuleHandler'] = {}
    
    @classmethod
    def register_handler(cls, handled_type: Type, handler: 'CapsuleHandler') -> None:
        """Register a handler for a specific Python type."""
        cls._handlers[handled_type] = handler
        logger.debug(f"🧩📥✅ Registered capsule handler for {handled_type.__name__}")
    
    @classmethod
    def get_handler(cls, value: Any) -> Optional['CapsuleHandler']:
        """Get the appropriate handler for a value."""
        if value is None:
            return None
            
        # Find the most specific handler by walking the MRO
        value_type = type(value)
        for base in value_type.__mro__:
            if base in cls._handlers:
                return cls._handlers[base]
                
        # Default to pickle handler
        return PickleHandler()
    
    def can_serialize(self, value: Any) -> bool:
        """Check if this handler can serialize the value."""
        raise NotImplementedError("Subclasses must implement can_serialize")
    
    def serialize(self, value: Any) -> Dict[str, Any]:
        """Serialize the value to a dictionary."""
        raise NotImplementedError("Subclasses must implement serialize")
    
    def can_deserialize(self, type_name: str) -> bool:
        """Check if this handler can deserialize the given type."""
        return type_name == self.__class__.__name__.replace('Handler', '').lower()
    
    def deserialize(self, data: Dict[str, Any]) -> Any:
        """Deserialize the dictionary back to a value."""
        raise NotImplementedError("Subclasses must implement deserialize")


class PickleHandler(CapsuleHandler):
    """
    Handler that uses pickle for serialization.
    
    This is a fallback for types that don't have a specific handler.
    """
    
    def can_serialize(self, value: Any) -> bool:
        """Check if the value can be pickled."""
        try:
            pickle.dumps(value)
            return True
        except Exception:
            return False
    
    def serialize(self, value: Any) -> Dict[str, Any]:
        """Serialize the value using pickle."""
        try:
            pickled = pickle.dumps(value)
            encoded = base64.b64encode(pickled).decode('utf-8')
            return {
                "type": "pickle",
                "value": encoded,
                "python_type": f"{type(value).__module__}.{type(value).__name__}"
            }
        except Exception as e:
            raise CapsuleSerializationError(f"Failed to pickle value: {e}", value)
    
    def deserialize(self, data: Dict[str, Any]) -> Any:
        """Deserialize the value using pickle."""
        try:
            encoded = data.get("value", "")
            pickled = base64.b64decode(encoded)
            return pickle.loads(pickled)
        except Exception as e:
            raise CapsuleDeserializationError(f"Failed to unpickle value: {e}")


class SimpleAttributeHandler(CapsuleHandler):
    """
    Handler for objects with simple attributes that can be serialized to JSON.
    """
    
    def can_serialize(self, value: Any) -> bool:
        """Check if the object has only simple attributes."""
        if not hasattr(value, "__dict__"):
            return False
            
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
    
    def serialize(self, value: Any) -> Dict[str, Any]:
        """Serialize the object's attributes."""
        result = {
            "type": "simple_attributes",
            "python_type": f"{type(value).__module__}.{type(value).__name__}",
            "attributes": {}
        }
        
        for attr_name, attr_value in value.__dict__.items():
            if attr_name.startswith("_"):
                continue
                
            result["attributes"][attr_name] = attr_value
            
        return result
    
    def deserialize(self, data: Dict[str, Any]) -> Any:
        """Deserialize the object by creating an instance and setting attributes."""
        try:
            # Get the class from the Python type string
            module_name, class_name = data["python_type"].rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            
            # Create a new instance without calling __init__
            instance = cls.__new__(cls)
            
            # Set the attributes
            for attr_name, attr_value in data.get("attributes", {}).items():
                setattr(instance, attr_name, attr_value)
                
            return instance
        except Exception as e:
            raise CapsuleDeserializationError(f"Failed to deserialize simple attributes: {e}")


def prepare_capsule_value(value: Any, capsule_type: CtyCapsule) -> Dict[str, Any]:
    """
    Prepare a capsule value for serialization.
    
    Args:
        value: The value to serialize
        capsule_type: The capsule type
        
    Returns:
        A serializable dictionary
        
    Raises:
        CapsuleSerializationError: If the value cannot be serialized
    """
    logger.debug(f"🧩📤🔄 Preparing capsule value for serialization: {capsule_type.friendly_name}")
    
    # Handle null values
    if value is None:
        return {
            "capsule_type": capsule_type.friendly_name,
            "is_null": True
        }
    
    # Get the appropriate handler
    handler = CapsuleHandler.get_handler(value)
    
    if handler is None or not handler.can_serialize(value):
        error_msg = f"Cannot serialize value of type {type(value).__name__} in capsule {capsule_type.friendly_name}"
        logger.error(f"🧩❗❌ {error_msg}")
        raise CapsuleSerializationError(error_msg, value, capsule_type)
    
    # Serialize using the handler
    handler_data = handler.serialize(value)
    
    return {
        "capsule_type": capsule_type.friendly_name,
        "capsule_data": handler_data,
        "is_null": False
    }


def process_capsule_value(data: Dict[str, Any]) -> "CtyValue":
    """
    Process a deserialized capsule value.
    
    Args:
        data: The deserialized data
        
    Returns:
        A CtyValue with the capsule value
        
    Raises:
        CapsuleDeserializationError: If the value cannot be deserialized
    """
    from pyvider.cty.values import CtyValue
    logger.debug(f"🧩📥🔄 Processing capsule value")
    
    capsule_type_name = data.get("capsule_type")
    
    if not capsule_type_name:
        error_msg = "Missing capsule_type in capsule data"
        logger.error(f"🧩❗❌ {error_msg}")
        raise CapsuleDeserializationError(error_msg)
    
    # Find the capsule type
    capsule_type = CtyCapsule.get_registered_type(capsule_type_name)
    if capsule_type is None:
        error_msg = f"Unknown capsule type: {capsule_type_name}"
        logger.error(f"🧩❗❌ {error_msg}")
        raise CapsuleDeserializationError(error_msg)
    
    # Handle null values
    if data.get("is_null", False):
        logger.debug(f"🧩📥✅ Creating null capsule value for type {capsule_type_name}")
        return CtyValue(type_=capsule_type, is_null=True)
    
    # Get the capsule data
    capsule_data = data.get("capsule_data")
    if not capsule_data:
        error_msg = "Missing capsule_data in non-null capsule value"
        logger.error(f"🧩❗❌ {error_msg}")
        raise CapsuleDeserializationError(error_msg)
    
    # Determine handler type and deserialize
    handler_type = capsule_data.get("type")
    
    if handler_type == "pickle":
        handler = PickleHandler()
        value = handler.deserialize(capsule_data)
        return CtyValue(type_=capsule_type, value=value)
    
    elif handler_type == "simple_attributes":
        handler = SimpleAttributeHandler()
        value = handler.deserialize(capsule_data)
        return CtyValue(type_=capsule_type, value=value)
    
    else:
        error_msg = f"Unknown handler type: {handler_type}"
        logger.error(f"🧩❗❌ {error_msg}")
        raise CapsuleDeserializationError(error_msg)

# Register default handlers
PickleHandler.register_handler(object, PickleHandler())
SimpleAttributeHandler.register_handler(object, SimpleAttributeHandler())

# 🐍🏗️🐣
