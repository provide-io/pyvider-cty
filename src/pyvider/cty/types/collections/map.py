#
# pyvider/cty/types/collections/map.py
#

"""
Map type implementation for the Cty type system.

This module provides a complete implementation of the Map type for the Cty type system,
following go-cty's map semantics. Maps are collections of key-value pairs with string
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

from attrs import define, field, evolve

# Assuming CtyValue is imported correctly elsewhere, e.g., from pyvider.cty.values import CtyValue
# Assuming CtyString is imported correctly elsewhere, e.g., from pyvider.cty.types.primitives import CtyString
from pyvider.cty.exceptions import CtyMapValidationError, CtyValidationError
from pyvider.telemetry import logger
from pyvider.cty.types.base import CtyType
# These imports might need adjustment based on your actual project structure
from pyvider.cty.values import CtyValue
from pyvider.cty.types.primitives import CtyString


V = TypeVar('V')  # Value type is variable

@define(frozen=True, slots=True)
class CtyMap(CtyType[dict[str, V]], Generic[V]):
    """
    String-keyed map type in the Cty type system.

    (Docstring unchanged - see previous context)
    """
    ctype: ClassVar[str] = "map"
    key_type: CtyType[str] = field(kw_only=True)
    value_type: CtyType[V] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        """
        Validate CtyMap configuration after initialization.
        (Function body unchanged - see previous context)
        """
        logger.debug("🔌🔍🔄 Validating CtyMap configuration")
        if not isinstance(self.key_type, CtyString):
            error_msg = f"Map key type must be CtyString, got {type(self.key_type).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)
        if not isinstance(self.value_type, CtyType):
            error_msg = f"Expected CtyType for value_type, got {type(self.value_type).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)
        logger.debug("🔌✅🔄 CtyMap configuration validated successfully")

    def validate(self, value: Any) -> CtyValue:
        """
        Validate a value against this map type.
        (Docstring unchanged)
        """
        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue
        from pyvider.cty.types.primitives import CtyString

        logger.debug(f"🔌🔍🔄 Validating value as CtyMap: {type(value).__name__}")

        # --- Handle Input Type ---
        input_dict: Optional[dict] = None
        if value is None:
            logger.debug("🔌🔍✅ None value converted to empty map")
            return CtyValue(vtype=self, value={}, key_mapping={})
        elif isinstance(value, dict):
            input_dict = value
        elif isinstance(value, CtyValue):
            logger.debug("🔌🔍🔄 Input is a CtyValue, checking type...")
            if isinstance(value.type, CtyMap):
                if self.equal(value.type):
                    logger.debug("🔌🔍✅ Input CtyValue has matching map type, returning as is")
                    return value
                elif value.type.usable_as(self):
                    logger.debug("🔌🔍🔄 Input CtyValue has usable map type, attempting conversion/validation")
                    try:
                        # Use public properties/methods
                        inner_value = value.value # Access public property
                        inner_key_mapping = getattr(value,'_key_mapping',{}) # Safer access

                        if not isinstance(inner_value, dict):
                             raise CtyMapValidationError(f"Internal value of CtyValue map is not a dict: {type(inner_value).__name__}")

                        input_dict_with_cty_keys = {}
                        for str_key, inner_val in inner_value.items():
                            original_key = inner_key_mapping.get(str_key)
                            if original_key:
                                input_dict_with_cty_keys[original_key] = inner_val
                            else:
                                fallback_key = CtyValue(vtype=CtyString(), value=str_key)
                                input_dict_with_cty_keys[fallback_key] = inner_val
                        input_dict = input_dict_with_cty_keys
                    except Exception as e:
                        error_msg = f"Error processing CtyValue input map: {e}"
                        logger.error(f"🔌❌🔄 {error_msg}")
                        raise CtyMapValidationError(error_msg) from e
                else:
                    error_msg = f"Input CtyValue map type {value.type} is not compatible with target type {self}"
                    logger.error(f"🔌❌🔄 {error_msg}")
                    raise CtyMapValidationError(error_msg)
            else:
                error_msg = f"Input CtyValue has type {value.type}, expected compatible map type"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise CtyMapValidationError(error_msg)
        else:
            error_msg = f"Expected dict or CtyValue map, got {type(value).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)

        if not input_dict: # Handles empty dict case here now
             logger.debug("🔌🔍✅ Empty dictionary is valid")
             return CtyValue(vtype=self, value={}, key_mapping={})

        # --- Validate Dictionary Items ---
        validated_map: dict[str, CtyValue] = {}
        key_mapping: dict[str, CtyValue] = {}
        validation_errors = []

        for k, v in input_dict.items():
            map_key_str: Optional[str] = None
            validated_key_cty: Optional[CtyValue] = None
            validated_value_cty: Optional[CtyValue] = None
            item_errors = []

            # --- Validate Key ---
            try:
                if isinstance(k, CtyValue):
                    logger.debug(f"🔌🔍🔄 Processing pre-validated key: {k!r}")
                    if not isinstance(k.type, CtyString):
                        # Key is CtyValue but not CtyString
                        raise CtyMapValidationError(f"Key type mismatch: expected CtyString, got {k.type.__class__.__name__}")
                    if k.is_null or k.is_unknown:
                        # Key is null or unknown
                        raise CtyMapValidationError("Map keys cannot be null or unknown")
                    # Key is a valid, known, non-null CtyString CtyValue - USE IT DIRECTLY
                    validated_key_cty = k
                    map_key_str = str(k.value) # Extract string value
                    logger.debug(f"🔌🔍✅ Using valid pre-validated CtyString key, str value: '{map_key_str}'")
                else:
                    # Input key k is NOT a CtyValue, validate it as a string
                    logger.debug(f"🔌🔍🔄 Validating raw key: {k!r}")
                    # Use CtyString() validator instance
                    string_validator = CtyString()
                    validated_key_cty = string_validator.validate(k) # Returns a CtyValue
                    if validated_key_cty.is_null or validated_key_cty.is_unknown:
                        raise CtyMapValidationError("Map keys cannot be null or unknown after validation")
                    map_key_str = str(validated_key_cty.value)
                    logger.debug(f"🔌🔍✅ Validated raw key to string: '{map_key_str}'")

            except (CtyValidationError, CtyMapValidationError) as key_err:
                item_errors.append(f"Invalid key {k!r}: {key_err}")
            except Exception as key_err:
                item_errors.append(f"Unexpected error validating key {k!r}: {key_err}")

            if item_errors:
                validation_errors.extend(item_errors)
                continue # Skip value validation for this item

            # Ensure map_key_str is set (should be if no key errors)
            if map_key_str is None:
                 validation_errors.append(f"Internal error: map_key_str is None for key {k!r}")
                 continue

            # --- Validate Value ---
            try:
                if isinstance(v, CtyValue):
                    if not v.type.usable_as(self.value_type):
                        raise CtyMapValidationError(f"Value type mismatch for key '{map_key_str}': expected compatible with {self.value_type.__class__.__name__}, got {v.type.__class__.__name__}")
                    validated_value_cty = v
                else:
                    validated_value_cty = self.value_type.validate(v)

            except (CtyValidationError, CtyMapValidationError) as val_err:
                item_errors.append(f"Invalid value for key '{map_key_str}': {val_err}")
            except Exception as val_err:
                item_errors.append(f"Unexpected error validating value for key '{map_key_str}': {val_err}")

            if item_errors:
                validation_errors.extend(item_errors)
                continue # Skip adding this item

            # --- Add Validated Item ---
            if validated_key_cty is not None and validated_value_cty is not None and map_key_str is not None:
                validated_map[map_key_str] = validated_value_cty
                key_mapping[map_key_str] = validated_key_cty
                logger.debug(f"🔌🔍✅ Added key-value pair ('{map_key_str}') to map, size: {len(validated_map)}")
            else:
                validation_errors.append(f"Internal error: validation passed but parts are None for key {k!r}")

            # In the CtyMap.validate method
            # Add explicit validation for boolean values
            from pyvider.cty.types.primitives import CtyBool
            if isinstance(self.value_type, CtyBool):
                try:
                    validated_value_cty = self.value_type.validate(v)
                except Exception as e:
                    error_msg = f"Invalid boolean value for key '{map_key_str}': {e}"
                    logger.error(f"🔌❌🔄 {error_msg}")
                    raise CtyMapValidationError(error_msg) from e

        # Hmm.
        # from pyvider.cty.types.primitives import CtyBool
        # if isinstance(self.value_type, CtyBool):
        #     try:
        #         validated_value_cty = self.value_type.validate(v)
        #     except Exception as e:
        #         error_msg = f"Invalid boolean value for key '{map_key_str}': {e}"
        #         logger.error(f"🔌❌🔄 {error_msg}")
        #         raise CtyMapValidationError(error_msg) from e

        # --- Finalize ---
        if validation_errors:
            combined_error_msg = "Map validation failed:\n - " + "\n - ".join(validation_errors)
            logger.error(f"🔌❌🔄 {combined_error_msg}")
            raise CtyMapValidationError(combined_error_msg)

        logger.debug(f"🔌🔍✅ Map validated successfully with {len(validated_map)} entries")
        # Use keywords matching CtyValue field names
        return CtyValue(vtype=self, value=validated_map, key_mapping=key_mapping)

    def get(self, map_value: CtyValue, key: Any, default: Optional[CtyValue] = None) -> Optional[CtyValue]:
        """
        Get a value from the map by key.
        (Docstring unchanged - see previous context)
        """
        logger.debug(f"🔌🔍🔄 Getting value for key {key!r} from map")

        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise TypeError(f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}")

        if map_value.is_null or map_value.is_unknown:
            logger.debug(f"🔌🔍⚠️ Cannot get from null/unknown map, returning default or special value")
            if default is not None: return default
            return CtyValue.null(self.value_type) if map_value.is_null else CtyValue.unknown(self.value_type)

        # --- Key Validation and String Conversion ---
        str_key: Optional[str] = None
        try:
            if isinstance(key, CtyValue):
                if isinstance(key.type, CtyString) and not key.is_null and not key.is_unknown:
                    str_key = str(key.value)
                # else: Invalid CtyValue key, str_key remains None
            else:
                # Validate raw key
                validated_key = CtyString().validate(key)
                if not validated_key.is_null and not validated_key.is_unknown:
                    str_key = str(validated_key.value)
            logger.debug(f"🔌🔍🔄 Lookup key string: {str_key}")
        except (CtyValidationError, CtyMapValidationError) as e:
            logger.debug(f"🔌🔍⚠️ Key validation failed for get: {e}")
        except Exception as e:
             logger.warning(f"🔌🔍⚠️ Unexpected error during key validation for get: {e}")

        # If key is invalid or couldn't be converted, return default
        if str_key is None:
            logger.debug(f"🔌🔍⚠️ Invalid key {key!r} for map lookup, returning default")
            return default

        # --- Access Map Data ---
        # Use public property .value if direct _value access is problematic
        internal_map = map_value.value
        if not isinstance(internal_map, dict):
             logger.error(f"🔌❌🔄 Internal map value is not a dict: {type(internal_map).__name__}")
             return default # Or raise error? Default seems safer

        result = internal_map.get(str_key)
        if result is not None:
             logger.debug(f"🔌🔍✅ Found value for key: {str_key}")
             return result # Should already be a CtyValue from validation

        logger.debug(f"🔌🔍⚠️ Key {str_key} not found, returning default")
        return default

    def set(self, map_value: CtyValue, key: Any, value: Any) -> CtyValue:
        """
        Set a value in a map, returning a new map.
        (Docstring unchanged - see previous context)
        """
        logger.debug(f"🔌📝🔄 Setting key {key!r} to value {value!r} in map")

        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise TypeError(f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}")
        if map_value.is_null or map_value.is_unknown:
            raise CtyMapValidationError("Cannot set on null or unknown map")

        # --- Validate Key ---
        validated_key_cty: Optional[CtyValue] = None
        str_key: Optional[str] = None
        try:
            if isinstance(key, CtyValue):
                if not isinstance(key.type, CtyString):
                    raise CtyMapValidationError(f"Key type mismatch: expected CtyString, got {key.type.__class__.__name__}")
                if key.is_null or key.is_unknown:
                    raise CtyMapValidationError("Map keys cannot be null or unknown")
                validated_key_cty = key
                str_key = str(key.value)
            else:
                validated_key_cty = CtyString().validate(key)
                if validated_key_cty.is_null or validated_key_cty.is_unknown:
                    raise CtyMapValidationError("Map keys cannot be null or unknown")
                str_key = str(validated_key_cty.value)
        except (CtyValidationError, CtyMapValidationError) as e:
            raise CtyMapValidationError(f"Invalid key {key!r}: {e}") from e
        except Exception as e:
            raise CtyMapValidationError(f"Unexpected error validating key {key!r}: {e}") from e

        # Should not be None if validation passed
        assert str_key is not None
        assert validated_key_cty is not None

        # --- Validate Value ---
        validated_value_cty: Optional[CtyValue] = None
        try:
            if isinstance(value, CtyValue):
                if not value.type.usable_as(self.value_type):
                    raise CtyMapValidationError(f"Value type mismatch for key '{str_key}': expected compatible with {self.value_type.__class__.__name__}, got {value.type.__class__.__name__}")
                validated_value_cty = value
            else:
                validated_value_cty = self.value_type.validate(value)
        except (CtyValidationError, CtyMapValidationError) as e:
            raise CtyMapValidationError(f"Invalid value for key '{str_key}': {e}") from e
        except Exception as e:
            raise CtyMapValidationError(f"Unexpected error validating value for key '{str_key}': {e}") from e

        # Should not be None if validation passed
        assert validated_value_cty is not None

        # --- Create New State ---
        # Use public properties/methods if direct _ access is problematic
        current_map = map_value.value
        current_key_mapping = getattr(map_value, '_key_mapping', {}) # Safer access

        new_map = dict(current_map) # Copy existing map
        new_key_mapping = dict(current_key_mapping) # Copy existing mapping

        new_map[str_key] = validated_value_cty
        new_key_mapping[str_key] = validated_key_cty
        logger.debug(f"🔌📝✅ Set key {str_key} to value")

        # Use evolve with public field names as keywords
        return evolve(
            map_value,
            value=new_map, # Pass the new dictionary
            key_mapping=new_key_mapping # Pass the new key mapping
        )

    def delete(self, map_value: CtyValue, key: Any) -> CtyValue:
        """
        Delete a key from a map, returning a new map.
        (Docstring unchanged - see previous context)
        """
        logger.debug(f"🔌📝🔄 Deleting key {key!r} from map")

        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise TypeError(f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}")
        if map_value.is_null or map_value.is_unknown:
            raise CtyMapValidationError("Cannot delete from null or unknown map")

        # --- Key Validation and String Conversion ---
        str_key: Optional[str] = None
        try:
            if isinstance(key, CtyValue):
                if isinstance(key.type, CtyString) and not key.is_null and not key.is_unknown:
                    str_key = str(key.value)
            else:
                validated_key = CtyString().validate(key)
                if not validated_key.is_null and not validated_key.is_unknown:
                    str_key = str(validated_key.value)
        except Exception as e:
            logger.debug(f"🔌📝⚠️ Key validation failed for delete, map unchanged: {e}")
            return map_value # Key is invalid, cannot exist, return original map

        # If key is invalid or couldn't be converted, return original map
        if str_key is None:
            logger.debug(f"🔌📝⚠️ Invalid key {key!r} for delete, map unchanged")
            return map_value

        # --- Create New State ---
        # Use public properties/methods if direct _ access is problematic
        current_map = map_value.value
        current_key_mapping = getattr(map_value, '_key_mapping', {}) # Safer access

        if str_key not in current_map:
            logger.debug(f"🔌📝⚠️ Key {str_key} not found, map unchanged")
            return map_value # Key not present, return original map

        new_map = dict(current_map)
        new_key_mapping = dict(current_key_mapping)

        del new_map[str_key]
        if str_key in new_key_mapping:
            del new_key_mapping[str_key]
        logger.debug(f"🔌📝✅ Deleted key {str_key}")

        # Use evolve with public field names as keywords
        return evolve(
            map_value,
            value=new_map,
            key_mapping=new_key_mapping
        )

    def element_iterator(self, map_value: CtyValue) -> "ElementIterator":
        """
        Get an iterator for the elements in a map.
        (Docstring unchanged - see previous context)
        """
        logger.debug(f"🔌🔍🔄 Creating element iterator for map")

        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise TypeError(f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}")
        if map_value.is_null or map_value.is_unknown:
            raise CtyMapValidationError("Cannot iterate null or unknown map")

        # Use public properties/methods if direct _ access is problematic
        internal_map = map_value.value
        key_mapping = getattr(map_value, '_key_mapping', {}) # Safer access

        if not isinstance(internal_map, dict):
             raise TypeError(f"Internal map value is not a dict: {type(internal_map).__name__}")

        # Pass the internal dict and key mapping to the iterator
        return ElementIterator(self.key_type, internal_map, key_mapping)

    def equal(self, other: CtyType) -> bool:
        """
        Check if this type equals another type.
        (Implementation unchanged)
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
        (Implementation unchanged)
        """
        logger.debug(f"🔌🔍🔄 Checking usability as {type(other).__name__}")
        if not isinstance(other, CtyMap):
            logger.debug(f"🔌🔍❌ Not usable as: {type(other).__name__} is not CtyMap")
            return False

        keys_ok = self.key_type.usable_as(other.key_type)
        vals_ok = self.value_type.usable_as(other.value_type)

        logger.debug(
            f"🗺️🔍🔄 key_type.usable_as → {keys_ok}   ",
            f"value_type.usable_as → {vals_ok}",
        )
        return keys_ok and vals_ok

    def __str__(self) -> str:
        """
        Human-readable string representation.
        (Implementation unchanged)
        """
        key_type_name = self.key_type.__class__.__name__
        value_type_name = self.value_type.__class__.__name__
        return f"map({key_type_name}, {value_type_name})"

    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.
        (Implementation unchanged)
        """
        return f"CtyMap(key_type={self.key_type!r}, value_type={self.value_type!r})"


class ElementIterator:
    """
    Iterator for map elements with consistent ordering.
    (Docstring unchanged - see previous context)
    """
    def __init__(self,
                 key_type: "CtyType",
                 map_data: dict[str, CtyValue],
                 key_mapping: dict[str, CtyValue]):
        """
        Initialize the iterator with map data and key mapping.
        (Implementation unchanged - see previous context)
        """
        self.key_type = key_type
        self.items = []
        for string_key, value in map_data.items():
            key_value = key_mapping.get(string_key)
            if key_value is None:
                try:
                    key_value = key_type.validate(string_key)
                except Exception:
                    key_value = CtyValue(vtype=key_type, value=string_key) # Fallback
            self.items.append((key_value, value))
        try:
            self.items.sort(key=lambda item: str(item[0].value))
        except ValueError:
            logger.warning("Could not sort map iterator items by key value, using repr fallback")
            self.items.sort(key=lambda item: repr(item[0]))
        self.index = -1

    def next(self) -> bool:
        """
        Advance to the next element in the iteration.
        (Implementation unchanged)
        """
        if self.index < len(self.items) - 1:
            self.index += 1
            return True
        return False

    def key(self) -> CtyValue:
        """
        Get the current key as a CtyValue.
        (Implementation unchanged)
        """
        if self.index < 0 or self.index >= len(self.items):
            raise IndexError("ElementIterator: no current element")
        return self.items[self.index][0]

    def value(self) -> CtyValue:
        """
        Get the current value.
        (Implementation unchanged)
        """
        if self.index < 0 or self.index >= len(self.items):
            raise IndexError("ElementIterator: no current element")
        return self.items[self.index][1]

# 🐍🏗️🐣
