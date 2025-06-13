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

from pyvider.cty.exceptions import CtyMapValidationError, CtyValidationError, CtyStringValidationError, CtyNumberValidationError
from pyvider.telemetry import logger
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue
from pyvider.cty.types.primitives import CtyString
from pyvider.cty.types.structural.dynamic import CtyDynamic # Reverted to direct import


V = TypeVar('V')  # Value type is variable

@define(frozen=True, slots=True)
class CtyMap(CtyType[dict[str, V]], Generic[V]):
    """
    String-keyed map type in the Cty type system.
    """
    ctype: ClassVar[str] = "map"
    key_type: CtyType[str] = field(kw_only=True)
    value_type: CtyType[V] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        logger.debug("🔌🔍🔄 Validating CtyMap configuration")
        if not isinstance(self.key_type, CtyType):
            error_msg = f"key_type must be a CtyType instance, got {type(self.key_type).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)

        # CtyDynamic is a primitive type and is allowed as a key type.
        # All other key types must also be primitive.
        if not self.key_type.is_primitive_type():
            error_msg = f"Map key_type must be a primitive type, got {self.key_type.__class__.__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)

        if not isinstance(self.value_type, CtyType): # Check if it's a CtyType instance
            error_msg = f"value_type must be a CtyType instance, got {type(self.value_type).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)
        logger.debug("🔌✅🔄 CtyMap configuration validated successfully")

    def validate(self, value: Any) -> CtyValue:
        logger.debug(f"🔌🔍🔄 Validating value as CtyMap: {type(value).__name__}")

        input_dict: Optional[dict] = None
        if value is None:
            # logger.debug("🔌🔍✅ None value converted to empty map") # No longer converting
            # return CtyValue(vtype=self, value={}, key_mapping={})
            raise CtyMapValidationError("Input to CtyMap.validate cannot be None.")
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
                        inner_value = value.value
                        inner_key_mapping = getattr(value,'_key_mapping',{})
                        if not isinstance(inner_value, dict):
                             raise CtyMapValidationError(f"Internal value of CtyValue map is not a dict: {type(inner_value).__name__}")
                        input_dict_with_cty_keys = {}
                        for str_key, inner_val in inner_value.items():
                            original_key = inner_key_mapping.get(str_key)
                            if original_key: input_dict_with_cty_keys[original_key] = inner_val
                            else: input_dict_with_cty_keys[CtyValue(vtype=CtyString(), value=str_key)] = inner_val
                        input_dict = input_dict_with_cty_keys
                    except Exception as e:
                        raise CtyMapValidationError(f"Error processing CtyValue input map: {e}") from e
                else:
                    raise CtyMapValidationError(f"Input CtyValue map type {value.type} is not compatible with target type {self}")
            else:
                raise CtyMapValidationError(f"Input CtyValue has type {value.type}, expected compatible map type")
        else:
            raise CtyMapValidationError(f"Expected dict or CtyValue map, got {type(value).__name__}")

        if not input_dict:
             logger.debug("🔌🔍✅ Empty dictionary is valid")
             return CtyValue(vtype=self, value={}, key_mapping={})

        validated_map: dict[str, CtyValue] = {}
        key_mapping: dict[str, CtyValue] = {}
        validation_errors = []

        for k, v in input_dict.items():
            map_key_str: Optional[str] = None
            validated_key_cty: Optional[CtyValue] = None
            item_errors = []

            try:
                # Regardless of whether k is a CtyValue or a raw Python value,
                # it must be validated against self.key_type.
                # self.key_type is guaranteed to be a primitive type by __attrs_post_init__.
                # If self.key_type is CtyDynamic, it will accept any primitive CtyValue or raw value.
                # If self.key_type is, e.g., CtyString, it will ensure the key is a valid string.
                validated_key_cty = self.key_type.validate(k)

                if validated_key_cty.is_null or validated_key_cty.is_unknown:
                    # This check might be redundant if self.key_type.validate(k) already disallows null/unknown
                    # for non-CtyDynamic types, but it's a good safeguard.
                    # CtyDynamic itself doesn't produce null/unknown unless k is already null/unknown CtyValue.
                    raise CtyMapValidationError("Map keys cannot be null or unknown after validation against map's key_type.")

                map_key_str = str(validated_key_cty.value)

                # If the original key 'k' was already a CtyValue and compatible (after validation),
                # we prefer to use it in the key_mapping for type fidelity.
                # However, validated_key_cty is the one that has passed self.key_type validation.
                # For simplicity and correctness against self.key_type, we use validated_key_cty.
                # This means if k was CtyNumber(1) and self.key_type was CtyDynamic(),
                # validated_key_cty would be CtyNumber(1).
                # If k was CtyNumber(1) and self.key_type was CtyString(), validate() would raise an error.

            except Exception as key_err:
                # Preserve the original key k in the error message for clarity
                error_prefix = ""
                if isinstance(key_err, CtyStringValidationError): error_prefix = "String validation error: "
                elif isinstance(key_err, CtyNumberValidationError): error_prefix = "Number validation error: "
                elif isinstance(key_err, CtyValidationError): error_prefix = f"{key_err.__class__.__name__}: "
                item_errors.append(f"Invalid key {k!r}: {error_prefix}{key_err}")

            if item_errors:
                validation_errors.extend(item_errors)
                continue

            # map_key_str should be non-None if no exception occurred and key is not null/unknown
            assert map_key_str is not None, f"Internal error: map_key_str is None for key {k!r} after key validation, without errors."

            validated_value_cty: Optional[CtyValue] = None
            try:
                validated_value_cty = self.value_type.validate(v)
            except Exception as val_err:
                item_errors.append(f"Invalid value for key '{map_key_str}': {val_err}")

            if item_errors: # Check again if value validation added errors
                validation_errors.extend(item_errors)
                continue

            # Both key and value have been validated successfully and are not None CtyValues themselves
            if validated_key_cty is not None and validated_value_cty is not None:
                validated_map[map_key_str] = validated_value_cty
                # Store the key that was successfully validated against self.key_type
                key_mapping[map_key_str] = validated_key_cty
            else:
                 # This case should ideally not be reached if assertions and checks above are correct
                if not item_errors: # Avoid adding redundant generic error if specific one exists
                    validation_errors.append(f"Internal error: validated key or value is None for original key {k!r}")

        if validation_errors:
            raise CtyMapValidationError("Map validation failed:\n - " + "\n - ".join(validation_errors))

        logger.debug(f"🔌🔍✅ Map validated successfully with {len(validated_map)} entries")
        return CtyValue(vtype=self, value=validated_map, key_mapping=key_mapping)

    def get(self, map_value: CtyValue, key: Any, default: Optional[CtyValue] = None) -> Optional[CtyValue]:
        logger.debug(f"🔌🔍🔄 Getting value for key {key!r} from map")
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise TypeError(f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}")
        if map_value.is_null or map_value.is_unknown:
            logger.debug(f"🔌🔍⚠️ Cannot get from null/unknown map, returning default or special value")
            if default is not None: return default
            return CtyValue.null(self.value_type) if map_value.is_null else CtyValue.unknown(self.value_type)
        str_key: Optional[str] = None
        try:
            if isinstance(key, CtyValue):
                if isinstance(key.type, CtyString) and not key.is_null and not key.is_unknown: str_key = str(key.value)
            else:
                validated_key = CtyString().validate(key)
                if not validated_key.is_null and not validated_key.is_unknown: str_key = str(validated_key.value)
        except Exception as e: logger.debug(f"🔌🔍⚠️ Key validation failed for get: {e}")
        if str_key is None: return default
        internal_map = map_value.value
        if not isinstance(internal_map, dict): return default
        result = internal_map.get(str_key)
        if result is not None: return result
        return default

    def set(self, map_value: CtyValue, key: Any, value: Any) -> CtyValue:
        logger.debug(f"🔌📝🔄 Setting key {key!r} to value {value!r} in map")
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise TypeError(f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}")
        if map_value.is_null or map_value.is_unknown:
            raise CtyMapValidationError("Cannot set on null or unknown map")
        validated_key_cty: Optional[CtyValue] = None
        str_key: Optional[str] = None
        try:
            if isinstance(key, CtyValue):
                if not isinstance(key.type, CtyString): raise CtyMapValidationError(f"Key type mismatch: expected CtyString, got {key.type.__class__.__name__}")
                if key.is_null or key.is_unknown: raise CtyMapValidationError("Map keys cannot be null or unknown")
                validated_key_cty = key; str_key = str(key.value)
            else:
                validated_key_cty = CtyString().validate(key)
                if validated_key_cty.is_null or validated_key_cty.is_unknown: raise CtyMapValidationError("Map keys cannot be null or unknown")
                str_key = str(validated_key_cty.value)
        except Exception as e: raise CtyMapValidationError(f"Invalid key {key!r}: {e}") from e
        assert str_key is not None and validated_key_cty is not None
        validated_value_cty = self.value_type.validate(value)
        assert validated_value_cty is not None
        current_map = map_value.value; current_key_mapping = getattr(map_value, '_key_mapping', {})
        new_map = dict(current_map); new_key_mapping = dict(current_key_mapping)
        new_map[str_key] = validated_value_cty; new_key_mapping[str_key] = validated_key_cty
        return evolve(map_value, value=new_map, key_mapping=new_key_mapping)

    def delete(self, map_value: CtyValue, key: Any) -> CtyValue:
        logger.debug(f"🔌📝🔄 Deleting key {key!r} from map")
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise TypeError(f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}")
        if map_value.is_null or map_value.is_unknown: raise CtyMapValidationError("Cannot delete from null or unknown map")
        str_key: Optional[str] = None
        try:
            if isinstance(key, CtyValue):
                if isinstance(key.type, CtyString) and not key.is_null and not key.is_unknown: str_key = str(key.value)
            else:
                validated_key = CtyString().validate(key)
                if not validated_key.is_null and not validated_key.is_unknown: str_key = str(validated_key.value)
        except Exception: return map_value
        if str_key is None: return map_value
        current_map = map_value.value; current_key_mapping = getattr(map_value, '_key_mapping', {})
        if str_key not in current_map: return map_value
        new_map = dict(current_map); new_key_mapping = dict(current_key_mapping)
        del new_map[str_key]
        if str_key in new_key_mapping: del new_key_mapping[str_key]
        return evolve(map_value, value=new_map, key_mapping=new_key_mapping)

    def element_iterator(self, map_value: CtyValue) -> "ElementIterator":
        logger.debug(f"🔌🔍🔄 Creating element iterator for map")
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise TypeError(f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}")
        if map_value.is_null or map_value.is_unknown:
            raise CtyMapValidationError("Cannot iterate null or unknown map")
        internal_map = map_value.value; key_mapping = getattr(map_value, '_key_mapping', {})
        if not isinstance(internal_map, dict):
             raise TypeError(f"Internal map value is not a dict: {type(internal_map).__name__}")
        return ElementIterator(self.key_type, internal_map, key_mapping)

    def equal(self, other: CtyType) -> bool:
        logger.debug(f"🔌🔍🔄 Checking equality with {type(other).__name__}")
        if not isinstance(other, CtyMap): return False
        return self.key_type.equal(other.key_type) and self.value_type.equal(other.value_type)

    def usable_as(self, other: CtyType) -> bool:
        logger.debug(f"🔌🔍🔄 Checking map usability: self({self!s}) as other({other!s})")
        if isinstance(other, CtyDynamic):
            logger.debug(f"🔌🔍✅ Map type is usable as CtyDynamic")
            return True
        if not isinstance(other, CtyMap):
            logger.debug(f"🔌🔍❌ Target type is not CtyMap or CtyDynamic, got {other.__class__.__name__}")
            return False

        # Both self and other are CtyMap instances at this point.
        self_key_is_dyn = isinstance(self.key_type, CtyDynamic)
        other_key_is_dyn = isinstance(other.key_type, CtyDynamic)
        self_val_is_dyn = isinstance(self.value_type, CtyDynamic)
        other_val_is_dyn = isinstance(other.value_type, CtyDynamic)

        # Key compatibility:
        # 1. If this map's key type is Dynamic, the other's key type must be primitive (or also Dynamic).
        # 2. If the other map's key type is Dynamic, any key from this map is fine.
        # 3. Otherwise, key types must be directly usable.
        key_ok = False
        if self_key_is_dyn: # map(dynamic, V1) usable as map(K2, V2)
            key_ok = other.key_type.is_primitive_type() # K2 must be primitive
        elif other_key_is_dyn: # map(K1, V1) usable as map(dynamic, V2)
            key_ok = self.key_type.is_primitive_type() # K1 must be primitive (already enforced by __init__)
        else: # map(K1, V1) usable as map(K2, V2)
            key_ok = self.key_type.usable_as(other.key_type)

        logger.debug(f"🔌🔍🔄 Key usability detail: self.key({self.key_type!s}), other.key({other.key_type!s}) -> {key_ok}")

        # Value compatibility:
        # 1. If this map's value type is Dynamic, any value type in the other map is fine (dynamic can hold anything).
        # 2. If the other map's value type is Dynamic, any value from this map is fine.
        # 3. Otherwise, value types must be directly usable.
        val_ok = False
        if self_val_is_dyn: # map(K1, dynamic) usable as map(K2, V2)
            val_ok = True # Dynamic can provide for any V2
        elif other_val_is_dyn: # map(K1, V1) usable as map(K2, dynamic)
            val_ok = True # V1 can be placed into a Dynamic value type
        else: # map(K1, V1) usable as map(K2, V2)
            val_ok = self.value_type.usable_as(other.value_type)

        logger.debug(f"🔌🔍🔄 Value usability detail: self.value({self.value_type!s}), other.value({other.value_type!s}) -> {val_ok}")

        final_usability = key_ok and val_ok
        logger.debug(f"🔌🔍✅ Final map usability: {final_usability}")
        return final_usability

    def __str__(self) -> str:
        return f"map({self.key_type.__class__.__name__}, {self.value_type.__class__.__name__})"

    def __repr__(self) -> str:
        return f"CtyMap(key_type={self.key_type!r}, value_type={self.value_type!r})"

    def is_collection_type(self) -> bool:
        """Check if this type is a collection type."""
        return True

    def is_map_type(self) -> bool:
        """Check if this type is a map type."""
        return True

@define
class ElementIterator:
    """ Iterator for map elements with consistent ordering. """
    def __init__(self, key_type: "CtyType", map_data: dict[str, CtyValue], key_mapping: dict[str, CtyValue]):
        self.key_type = key_type
        self.items = []
        for string_key, value in map_data.items():
            key_value = key_mapping.get(string_key)
            if key_value is None:
                try: key_value = key_type.validate(string_key)
                except Exception: key_value = CtyValue(vtype=key_type, value=string_key)
            self.items.append((key_value, value))
        try: self.items.sort(key=lambda item: str(item[0].value))
        except ValueError: self.items.sort(key=lambda item: repr(item[0]))
        self.index = -1

    def next(self) -> bool:
        if self.index < len(self.items) - 1: self.index += 1; return True
        return False

    def key(self) -> CtyValue:
        if self.index < 0 or self.index >= len(self.items): raise IndexError("ElementIterator: no current element")
        return self.items[self.index][0]

    def value(self) -> CtyValue:
        if self.index < 0 or self.index >= len(self.items): raise IndexError("ElementIterator: no current element")
        return self.items[self.index][1]

# 🐍🏗️🐣
