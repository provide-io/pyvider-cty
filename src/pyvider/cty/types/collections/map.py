#
# pyvider/cty/types/collections/map.py
#

"""
Map type implementation for the Cty type system.

This module provides a complete implementation of the Map type for the Cty type system,
following Go-CTY's map semantics. Maps are collections of key-value pairs with string
keys and values of a consistent type. Key features include:

1. String-keyed design with support for CtyValue key representation
2. Immutable operations that return new instances on modification
3. Strict type checking and validation
4. Support for internal key mapping between string keys and CtyValue keys
5. Consistent iteration order through ElementIterator

Maps serve a similar role to Python dictionaries but with added type safety
and immutability guarantees.
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
    String-keyed map type in the Cty type system.

    CtyMap implements a mapping type with string keys and a uniform value type.
    Maps are immutable collections that support key-value operations similar to
    Python dictionaries while maintaining strict type safety. All maps use string
    keys internally but preserve CtyValue key objects for type integrity.

    Unlike Python dictionaries, CtyMap enforces consistent value types and
    never modifies the original structure during operations. All operations
    return new instances.

    Attributes:
        ctype (ClassVar[str]): Type identifier constant, always "map".
        key_type (CtyType[str]): Type for map keys, must be CtyString.
        value_type (CtyType[V]): Type for map values, can be any CtyType.
        value (dict[str, CtyValue]): Optional pre-validated map content.

    Examples:
        Creating a map type:
        >>> from pyvider.cty import CtyString, CtyNumber
        >>> string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        >>> number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())

        Validating a map:
        >>> data = {"name": "Alice", "email": "alice@example.com"}
        >>> validated = string_map.validate(data)
    """
    ctype: ClassVar[str] = "map"
    key_type: CtyType[str] = field(kw_only=True)
    value_type: CtyType[V] = field(kw_only=True)
    value: dict[str, "CtyValue"] = field(factory=dict, kw_only=True)

    def __attrs_post_init__(self) -> None:
        """
        Validate CtyMap configuration after initialization.

        Performs sanity checks on the map type configuration to ensure that:
        1. The key_type is a valid CtyString type
        2. The value_type is a valid CtyType instance

        Raises:
            CtyMapValidationError: If key_type is not CtyString or value_type is invalid
        """
        logger.debug("🔌🔍🔄 Validating CtyMap configuration")

        # Verify key_type is CtyString - this is a strict requirement
        from pyvider.cty.types.primitives import CtyString
        if not isinstance(self.key_type, CtyString):
            error_msg = f"Map key type must be CtyString, got {type(self.key_type).__name__}"
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
        Validate a value against this map type.

        Performs comprehensive validation of the input value to ensure it conforms
        to this map type's requirements. This method handles:

        1. Empty values (None, {}) as valid empty maps
        2. Dictionary-like values with proper key-value validation
        3. Pre-validated CtyValue instances of compatible types
        4. Type conversion where possible for keys and values
        5. Key mapping between string keys and CtyValue keys

        The validation process is "fail-fast", raising errors as soon as invalid
        data is encountered rather than accumulating errors.

        Args:
            value: The value to validate, typically a dict-like object, None for
                  empty map, or a pre-validated CtyValue

        Returns:
            CtyValue: A validated map value wrapped in a CtyValue with type information

        Raises:
            CtyMapValidationError: If validation fails for any reason, with a detailed
                                  error message explaining the failure
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

        Retrieves a value from the map using the provided key. The key can be:
        1. A string that matches a key in the map
        2. A CtyValue with a string value that matches a key in the map
        3. Any value that can be validated as a string

        If the key is not found, the default value is returned.

        Args:
            map_value: CtyValue containing the map to search in
            key: The key to look up (string, CtyValue, or convertible value)
            default: Value to return if key not found (defaults to None)

        Returns:
            The value associated with the key, or the default if not found

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
        Set a value in a map, returning a new map.

        This is an immutable operation that:
        1. Creates a new map with all existing entries
        2. Validates the key and value
        3. Sets the validated value at the validated key
        4. Returns the new map as a CtyValue

        The original map is not modified.

        Args:
            map_value: CtyValue containing the map to modify
            key: The key to set (string, CtyValue, or convertible value)
            value: The value to set at the key (raw value or CtyValue)

        Returns:
            A new CtyValue containing the updated map

        Raises:
            TypeError: If map_value is not a CtyValue with CtyMap type
            CtyMapValidationError: If validation fails for key or value
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

        This is an immutable operation that:
        1. Creates a new map with all existing entries except the deleted key
        2. Returns the new map as a CtyValue

        If the key doesn't exist, the original map is returned unchanged.
        The original map is never modified.

        Args:
            map_value: CtyValue containing the map to modify
            key: The key to delete (string, CtyValue, or convertible value)

        Returns:
            A new CtyValue containing the map without the deleted key

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

        Creates an ElementIterator for consistent iteration over map elements.
        The iterator preserves the map's key-value pairs and supports accessing
        both keys and values during iteration. Map elements are sorted by key
        for consistent iteration order.

        Args:
            map_value: CtyValue containing the map to iterate over

        Returns:
            An ElementIterator that provides access to keys and values

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

        Two map types are equal if:
        1. They are both CtyMap instances
        2. They have equal key types
        3. They have equal value types

        This implements strict type equality for the Cty type system.

        Args:
            other: The type to compare with

        Returns:
            True if the types are equal, False otherwise
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

        A map type is usable as another type if:
        1. The other type is also a CtyMap
        2. This map's key type is usable as the other map's key type
        3. This map's value type is usable as the other map's value type

        This implements type compatibility checking for the Cty type system.

        Args:
            other: The target type to check compatibility with

        Returns:
            True if this type can be used as the other type, False otherwise
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
        """
        Return an ordered iterator of (key, value) pairs.

        This is a convenience method that creates an ElementIterator and
        yields key-value pairs in order. Keys are sorted for consistent iteration.

        Returns:
            Generator yielding (key, value) pairs from the map
        """
        iterator = self.element_iterator()
        while iterator.next():
            yield iterator.key(), iterator.value()

    def keys(self):
        """
        Return an ordered iterator of map keys.

        This is a convenience method that creates an ElementIterator and
        yields only the keys in order. Keys are sorted for consistent iteration.

        Returns:
            Generator yielding keys from the map
        """
        for key, _ in self.items():
            yield key

    def __eq__(self, other: object) -> bool:
        """
        Equality operator implementation.

        Implements the == operator for CtyMap instances.
        Delegates to the equal() method for type-specific equality logic.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise
        """
        if not isinstance(other, CtyMap):
            return False
        return self.equal(other)

    def __hash__(self) -> int:
        """
        Hash implementation for use in sets and as dict keys.

        Makes CtyMap instances usable as dictionary keys and in sets.
        The hash is based on the class and the hash of key and value types.

        Returns:
            A hash value based on the type information
        """
        return hash((self.__class__, hash(self.key_type), hash(self.value_type)))

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns a concise string representation suitable for display
        to users, showing the map type with key and value types.

        Returns:
            A string representation of the map type
        """
        return f"map({self.key_type}, {self.value_type})"

    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.

        Returns a more detailed string representation that includes
        implementation details useful for debugging.

        Returns:
            A detailed string representation of the map type
        """
        return f"CtyMap(key_type={repr(self.key_type)}, value_type={repr(self.value_type)})"


class ElementIterator:
    """
    Iterator for map elements with consistent ordering.

    ElementIterator provides a standardized way to iterate over map elements
    while maintaining consistent ordering and preserving type information.
    It follows Go-CTY's iterator pattern, with next(), key(), and value() methods.

    Map elements are sorted by key for consistent iteration order.

    Attributes:
        key_type: The key type to use when creating CtyValue keys
        items: The sorted list of (key, value) pairs to iterate over
        index: The current position in the iteration
    """

    def __init__(self,
                 key_type: "CtyType",
                 map_data: dict[str, "CtyValue"],
                 key_mapping: dict[str, "CtyValue"]):
        """
        Initialize the iterator with map data and key mapping.

        Prepares a sorted list of (key, value) pairs from the map data,
        using the original CtyValue keys from key_mapping where available.

        Args:
            key_type: The key type to use when creating CtyValue keys
            map_data: Dictionary of string keys to value pairs to iterate over
            key_mapping: Mapping of string keys to original CtyValue keys
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
        Advance to the next element in the iteration.

        Moves the iterator to the next element and returns whether
        there is a next element available.

        Returns:
            True if there is a next element, False if at the end
        """
        if self.index < len(self.items):
            self.index += 1
            return True
        return False

    def key(self) -> "CtyValue":
        """
        Get the current key as a CtyValue.

        Retrieves the key at the current iterator position.
        Must be called after next() returns True.

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

        Retrieves the value at the current iterator position.
        Must be called after next() returns True.

        Returns:
            The current value as a CtyValue

        Raises:
            IndexError: If called before next() or after reaching the end
        """
        if self.index == 0 or self.index > len(self.items):
            raise IndexError("ElementIterator: no current element")
        return self.items[self.index - 1][1]

# 🐍🏗️🐣
