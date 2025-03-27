#
# pyvider/cty/types/collections/map.py
#

from typing import Any, ClassVar, Dict, Generic, TypeVar, final
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
    value: Dict[K, V] = field(factory=dict, kw_only=True)  # Allow passing value via kw_only

    def __attrs_post_init__(self) -> None:
        """Validate key_type and value_type after initialization."""
        if not isinstance(self.key_type, CtyType):
            raise ValidationError(
                f"Expected CtyType for key_type, got {type(self.key_type)}"
            )
        if not isinstance(self.value_type, CtyType):
            raise ValidationError(
                f"Expected CtyType for value_type, got {type(self.value_type)}"
            )

    def validate(self, value: Any) -> "CtyMap":
        """
        Validate that the given value conforms to this map type.

        Args:
            value: The value to validate

        Returns:
            A new CtyMap with the validated value

        Raises:
            ValidationError: If validation fails
        """
        logger.debug(f"🔌📝🔄 Validating value as CtyMap: {type(value).__name__}")

        if value is None:
            logger.debug("🔌📝✅ Returning empty map for None value")
            return evolve(self, value={})

        if not isinstance(value, dict):
            logger.debug(f"🔌❗❌ Expected dict, got {type(value).__name__}")
            raise ValidationError(f"Expected dict, got {type(value).__name__}")

        if not value:
            logger.debug("🔌📝✅ Returning empty map for empty dict")
            return evolve(self, value={})

        validated = {}
        validation_errors = []

        for k, v in value.items():
            try:
                # Check if key is already a CtyType instance of the expected type
                if isinstance(k, CtyType) and k.__class__ == self.key_type.__class__:
                    validated_key = k
                    logger.debug(f"🔌📝✅ Key is already a {self.key_type.__class__.__name__}, no validation needed")
                else:
                    validated_key = self.key_type.validate(k)

                # Check if value is already a CtyType instance of the expected type
                if isinstance(v, CtyType) and v.__class__ == self.value_type.__class__:
                    validated_value = v
                    logger.debug(f"🔌📝✅ Value is already a {self.value_type.__class__.__name__}, no validation needed")
                else:
                    validated_value = self.value_type.validate(v)

                validated[validated_key] = validated_value
                logger.debug(f"🔌📝✅ Validated key-value pair: {validated_key} -> {validated_value}")
            except Exception as e:
                error_msg = f"Key {k}: {v} -> {e!s}"
                logger.debug(f"🔌❗❌ {error_msg}")
                validation_errors.append(error_msg)

        if validation_errors:
            error_msg = "CtyMap validation failed:\n" + "\n".join(validation_errors)
            logger.debug(f"🔌❗❌ {error_msg}")
            raise ValidationError(error_msg)

        logger.debug(f"🔌📝✅ Successfully validated map with {len(validated)} items")
        return evolve(self, value=validated)

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get a value from the map by key.

        Args:
            key: The key to look up
            default: The default value to return if key is not found

        Returns:
            The value associated with the key, or the default value
        """
        try:
            # If key is already a CtyType instance of the expected type
            if isinstance(key, CtyType) and key.__class__ == self.key_type.__class__:
                validated_key = key
            else:
                validated_key = self.key_type.validate(key)

            # Try to find the key in the map
            for k, v in self.value.items():
                if k == validated_key:
                    return v

            return default
        except Exception as e:
            logger.debug(f"🔌❗⚠️ Error getting key {key}: {e}")
            return default

    def set(self, key: Any, value: Any) -> "CtyMap":
        """
        Set a key-value pair in the map.

        Args:
            key: The key to set
            value: The value to set

        Returns:
            A new CtyMap with the key-value pair set

        Raises:
            ValidationError: If the key or value cannot be validated
        """
        try:
            # Validate the key
            if isinstance(key, CtyType) and key.__class__ == self.key_type.__class__:
                validated_key = key
            else:
                validated_key = self.key_type.validate(key)

            # Validate the value
            if isinstance(value, CtyType) and value.__class__ == self.value_type.__class__:
                validated_value = value
            else:
                validated_value = self.value_type.validate(value)

            # Create a new map with the updated key-value pair
            new_value = dict(self.value)
            new_value[validated_key] = validated_value

            logger.debug(f"🔌📝✅ Set key-value pair: {validated_key} -> {validated_value}")
            return evolve(self, value=new_value)
        except Exception as e:
            logger.debug(f"🔌❗❌ Failed to set key-value pair: {e}")
            raise ValidationError(f"Failed to set key-value pair: {e}")

    def delete(self, key: Any) -> "CtyMap":
        """
        Delete a key from the map.

        Args:
            key: The key to delete

        Returns:
            A new CtyMap with the key deleted
        """
        try:
            # Validate the key
            if isinstance(key, CtyType) and key.__class__ == self.key_type.__class__:
                validated_key = key
            else:
                validated_key = self.key_type.validate(key)

            # Create a new map without the key
            new_value = {}
            keys_to_delete = []

            # Find keys to delete by comparing value, not reference
            for k in self.value:
                if isinstance(k, CtyType) and k.value == validated_key.value:
                    keys_to_delete.append(k)

            # Copy all key-value pairs except those to be deleted
            for k, v in self.value.items():
                if k not in keys_to_delete:
                    new_value[k] = v

            if keys_to_delete:
                logger.debug(f"🔌📝✅ Deleted {len(keys_to_delete)} keys")
            else:
                logger.debug(f"🔌📝⚠️ Key not found: {validated_key}")

            return evolve(self, value=new_value)
        except Exception as e:
            logger.debug(f"🔌❗⚠️ Error deleting key {key}: {e}")
            # Return unchanged map on error
            return self

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
        if not self.key_type == other.key_type or not self.value_type == other.value_type:
            return False

        # Check if maps have the same number of entries
        if len(self.value) != len(other.value):
            return False

        # For each key-value pair in self.value, check if it exists in other.value
        for self_key, self_val in self.value.items():
            # Find matching key in other.value
            found = False
            for other_key, other_val in other.value.items():
                if self_key == other_key:
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
        return iter(self.value)

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
