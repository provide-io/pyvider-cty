#
# pyvider/cty/types/collections/map.py
#

"""
CtyMap implementation for the Cty map type.

Maps are collections of key-value pairs where keys have a consistent type
and values have a consistent type.
"""

from typing import Any, ClassVar, Dict, Generic, Optional, TypeVar, Union

import attrs

from pyvider.cty.exceptions import ValidationError
from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType

K = TypeVar('K')
V = TypeVar('V')

@attrs.define(frozen=True, slots=True)
class CtyMap(CtyType[Dict[K, V]], Generic[K, V]):
    """
    Represents a map type in the Cty type system.

    Maps are collections of key-value pairs where all keys have the same type
    and all values have the same type.
    """
    ctype: ClassVar[str] = "map"
    key_type: CtyType[K] = attrs.field(kw_only=True)
    value_type: CtyType[V] = attrs.field(kw_only=True)
    value: Dict[K, V] = attrs.field(factory=dict, kw_only=True)

    def __attrs_post_init__(self):
        """Validate the map configuration."""
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
        Validate a value against this map type.

        Args:
            value: Value to validate

        Returns:
            The validated map value as a CtyValue

        Raises:
            ValidationError: If the value doesn't match this map type
        """
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔌🔍🔄 Validating value against CtyMap: {type(value).__name__}")

        # Handle None as empty map
        if value is None:
            logger.debug("🔌🔍✅ None value treated as empty map")
            return CtyValue(type_=self, value={})

        # Value must be a dictionary
        if not isinstance(value, dict):
            error_msg = f"Expected dictionary, got {type(value).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise ValidationError(error_msg)

        # Handle empty dictionary
        if not value:
            logger.debug("🔌🔍✅ Empty dictionary is valid")
            return CtyValue(type_=self, value={})

        # Validate each key-value pair
        validated_map = {}
        validation_errors = []

        for k, v in value.items():
            try:
                # Validate key
                validated_key = self._validate_key(k)
                # Validate value
                validated_value = self._validate_value(v)
                
                # Add to validated map
                validated_map[validated_key] = validated_value
                logger.debug(f"🔌🔍✅ Validated map entry: {k} -> {v}")
            except Exception as e:
                error_msg = f"Invalid map entry {k}: {v} -> {e}"
                logger.error(f"🔌❌🔄 {error_msg}")
                validation_errors.append(error_msg)

        if validation_errors:
            error_msg = "Map validation failed:\n" + "\n".join(validation_errors)
            logger.error(f"🔌❌🔄 {error_msg}")
            raise ValidationError(error_msg)

        logger.debug(f"🔌🔍✅ Map validated successfully with {len(validated_map)} entries")
        return CtyValue(type_=self, value=validated_map)

    def set(self, container: Dict[K, V], key: Any, value: Any) -> Dict[K, V]:
        """
        Set a key-value pair in a map.

        This operation is immutable - it returns a new map with the updated key-value pair.

        Args:
            container: The map to update
            key: The key to set
            value: The value to set

        Returns:
            A new map with the updated key-value pair
        """
        logger.debug(f"🔌📝🔄 Setting key {key} to value {value} in map")

        # Create a new map
        new_map = dict(container)

        # Validate and wrap the key and value
        validated_key = self._validate_key(key)
        validated_value = self._validate_value(value)

        # Set the key-value pair in the new map
        new_map[validated_key] = validated_value

        logger.debug(f"🔌📝✅ Key {key} set successfully")
        return new_map

    def get(self, container: Dict[K, V], key: Any, default: Any = None) -> Optional[V]:
        """
        Get a value from a map by key.

        Args:
            container: The map to get the value from
            key: The key to look up
            default: Value to return if key not found

        Returns:
            The value at the key, or the default if not found
        """
        logger.debug(f"🔌🔍🔄 Getting value for key {key} from map")

        try:
            # Validate the key
            validated_key = self._validate_key(key)

            # Search for the key in the map
            for k, v in container.items():
                # Compare keys - handle CtyValue keys
                if hasattr(k, 'value') and hasattr(validated_key, 'value'):
                    if k.value == validated_key.value:
                        logger.debug(f"🔌🔍✅ Found value for key {key}")
                        return v
                # Direct comparison
                elif k == validated_key:
                    logger.debug(f"🔌🔍✅ Found value for key {key}")
                    return v

            # Key not found
            logger.debug(f"🔌🔍⚠️ Key {key} not found in map, returning default")
            return default
        except Exception as e:
            logger.debug(f"🔌❌🔄 Error getting value: {e}")
            return default

    def delete(self, container: Dict[K, V], key: Any) -> Dict[K, V]:
        """
        Delete a key-value pair from a map.

        This operation is immutable - it returns a new map with the key-value pair removed.

        Args:
            container: The map to update
            key: The key to delete

        Returns:
            A new map with the key-value pair removed
        """
        logger.debug(f"🔌📝🔄 Deleting key {key} from map")

        # Create a new map
        new_map = {}

        try:
            # Validate the key
            validated_key = self._validate_key(key)

            # Copy all entries except the one to delete
            found = False
            for k, v in container.items():
                # Compare keys - handle CtyValue keys
                if hasattr(k, 'value') and hasattr(validated_key, 'value'):
                    if k.value == validated_key.value:
                        found = True
                        continue
                # Direct comparison
                elif k == validated_key:
                    found = True
                    continue

                # Copy the entry
                new_map[k] = v

            if found:
                logger.debug(f"🔌📝✅ Key {key} deleted successfully")
            else:
                logger.debug(f"🔌📝⚠️ Key {key} not found in map")

            return new_map
        except Exception as e:
            logger.debug(f"🔌❌🔄 Error deleting key: {e}")
            # If an error occurs, return original map
            return container

    def _validate_key(self, key: Any) -> K:
        """
        Validate a key against the key type.

        Args:
            key: The key to validate

        Returns:
            The validated key

        Raises:
            ValidationError: If the key is invalid
        """
        logger.debug(f"🔌🔍🔄 Validating map key: {key}")

        # If already a CtyValue with matching type, use directly
        from pyvider.cty.values import CtyValue
        if isinstance(key, CtyValue) and isinstance(key.type, type(self.key_type)):
            logger.debug("🔌🔍✅ Key is already a CtyValue with correct type")
            return key

        # Validate using key_type
        try:
            validated_key = self.key_type.validate(key)
            logger.debug(f"🔌🔍✅ Key validated successfully")
            return validated_key
        except Exception as e:
            error_msg = f"Invalid key: {e}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise ValidationError(error_msg) from e

    def _validate_value(self, value: Any) -> V:
        """
        Validate a value against the value type.

        Args:
            value: The value to validate

        Returns:
            The validated value

        Raises:
            ValidationError: If the value is invalid
        """
        logger.debug(f"🔌🔍🔄 Validating map value: {value}")

        # If already a CtyValue with matching type, use directly
        from pyvider.cty.values import CtyValue
        if isinstance(value, CtyValue) and isinstance(value.type, type(self.value_type)):
            logger.debug("🔌🔍✅ Value is already a CtyValue with correct type")
            return value

        # Validate using value_type
        try:
            validated_value = self.value_type.validate(value)
            logger.debug(f"🔌🔍✅ Value validated successfully")
            return validated_value
        except Exception as e:
            error_msg = f"Invalid value: {e}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise ValidationError(error_msg) from e

    def equal(self, other: CtyType) -> bool:
        """
        Check if this map type is equal to another type.

        Args:
            other: The other type to compare with

        Returns:
            True if the types are equal, False otherwise
        """
        logger.debug(f"🔌🔍🔄 Checking equality with {other.__class__.__name__}")

        if not isinstance(other, CtyMap):
            logger.debug(f"🔌❌🔄 Not equal: {other.__class__.__name__} is not CtyMap")
            return False

        # Check key type and value type equality
        key_equal = self.key_type.equal(other.key_type)
        value_equal = self.value_type.equal(other.value_type)

        result = key_equal and value_equal
        logger.debug(f"🔌🔍✅ CtyMap.equal: {result}")
        return result

    def usable_as(self, other: CtyType) -> bool:
        """
        Check if this map type can be used as another type.

        Args:
            other: The other type to check compatibility with

        Returns:
            True if this type can be used as the other type, False otherwise
        """
        logger.debug(f"🔌🔍🔄 Checking usability as {other.__class__.__name__}")

        if not isinstance(other, CtyMap):
            logger.debug(f"🔌❌🔄 Not usable as: {other.__class__.__name__} is not CtyMap")
            return False

        # Check key type and value type compatibility
        key_usable = self.key_type.usable_as(other.key_type)
        value_usable = self.value_type.usable_as(other.value_type)

        result = key_usable and value_usable
        logger.debug(f"🔌🔍✅ CtyMap.usable_as: {result}")
        return result

    def __str__(self) -> str:
        """Get string representation of the map type."""
        return f"map({self.key_type.__class__.__name__}, {self.value_type.__class__.__name__})"

    def __repr__(self) -> str:
        """Get detailed string representation of the map type."""
        return f"CtyMap(key_type={self.key_type!r}, value_type={self.value_type!r})"

# 🐍🏗️🐣
