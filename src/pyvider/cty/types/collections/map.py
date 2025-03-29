#
# pyvider/cty/types/collections/map.py
#

from typing import Any, ClassVar, Dict, Generic, Optional, TypeVar, final
from attrs import define, evolve, field
from pyvider.cty.exceptions import ValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.logger import logger

K = TypeVar('K')
V = TypeVar('V')

@final
@define(frozen=True, slots=True)
class CtyMap(CtyType[Dict[K, V]], Generic[K, V]):
    """
    CtyMap represents a map type in the Cty type system.

    Maps are collections of key-value pairs where all keys have the same type
    and all values have the same type. In Cty, map keys are typically strings.
    """
    ctype: ClassVar[str] = "map"
    key_type: CtyType[K] = field(kw_only=True)  # Mandatory as keyword-only
    value_type: CtyType[V] = field(kw_only=True)  # Mandatory as keyword-only
    value: Dict[Any, Any] = field(factory=dict, kw_only=True)  # Allow passing value via kw_only

    def __attrs_post_init__(self) -> None:
        """Validate key_type and value_type after initialization."""
        logger.debug("🔌📝🔄 Validating CtyMap initialization")

        if not isinstance(self.key_type, CtyType):
            error_msg = f"Expected CtyType for key_type, got {type(self.key_type)}"
            logger.error(f"🔌❗❌ {error_msg}")
            raise ValidationError(error_msg)

        if not isinstance(self.value_type, CtyType):
            error_msg = f"Expected CtyType for value_type, got {type(self.value_type)}"
            logger.error(f"🔌❗❌ {error_msg}")
            raise ValidationError(error_msg)

        logger.debug("🔌📝✅ CtyMap initialization valid")

    def validate(self, value: Any) -> "CtyValue":
        """Validate that the given value conforms to this map type."""
        logger.debug(f"🔌📝🔄 Validating value as CtyMap: {type(value).__name__}")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        # Handle None/empty
        if value is None or not value:
            logger.debug("🔌📝✅ Creating empty map")
            return CtyValue(type_=self, value={})

        # Ensure input is a dictionary
        if not isinstance(value, dict):
            logger.debug(f"🔌❗❌ Expected dict, got {type(value).__name__}")
            raise ValidationError(f"Expected dict, got {type(value).__name__}")

        # Validate each key-value pair
        validated = {}
        validation_errors = []

        for k, v in value.items():
            try:
                # Handle key validation - always ensure it's a CtyValue
                if isinstance(k, CtyValue) and isinstance(k.type, self.key_type.__class__):
                    validated_key = k
                    logger.debug(f"🔌📝✅ Key is already a CtyValue: {k}")
                else:
                    # Validate raw key
                    raw_key = self.key_type.validate(k)
                    validated_key = raw_key  # Already a CtyValue from validate
                    logger.debug(f"🔌📝✅ Validated key: {k} -> {validated_key}")

                # Handle value validation - always ensure it's a CtyValue
                if isinstance(v, CtyValue) and isinstance(v.type, self.value_type.__class__):
                    validated_value = v
                    logger.debug(f"🔌📝✅ Value is already a CtyValue: {v}")
                else:
                    # Validate raw value
                    validated_value = self.value_type.validate(v)
                    logger.debug(f"🔌📝✅ Validated value: {v} -> {validated_value}")

                validated[validated_key] = validated_value
            except Exception as e:
                error_msg = f"Key {k}: {v} -> {e!s}"
                logger.debug(f"🔌❗❌ {error_msg}")
                validation_errors.append(error_msg)

        if validation_errors:
            error_msg = "CtyMap validation failed:\n" + "\n".join(validation_errors)
            logger.debug(f"🔌❗❌ {error_msg}")
            raise ValidationError(error_msg)

        logger.debug(f"🔌📝✅ Successfully validated map with {len(validated)} items")
        return CtyValue(type_=self, value=validated)

    def element(self, container: Any, key: Any) -> "CtyValue":
        """
        Get a value from a map by key (Go-CTY style).
        
        Args:
            container: Map container (CtyValue or dict)
            key: Key to look up (native or CtyValue)
            
        Returns:
            Value at the key as a CtyValue
        """
        logger.debug(f"🔌🔍🔄 Getting element for key: {key}")

        # Import here to avoid circular imports
        from pyvider.cty.values import CtyValue

        # Handle container
        if isinstance(container, CtyValue):
            container_map = container.value
        elif isinstance(container, dict):
            container_map = container
        else:
            raise ValidationError(f"Expected map container, got {type(container).__name__}")

        # Validate key
        try:
            search_key = self._validate_key(key)
        except Exception as e:
            logger.error(f"🔌❗❌ Invalid key: {e}")
            raise ValidationError(f"Invalid key: {e}")

        # Search for the key
        for k, v in container_map.items():
            # Compare by value, not identity
            if hasattr(k, 'value') and hasattr(search_key, 'value') and k.value == search_key.value:
                return v

        # Key not found
        raise KeyError(f"Key not found: {key}")

    def get(self, container: Any, key: Any, default: Any = None) -> "CtyValue":
        """
        Get a value from the map by key, with a default if not found.
        
        Args:
            container: Map container (CtyValue or dict)
            key: Key to look up
            default: Value to return if key not found
            
        Returns:
            Value at the key as a CtyValue, or default
        """
        logger.debug(f"🔌🔍🔄 Getting value for key: {key}")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        # Handle container
        if isinstance(container, CtyValue):
            container_map = container.value
        elif isinstance(container, dict):
            container_map = container
        else:
            logger.debug(f"🔌❗⚠️ Invalid container type: {type(container).__name__}")
            return default

        try:
            # Validate key for consistent comparison
            if isinstance(key, CtyValue) and isinstance(key.type, self.key_type.__class__):
                search_key = key
            else:
                try:
                    search_key = self.key_type.validate(key)
                except Exception as e:
                    logger.debug(f"🔌🔍⚠️ Key validation failed: {e}")
                    return default

            # Find matching key by value comparison
            for k, v in container_map.items():
                if hasattr(k, 'value') and hasattr(search_key, 'value'):
                    if k.value == search_key.value:
                        logger.debug(f"🔌🔍✅ Found value for key: {k.value}")
                        return v
                elif k == search_key:
                    logger.debug(f"🔌🔍✅ Found value for key: {k}")
                    return v

            logger.debug(f"🔌🔍⚠️ Key not found, returning default")
            return default
        except Exception as e:
            logger.debug(f"🔌❗⚠️ Error getting key: {e}")
            return default

    def set(self, container: Any, key: Any, value: Any) -> "CtyValue":
        """
        Set a key-value pair in a map (Go-CTY style).
        
        Args:
            container: The map container (CtyValue or dict)
            key: The key to set
            value: The value to set
            
        Returns:
            A new CtyValue with the key-value pair set
        """
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔌📝🔄 Setting value for key: {key}")

        # Handle container
        if isinstance(container, CtyValue):
            container_map = dict(container.value)  # Make a copy
        elif isinstance(container, dict):
            container_map = dict(container)  # Make a copy
        else:
            error_msg = f"Expected map container, got {type(container).__name__}"
            logger.error(f"🔌❗❌ {error_msg}")
            raise ValidationError(error_msg)

        # Validate key and value
        validated_key = self._validate_key(key)
        validated_value = self._validate_value(value)

        # Find and replace existing key or add new key-value pair
        found = False
        new_map = {}

        for k, v in container_map.items():
            if hasattr(k, 'value') and hasattr(validated_key, 'value') and k.value == validated_key.value:
                # Replace with new value
                new_map[k] = validated_value
                found = True
            else:
                # Keep existing key-value pair
                new_map[k] = v

        # If key not found, add new key-value pair
        if not found:
            new_map[validated_key] = validated_value

        # Return new map
        logger.debug(f"🔌📝✅ Set value for key {key} successfully")
        return CtyValue(type_=self, value=new_map)

    def delete(self, container: Any, key: Any) -> "CtyValue":
        """
        Delete a key from a map (Go-CTY style).
        
        Args:
            container: The map container (CtyValue or dict) 
            key: The key to delete
            
        Returns:
            A new CtyValue with the key removed
        """
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔌📝🔄 Deleting key: {key}")

        # Handle container
        if isinstance(container, CtyValue):
            container_map = dict(container.value)  # Make a copy
        elif isinstance(container, dict):
            container_map = dict(container)  # Make a copy
        else:
            error_msg = f"Expected map container, got {type(container).__name__}"
            logger.error(f"🔌❗❌ {error_msg}")
            raise ValidationError(error_msg)

        # Validate key
        try:
            validated_key = self._validate_key(key)
        except Exception as e:
            logger.debug(f"🔌❗⚠️ Key validation failed: {e}")
            # If key validation fails, return the original container unchanged
            return container if isinstance(container, CtyValue) else CtyValue(type_=self, value=container_map)

        # Filter out the key
        new_map = {}
        removed = False

        for k, v in container_map.items():
            if hasattr(k, 'value') and hasattr(validated_key, 'value') and k.value == validated_key.value:
                removed = True
                continue
            new_map[k] = v

        # If key not found, no change
        if not removed:
            logger.debug(f"🔌📝⚠️ Key {key} not found, no changes made")
            return container if isinstance(container, CtyValue) else CtyValue(type_=self, value=container_map)

        # Return new map
        logger.debug(f"🔌📝✅ Deleted key {key} successfully")
        return CtyValue(type_=self, value=new_map)

    def _validate_key(self, key: Any) -> "CtyValue":
        """Validate and wrap a key with the appropriate type."""
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔌🔍🔄 Validating key: {key}")

        # Already a CtyValue with the right type?
        if isinstance(key, CtyValue) and isinstance(key.type, self.key_type.__class__):
            logger.debug(f"🔌🔍✅ Key is already a valid CtyValue")
            return key

        # Validate raw key
        try:
            validated = self.key_type.validate(key)
            logger.debug(f"🔌🔍✅ Validated key: {key} -> {validated}")
            return validated
        except Exception as e:
            error_msg = f"Invalid key: {e}"
            logger.error(f"🔌❗❌ {error_msg}")
            raise ValidationError(error_msg)

    def _validate_value(self, value: Any) -> "CtyValue":
        """Validate and wrap a value with the appropriate type."""
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔌🔍🔄 Validating value: {value}")

        # Already a CtyValue with the right type?
        if isinstance(value, CtyValue) and isinstance(value.type, self.value_type.__class__):
            logger.debug(f"🔌🔍✅ Value is already a valid CtyValue")
            return value

        # Validate raw value
        try:
            validated = self.value_type.validate(value)
            logger.debug(f"🔌🔍✅ Validated value: {value} -> {validated}")
            return validated
        except Exception as e:
            error_msg = f"Invalid value: {e}"
            logger.error(f"🔌❗❌ {error_msg}")
            raise ValidationError(error_msg)

    def usable_as(self, other: "CtyType") -> bool:
        """
        Check if this type can be used as the other type.

        Args:
            other: The other type to check against

        Returns:
            True if this type can be used as the other type
        """
        if not isinstance(other, CtyMap):
            logger.debug(f"🔌📝❌ CtyMap.usable_as: False (other is {type(other).__name__})")
            return False

        key_usable = self.key_type.usable_as(other.key_type)
        value_usable = self.value_type.usable_as(other.value_type)

        result = key_usable and value_usable
        logger.debug(f"🔌📝✅ CtyMap.usable_as: {result}")
        return result

    def equal(self, other: "CtyType") -> bool:
        """
        Check if this type is equal to the other type.

        Args:
            other: The other type to check against

        Returns:
            True if the types are equal
        """
        if not isinstance(other, CtyMap):
            logger.debug(f"🔌📝❌ CtyMap.equal: False (other is {type(other).__name__})")
            return False

        key_equal = self.key_type.equal(other.key_type)
        value_equal = self.value_type.equal(other.value_type)

        result = key_equal and value_equal
        logger.debug(f"🔌📝✅ CtyMap.equal: {result}")
        return result

    def __eq__(self, other):
        """
        Check if this map is equal to another map.

        Args:
            other: The other map to check against

        Returns:
            True if the maps are equal
        """
        if not isinstance(other, CtyMap):
            return False

        # Check key type and value type equality
        if not self.key_type.__class__ == other.key_type.__class__ or not self.value_type.__class__ == other.value_type.__class__:
            return False

        # Check if maps have the same number of entries
        if len(self.value) != len(other.value):
            return False

        # For each key-value pair in self.value, check if it exists in other.value
        for self_key, self_val in self.value.items():
            # Find matching key in other.value
            found = False
            for other_key, other_val in other.value.items():
                # Try value comparison for keys
                if (hasattr(self_key, 'value') and hasattr(other_key, 'value') and
                    self_key.value == other_key.value):
                    # Compare values
                    if hasattr(self_val, 'value') and hasattr(other_val, 'value'):
                        if self_val.value != other_val.value:
                            return False
                    elif self_val != other_val:
                        return False
                    found = True
                    break
                # Direct equality comparison
                elif self_key == other_key:
                    if self_val != other_val:
                        return False
                    found = True
                    break

            if not found:
                return False

        return True

    def __iter__(self):
        """
        Iterate over the map keys.
        
        Returns:
            An iterator over the map keys
        """
        return iter(self.value.keys())

    def __str__(self) -> str:
        """
        Get a string representation of this map type.

        Returns:
            A string representation
        """
        return f"map({self.value_type.__class__.__name__})"

    def __repr__(self) -> str:
        """
        Get a detailed string representation of this map.

        Returns:
            A detailed string representation
        """
        return f"CtyMap(key_type={self.key_type!r}, value_type={self.value_type!r})"

# 🐍🏗️🐣
