#
# pyvider/cty/types/collections/map.py
#

"""
Map type implementation for the Cty type system.

CtyMap represents a map type with a fixed string key type and any value type.
This implementation strictly follows Go-CTY's map type semantics, which:
1. Uses string keys internally but maintains original CtyValue keys
2. Fails fast during validation (early error returns)
3. Maintains immutability for all operations
4. Preserves type safety throughout
"""

from typing import Any, ClassVar, Generic, Optional, TypeVar, cast, TypeGuard

from attrs import define, field

from pyvider.cty.exceptions import CtyMapValidationError
from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType

V = TypeVar('V')  # Value type is variable

@define(frozen=True, slots=True)
class CtyMap(CtyType[dict[str, V]], Generic[V]):
    """
    CtyMap represents a string-keyed map type in the Cty type system.

    Maps are key-value collections with string keys and a fixed value type.
    This implementation strictly follows go-cty's Map design, which only
    permits string keys and provides strong type guarantees for values.

    Attributes:
        key_type: CtyType for map keys (must be CtyString)
        value_type: CtyType for map values
        value: dictionary of validated values (optional, for pre-validated maps)
    """
    ctype: ClassVar[str] = "map"
    key_type: CtyType[str] = field(kw_only=True)
    value_type: CtyType[V] = field(kw_only=True)
    value: dict[str, "CtyValue"] = field(factory=dict, kw_only=True)

    def __attrs_post_init__(self) -> None:
        """
        Validate CtyMap configuration.

        Ensures the key_type is CtyString and value_type is a valid CtyType.
        Raises CtyMapValidationError on invalid configuration.
        """
        logger.debug("🔌🔍🔄 Validating CtyMap configuration")

        # Verify key_type is CtyString - this is a strict requirement
        from pyvider.cty.types.primitives import CtyString
        if not isinstance(self.key_type, CtyString):
            error_msg = f"Expected CtyType for key_type, got {type(self.key_type).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)

        # Verify value_type is a CtyType
        if not isinstance(self.value_type, CtyType):
            error_msg = f"Expected CtyType for value_type, got {type(self.value_type).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)

        logger.debug("🔌✅🔄 CtyMap configuration validated successfully")

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value conforms to this map type.

        Args:
            value: The value to validate (dict, None, or empty)

        Returns:
            A CtyValue wrapping the validated map

        Raises:
            CtyMapValidationError: If validation fails
        """
        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        logger.debug(f"🔌🔍🔄 Validating value as CtyMap: {type(value).__name__}")

        # Handle None or empty values - match/case for Python 3.10+
        match value:
            case None:
                logger.debug("🔌🔍✅ None value converted to empty map")
                result = CtyValue(type_=self, value={}, key_mapping={})
                return result
            case {}:
                logger.debug("🔌🔍✅ Empty dict is valid")
                result = CtyValue(type_=self, value={})
                result._key_mapping = {}  # Add empty key mapping
                return result
            case dict():
                # Continue with validation
                pass
            case _:
                # Fail fast for non-dict values
                error_msg = f"Expected dict, got {type(value).__name__}"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise CtyMapValidationError(error_msg)

        # Create new map for validated entries - Using string keys, not CtyValue keys
        validated_map: dict[str, CtyValue] = {}
        key_mapping: dict[str, CtyValue] = {}  # Track original CtyValue keys

        # Validate each key-value pair, failing fast on errors
        for k, v in value.items():
            try:
                # Validate key - must be a string
                if isinstance(k, CtyValue):
                    # Pre-validated CtyValue key
                    logger.debug(f"🔌🔍🔄 Processing pre-validated key of type {k.type.__class__.__name__}")
                    if not isinstance(k.type, self.key_type.__class__):
                        error_msg = f"Key type mismatch: expected {self.key_type.__class__.__name__}, got {k.type.__class__.__name__}"
                        logger.error(f"🔌❌🔄 {error_msg}")
                        raise CtyMapValidationError(error_msg)

                    if k.is_null or k.is_unknown:
                        error_msg = "Map keys cannot be null or unknown"
                        logger.error(f"🔌❌🔄 {error_msg}")
                        raise CtyMapValidationError(error_msg)

                    # Extract the string value from CtyValue for use as map key
                    map_key = str(k.value)
                    key_mapping[map_key] = k  # Store original CtyValue key
                    logger.debug(f"🔌🔍✅ Using string representation of pre-validated key: {map_key}")
                else:
                    # Raw key needs validation
                    logger.debug(f"🔌🔍🔄 Validating raw key: {k!r}")
                    try:
                        validated_key = self.key_type.validate(k)
                        if validated_key.is_null or validated_key.is_unknown:
                            error_msg = "Map keys cannot be null or unknown"
                            logger.error(f"🔌❌🔄 {error_msg}")
                            raise CtyMapValidationError(error_msg)

                        # Extract string value for use as map key
                        map_key = str(validated_key.value)
                        key_mapping[map_key] = validated_key  # Store validated CtyValue key
                        logger.debug(f"🔌🔍✅ Validated key to string: {map_key}")
                    except Exception as e:
                        error_msg = f"Invalid key {k!r}: {e}"
                        logger.error(f"🔌❌🔄 {error_msg}")
                        raise CtyMapValidationError(error_msg) from e

                # Validate value
                if isinstance(v, CtyValue):
                    # Pre-validated CtyValue
                    logger.debug(f"🔌🔍🔄 Processing pre-validated value of type {v.type.__class__.__name__}")
                    if not v.type.equal(self.value_type) and not v.type.usable_as(self.value_type):
                        error_msg = f"Value type mismatch: expected {self.value_type.__class__.__name__}, got {v.type.__class__.__name__}"
                        logger.error(f"🔌❌🔄 {error_msg}")
                        raise CtyMapValidationError(error_msg)

                    validated_value = v
                    logger.debug(f"🔌🔍✅ Using pre-validated value for key {map_key}")
                else:
                    # Raw value needs validation
                    logger.debug(f"🔌🔍🔄 Validating raw value for key {map_key}: {v!r}")
                    try:
                        validated_value = self.value_type.validate(v)
                        logger.debug(f"🔌🔍✅ Value validated successfully for key {map_key}")
                    except Exception as e:
                        error_msg = f"Invalid value for key {map_key}: {e}"
                        logger.error(f"🔌❌🔄 {error_msg}")
                        raise CtyMapValidationError(error_msg) from e

                # Add to validated map - using the string key, not a CtyValue
                validated_map[map_key] = validated_value
                logger.debug(f"🔌🔍✅ Added key-value pair to map, current size: {len(validated_map)}")

            except CtyMapValidationError:
                # Re-raise without wrapping to preserve error context
                raise
            except Exception as e:
                # Wrap other exceptions
                error_msg = f"Error processing map entry {k!r}: {v!r} -> {e}"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise CtyMapValidationError(error_msg) from e

        logger.debug(f"🔌🔍✅ Map validated successfully with {len(validated_map)} entries")
        result = CtyValue(type_=self, value=validated_map, key_mapping=key_mapping)
        return result

    def get(self, map_value: "CtyValue", key: Any, default: Optional["CtyValue"] = None) -> Optional["CtyValue"]:
        """
        Get a value from the map by key.

        Args:
            map_value: CtyValue containing the map
            key: Key to look up (can be string or CtyValue)
            default: Default value to return if key not found

        Returns:
            The value for the key, or default if not found

        Raises:
            TypeError: If map_value is not a CtyValue with CtyMap type
            CtyMapValidationError: If map_value is null or unknown
        """
        from pyvider.cty.values import CtyValue

        logger.debug(f"🔌🔍🔄 Getting value for key {key!r} from map")

        # Validate map_value is a map
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            error_msg = f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise TypeError(error_msg)

        # Cannot get from unknown or null values
        if map_value.is_null or map_value.is_unknown:
            error_msg = "Cannot get from null or unknown map"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)

        # Convert the key to a string to use as map key
        try:
            # For CtyValue keys, extract the string value
            if isinstance(key, CtyValue):
                str_key = str(key.value)
                logger.debug(f"🔌🔍🔄 Using string value from CtyValue key: {str_key}")
            else:
                # Validate the key first if it's not a CtyValue
                validated_key = self.key_type.validate(key)
                str_key = str(validated_key.value)
                logger.debug(f"🔌🔍🔄 Validated key to string: {str_key}")
        except Exception as e:
            logger.debug(f"🔌🔍⚠️ Key validation failed, returning default: {e}")
            return default

        # Search in the map using the string key
        map_data = map_value.value

        if str_key in map_data:
            logger.debug(f"🔌🔍✅ Found value for key: {str_key}")
            return map_data[str_key]

        logger.debug(f"🔌🔍⚠️ Key {str_key} not found, returning default")
        return default

    def set(self, map_value: "CtyValue", key: Any, value: Any) -> "CtyValue":
        """
        Set a value in a container.

        This operation is immutable - it returns a new CtyValue with the updated container.

        Args:
            map_value: CtyValue containing the map
            key: Key to set (can be string or CtyValue)
            value: Value to set

        Returns:
            A new CtyValue with the updated map

        Raises:
            TypeError: If map_value is not a CtyValue with CtyMap type
            CtyMapValidationError: If map_value is null or unknown, or validation fails
        """
        from pyvider.cty.values import CtyValue

        logger.debug(f"🔌📝🔄 Setting key {key!r} to value {value!r} in map")

        # Validate map_value is a map
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            error_msg = f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise TypeError(error_msg)

        # Cannot set on null/unknown maps
        if map_value.is_null or map_value.is_unknown:
            error_msg = "Cannot set on null or unknown map"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)

        # Create a new map with existing entries
        new_map = dict(map_value.value)
        # Get existing key mapping or create new one
        key_mapping = dict(getattr(map_value, '_key_mapping', {}))

        # Validate key and convert to string
        if isinstance(key, CtyValue):
            if not isinstance(key.type, self.key_type.__class__):
                error_msg = f"Key type mismatch: expected {self.key_type.__class__.__name__}, got {key.type.__class__.__name__}"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise CtyMapValidationError(error_msg)

            if key.is_null or key.is_unknown:
                error_msg = "Map keys cannot be null or unknown"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise CtyMapValidationError(error_msg)

            str_key = str(key.value)
            key_mapping[str_key] = key  # Store original CtyValue key
            logger.debug(f"🔌📝🔄 Using string from pre-validated key: {str_key}")
        else:
            # Validate raw key
            validated_key = self.key_type.validate(key)
            if validated_key.is_null or validated_key.is_unknown:
                error_msg = "Map keys cannot be null or unknown"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise CtyMapValidationError(error_msg)

            str_key = str(validated_key.value)
            key_mapping[str_key] = validated_key  # Store validated key
            logger.debug(f"🔌📝🔄 Validated key to string: {str_key}")

        # Validate value
        if isinstance(value, CtyValue):
            if not value.type.equal(self.value_type) and not value.type.usable_as(self.value_type):
                error_msg = f"Value type mismatch: expected {self.value_type.__class__.__name__}, got {value.type.__class__.__name__}"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise CtyMapValidationError(error_msg)

            validated_value = value
            logger.debug(f"🔌📝✅ Using pre-validated value")
        else:
            # Validate raw value
            validated_value = self.value_type.validate(value)
            logger.debug(f"🔌📝✅ Validated value")

        # Set the value using the string key
        new_map[str_key] = validated_value

        logger.debug(f"🔌📝✅ Set key {str_key} to value")

        result = CtyValue(type_=self, value=new_map, key_mapping=key_mapping)
        return result

    def delete(self, map_value: "CtyValue", key: Any) -> "CtyValue":
        """
        Delete a key from a map, returning a new map.

        This is an immutable operation that returns a new map without the specified key.

        Args:
            map_value: CtyValue containing the map
            key: Key to delete (can be string or CtyValue)

        Returns:
            A new CtyValue with the updated map

        Raises:
            TypeError: If map_value is not a CtyValue with CtyMap type
            CtyMapValidationError: If map_value is null or unknown
        """
        from pyvider.cty.values import CtyValue

        logger.debug(f"🔌📝🔄 Deleting key {key!r} from map")

        # Validate map_value is a map
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            error_msg = f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise TypeError(error_msg)

        # Cannot delete from null/unknown maps
        if map_value.is_null or map_value.is_unknown:
            error_msg = "Cannot delete from null or unknown map"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)

        # Create a new map without the key
        new_map = dict(map_value.value)
        # Get existing key mapping
        key_mapping = dict(getattr(map_value, '_key_mapping', {}))

        # Convert key to string
        try:
            if isinstance(key, CtyValue):
                str_key = str(key.value)
                logger.debug(f"🔌📝🔄 Using string from pre-validated key: {str_key}")
            else:
                # Validate raw key
                validated_key = self.key_type.validate(key)
                str_key = str(validated_key.value)
                logger.debug(f"🔌📝🔄 Validated key to string: {str_key}")
        except Exception as e:
            # If key validation fails, the key can't be in the map
            logger.debug(f"🔌📝⚠️ Key validation failed, map unchanged: {e}")
            return map_value

        # Remove the key if it exists
        if str_key in new_map:
            del new_map[str_key]
            # Also remove from key mapping if present
            if str_key in key_mapping:
                del key_mapping[str_key]
            logger.debug(f"🔌📝✅ Deleted key {str_key}")
        else:
            logger.debug(f"🔌📝⚠️ Key {str_key} not found, map unchanged")
            return map_value

        result = CtyValue(type_=self, value=new_map, key_mapping=key_mapping)
        return result

    def element_iterator(self, map_value: "CtyValue") -> "ElementIterator":
        """
        Get an iterator for the elements in a map.

        This follows go-cty's ElementIterator pattern for consistent
        iteration over collection types.

        Args:
            map_value: CtyValue containing the map

        Returns:
            An ElementIterator for the map

        Raises:
            TypeError: If map_value is not a CtyValue with CtyMap type
            CtyMapValidationError: If map_value is null or unknown
        """
        from pyvider.cty.values import CtyValue

        logger.debug(f"🔌🔍🔄 Creating element iterator for map")

        # Validate map_value is a map
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            error_msg = f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise TypeError(error_msg)

        # Cannot iterate null/unknown maps
        if map_value.is_null or map_value.is_unknown:
            error_msg = "Cannot iterate null or unknown map"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)

        # Get key mapping from the CtyValue
        key_mapping = getattr(map_value, '_key_mapping', {})

        # Create and return the iterator with key mapping
        return ElementIterator(self.key_type, map_value.value, key_mapping)

    def equal(self, other: CtyType) -> bool:
        """
        Check if this type equals another type.

        For maps, equality requires both key_type and value_type to be equal.

        Args:
            other: Type to compare with

        Returns:
            True if the types are equal
        """
        logger.debug(f"🔌🔍🔄 Checking equality with {type(other).__name__}")

        # Must be a CtyMap
        if not isinstance(other, CtyMap):
            logger.debug(f"🔌🔍❌ Not equal: {type(other).__name__} is not CtyMap")
            return False

        # Both key_type and value_type must be equal
        key_equal = self.key_type.equal(other.key_type)
        value_equal = self.value_type.equal(other.value_type)
        result = key_equal and value_equal

        logger.debug(f"🔌🔍✅ Equality check: {result}")
        return result

    def usable_as(self, other: CtyType) -> bool:
        """
        Check if this type can be used as another type.

        For maps, usability requires key_type and value_type to be usable
        as the corresponding types in the other map.

        Args:
            other: Type to check compatibility with

        Returns:
            True if this type can be used as the other type
        """
        logger.debug(f"🔌🔍🔄 Checking usability as {type(other).__name__}")

        # Must be a CtyMap
        if not isinstance(other, CtyMap):
            logger.debug(f"🔌🔍❌ Not usable as: {type(other).__name__} is not CtyMap")
            return False

        # Both key_type and value_type must be usable
        key_usable = self.key_type.usable_as(other.key_type)
        value_usable = self.value_type.usable_as(other.value_type)
        result = key_usable and value_usable

        logger.debug(f"🔌🔍✅ Usability check: {result}")
        return result

    def items(self):
        """Return an ordered iterator of (key, value) pairs."""
        iterator = self.element_iterator()
        while iterator.next():
            yield iterator.key(), iterator.value()
            
    def keys(self):
        """Return an ordered iterator of keys."""
        for key, _ in self.items():
            yield key

    def __eq__(self, other: object) -> bool:
        """
        Equality operator implementation.

        Args:
            other: Object to compare with

        Returns:
            True if equal
        """
        if not isinstance(other, CtyMap):
            return False
        return self.equal(other)

    def __hash__(self) -> int:
        """
        Hash implementation for use in sets and as dict keys.

        Returns:
            Hash value
        """
        return hash((self.__class__, hash(self.key_type), hash(self.value_type)))

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            String representation
        """
        return f"map({self.key_type}, {self.value_type})"

    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.

        Returns:
            Detailed string representation
        """
        return f"CtyMap(key_type={repr(self.key_type)}, value_type={repr(self.value_type)})"


class ElementIterator:
    """
    Iterator for map elements.

    This follows go-cty's ElementIterator pattern for consistent
    iteration over collection types. For maps, it iterates over
    string keys but returns CtyValue instances representing keys and values.
    """

    def __init__(self, 
                 key_type: "CtyType", 
                 map_data: dict[str, "CtyValue"], 
                 key_mapping: dict[str, "CtyValue"]):
        """
        Initialize the iterator.

        Args:
            key_type: The key type to use when creating CtyValue keys
            map_data: dictionary of string keys to value pairs to iterate over
            key_mapping: mapping of string keys to original CtyValue keys
        """
        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        self.key_type = key_type
        self.items = []

        # Convert string keys to CtyValue objects for iteration
        # Use original keys from key_mapping if available
        for string_key, value in map_data.items():
            key_value = key_mapping.get(string_key)
            if key_value is None:
                # If original key not found, reconstruct it
                key_value = CtyValue(type_=key_type, value=string_key)
            self.items.append((key_value, value))

        # Sort items by key for consistent iteration order (like Go)
        self.items.sort(key=lambda item: item[0].value)
        self.index = 0

    def next(self) -> bool:
        """
        Advance to the next element.

        Returns:
            True if there is another element, False if at the end
        """
        if self.index < len(self.items):
            self.index += 1
            return True
        return False

    def key(self) -> "CtyValue":
        """
        Get the current key as a CtyValue.

        Returns:
            The current key as a CtyValue

        Raises:
            IndexError: If called before next() or after reaching the end
        """
        if self.index == 0 or self.index > len(self.items):
            raise IndexError("ElementIterator: no current element")
        return self.items[self.index - 1][0]

    def value(self) -> "CtyValue":
        """
        Get the current value.

        Returns:
            The current value

        Raises:
            IndexError: If called before next() or after reaching the end
        """
        if self.index == 0 or self.index > len(self.items):
            raise IndexError("ElementIterator: no current element")
        return self.items[self.index - 1][1]

# 🐍🏗️🐣
