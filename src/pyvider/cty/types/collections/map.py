#
# pyvider/cty/types/collections/map.py
#

"""
This module defines the CtyMap type for the Cty type system.

CtyMap represents a map type in the Cty type system where each map has a key type 
and a value type. Maps are collections of key-value pairs where all keys have the 
same type and all values have the same type.

This implementation follows go-cty's Map type, with strong typing throughout.
"""

from typing import Any, ClassVar, Dict, Generic, Optional, TypeVar, cast

import attrs

from pyvider.cty.exceptions import ValidationError
from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType

K = TypeVar('K')
V = TypeVar('V')

@attrs.define(frozen=True, slots=True)
class CtyMap(CtyType[Dict[K, V]], Generic[K, V]):
    """
    CtyMap represents a map type in the Cty type system.
    
    Maps are key-value collections with a fixed key type and value type.
    This implementation follows go-cty's Map design with proper CtyValue wrapping.
    
    Attributes:
        key_type: CtyType for map keys
        value_type: CtyType for map values
        value: Dictionary of validated values (optional, for pre-validated maps)
    """
    ctype: ClassVar[str] = "map"
    key_type: CtyType[K] = attrs.field(kw_only=True)
    value_type: CtyType[V] = attrs.field(kw_only=True)
    value: Dict["CtyValue", "CtyValue"] = attrs.field(factory=dict, kw_only=True)

    def __attrs_post_init__(self) -> None:
        """Validate CtyMap configuration."""
        logger.debug("🔌🔍🔄 Validating CtyMap configuration")
        if not isinstance(self.key_type, CtyType):
            error_msg = f"Expected CtyType for key_type, got {type(self.key_type).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise ValidationError(error_msg)
        if not isinstance(self.value_type, CtyType):
            error_msg = f"Expected CtyType for value_type, got {type(self.value_type).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise ValidationError(error_msg)
        logger.debug("🔌✅🔄 CtyMap configuration validated successfully")

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value conforms to this map type.
        
        Args:
            value: Dictionary (or None) to validate
            
        Returns:
            A CtyValue wrapping a validated map
            
        Raises:
            ValidationError: If validation fails
        """
        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue
        
        logger.debug(f"🔌🔍🔄 Validating value as CtyMap: {type(value).__name__}")
        
        # Handle None or empty values
        match value:
            case None:
                logger.debug("🔌🔍✅ None value converted to empty map")
                return CtyValue(type_=self, value={})
            case {}:
                logger.debug("🔌🔍✅ Empty dict is valid")
                return CtyValue(type_=self, value={})
            case dict():
                # Continue with validation
                pass
            case _:
                error_msg = f"Expected dict, got {type(value).__name__}"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise ValidationError(error_msg)
        
        # Validate each key-value pair
        validated_map = {}
        validation_errors = []
        
        for k, v in value.items():
            try:
                # Validate key
                if isinstance(k, CtyValue):
                    if not k.type.equal(self.key_type):
                        raise ValidationError(f"Key type mismatch: expected {self.key_type}, got {k.type}")
                    if k.is_null or k.is_unknown:
                        raise ValidationError("Map keys cannot be null or unknown")
                    validated_key = k
                else:
                    validated_key = self.key_type.validate(k)
                    if validated_key.is_null or validated_key.is_unknown:
                        raise ValidationError("Map keys cannot be null or unknown")
                
                # Validate value
                if isinstance(v, CtyValue):
                    if not v.type.equal(self.value_type):
                        raise ValidationError(f"Value type mismatch: expected {self.value_type}, got {v.type}")
                    validated_value = v
                else:
                    validated_value = self.value_type.validate(v)
                
                # Add to validated map
                validated_map[validated_key] = validated_value
                logger.debug(f"🔌🔍✅ Validated map entry: {validated_key} -> {validated_value}")
            except ValidationError as e:
                error_msg = f"Invalid map entry {k!r}: {v!r} -> {e}"
                logger.error(f"🔌❌🔄 {error_msg}")
                validation_errors.append(error_msg)
            except Exception as e:
                error_msg = f"Error processing map entry {k!r}: {v!r} -> {e}"
                logger.error(f"🔌❌🔄 {error_msg}")
                validation_errors.append(error_msg)
        
        # If there were validation errors, raise an exception
        if validation_errors:
            error_msg = "Map validation failed:\n" + "\n".join(validation_errors)
            logger.error(f"🔌❌🔄 {error_msg}")
            raise ValidationError(error_msg)
        
        logger.debug(f"🔌🔍✅ Map validated successfully with {len(validated_map)} entries")
        return CtyValue(type_=self, value=validated_map)

    def get(self, map_value: "CtyValue", key: Any, default: Optional["CtyValue"] = None) -> Optional["CtyValue"]:
        """
        Get a value from the map by key.
        
        Args:
            map_value: CtyValue wrapping a validated map
            key: Key to look up (will be validated if not a CtyValue)
            default: Default value to return if key not found
            
        Returns:
            CtyValue for the key, or default if not found
            
        Raises:
            ValidationError: If the map is null/unknown or key validation fails
        """
        from pyvider.cty.values import CtyValue
        
        logger.debug(f"🔌🔍🔄 Getting value for key {key!r} from map")
        
        # Validate map_value
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            error_msg = f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise TypeError(error_msg)
            
        if map_value.is_null or map_value.is_unknown:
            error_msg = "Cannot get from null or unknown map"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise ValidationError(error_msg)
        
        # Validate the key if not already a CtyValue
        validated_key = None
        try:
            if isinstance(key, CtyValue):
                if key.type.equal(self.key_type):
                    validated_key = key
                else:
                    logger.debug(f"🔌🔍⚠️ Key type mismatch, returning default")
                    return default
            else:
                validated_key = self.key_type.validate(key)
        except Exception as e:
            logger.debug(f"🔌🔍⚠️ Key validation failed, returning default: {e}")
            return default
        
        # Look for the key in the map
        map_data = map_value.value
        
        # Direct lookup
        if validated_key in map_data:
            result = map_data[validated_key]
            logger.debug(f"🔌🔍✅ Found value for key: {validated_key}")
            return result
        
        # Value-based lookup for string keys
        for k, v in map_data.items():
            if hasattr(k, 'value') and hasattr(validated_key, 'value'):
                if k.value == validated_key.value:
                    logger.debug(f"🔌🔍✅ Found value for key by value equality: {validated_key.value}")
                    return v
        
        logger.debug(f"🔌🔍⚠️ Key not found, returning default")
        return default

    def set(self, map_value: "CtyValue", key: Any, value: Any) -> "CtyValue":
        """
        Set a key-value pair in the map, returning a new map.
        
        This operation is immutable - it returns a new CtyValue with the updated map.
        
        Args:
            map_value: CtyValue wrapping a validated map
            key: Key to set (will be validated if not a CtyValue)
            value: Value to set (will be validated if not a CtyValue)
            
        Returns:
            A new CtyValue with the updated map
            
        Raises:
            ValidationError: If validation fails
        """
        from pyvider.cty.values import CtyValue
        
        logger.debug(f"🔌📝🔄 Setting key {key!r} to value {value!r} in map")
        
        # Validate map_value
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            error_msg = f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise TypeError(error_msg)
            
        if map_value.is_null or map_value.is_unknown:
            error_msg = "Cannot set on null or unknown map"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise ValidationError(error_msg)
        
        # Validate key and value
        validated_key = None
        if isinstance(key, CtyValue):
            if not key.type.equal(self.key_type):
                error_msg = f"Key type mismatch: expected {self.key_type}, got {key.type}"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise ValidationError(error_msg)
            validated_key = key
        else:
            validated_key = self.key_type.validate(key)
        
        validated_value = None
        if isinstance(value, CtyValue):
            if not value.type.equal(self.value_type):
                error_msg = f"Value type mismatch: expected {self.value_type}, got {value.type}"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise ValidationError(error_msg)
            validated_value = value
        else:
            validated_value = self.value_type.validate(value)
        
        # Create a new map with the updated key-value pair
        new_map = dict(map_value.value)
        
        # Check for existing key with same value
        key_to_remove = None
        for k in new_map:
            if hasattr(k, 'value') and hasattr(validated_key, 'value'):
                if k.value == validated_key.value:
                    key_to_remove = k
                    break
        
        # Remove existing key if found
        if key_to_remove is not None:
            del new_map[key_to_remove]
        
        # Add new key-value pair
        new_map[validated_key] = validated_value
        
        logger.debug(f"🔌📝✅ Set key {validated_key!r} to value {validated_value!r}")
        return CtyValue(type_=self, value=new_map)

    def delete(self, map_value: "CtyValue", key: Any) -> "CtyValue":
        """
        Delete a key from the map, returning a new map.
        
        This operation is immutable - it returns a new CtyValue with the updated map.
        
        Args:
            map_value: CtyValue wrapping a validated map
            key: Key to delete (will be validated if not a CtyValue)
            
        Returns:
            A new CtyValue with the updated map
            
        Raises:
            ValidationError: If validation fails
        """
        from pyvider.cty.values import CtyValue
        
        logger.debug(f"🔌📝🔄 Deleting key {key!r} from map")
        
        # Validate map_value
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            error_msg = f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise TypeError(error_msg)
            
        if map_value.is_null or map_value.is_unknown:
            error_msg = "Cannot delete from null or unknown map"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise ValidationError(error_msg)
        
        # Validate the key
        validated_key = None
        try:
            if isinstance(key, CtyValue):
                if key.type.equal(self.key_type):
                    validated_key = key
                else:
                    logger.debug(f"🔌📝⚠️ Key type mismatch, map unchanged")
                    return map_value
            else:
                validated_key = self.key_type.validate(key)
        except Exception as e:
            logger.debug(f"🔌📝⚠️ Key validation failed, map unchanged: {e}")
            return map_value
        
        # Create a new map without the key
        new_map = {}
        key_found = False
        
        for k, v in map_value.value.items():
            if k == validated_key:
                key_found = True
                continue
                
            if hasattr(k, 'value') and hasattr(validated_key, 'value'):
                if k.value == validated_key.value:
                    key_found = True
                    continue
                    
            new_map[k] = v
            
        if key_found:
            logger.debug(f"🔌📝✅ Deleted key {validated_key!r}")
        else:
            logger.debug(f"🔌📝⚠️ Key {validated_key!r} not found, map unchanged")
            return map_value
            
        return CtyValue(type_=self, value=new_map)

    def equal(self, other: CtyType) -> bool:
        """
        Check if this type is equal to another type.
        
        Args:
            other: Type to compare with
            
        Returns:
            True if types are equal
        """
        logger.debug(f"🔌🔍🔄 Checking equality with {type(other).__name__}")
        
        if not isinstance(other, CtyMap):
            logger.debug(f"🔌🔍❌ Not equal: {type(other).__name__} is not CtyMap")
            return False
            
        key_equal = self.key_type.equal(other.key_type)
        value_equal = self.value_type.equal(other.value_type)
        result = key_equal and value_equal
        
        logger.debug(f"🔌🔍✅ Equality check: {result}")
        return result

    def usable_as(self, other: CtyType) -> bool:
        """
        Check if this type can be used as another type.
        
        Args:
            other: Type to check compatibility with
            
        Returns:
            True if this type can be used as the other type
        """
        logger.debug(f"🔌🔍🔄 Checking usability as {type(other).__name__}")
        
        if not isinstance(other, CtyMap):
            logger.debug(f"🔌🔍❌ Not usable as: {type(other).__name__} is not CtyMap")
            return False
            
        key_usable = self.key_type.usable_as(other.key_type)
        value_usable = self.value_type.usable_as(other.value_type)
        result = key_usable and value_usable
        
        logger.debug(f"🔌🔍✅ Usability check: {result}")
        return result

    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, CtyMap):
            return False
        return self.equal(other)

    def __hash__(self) -> int:
        """Hash for use in sets and as dict keys."""
        return hash((self.__class__, hash(self.key_type), hash(self.value_type)))

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"map({self.key_type}, {self.value_type})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"CtyMap(key_type={repr(self.key_type)}, value_type={repr(self.value_type)})"

# 🐍🏗️🐣
