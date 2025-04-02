#
# pyvider/cty/types/collections/map.py
#

"""
Map type implementation for the Cty type system.
(Rest of docstring remains the same)
"""

from typing import Any, ClassVar, Generic, Optional, TypeVar, cast, TypeGuard

from attrs import define, field, evolve

from pyvider.cty.exceptions import CtyMapValidationError, CtyValidationError
from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType

V = TypeVar('V')  # Value type is variable

@define(frozen=True, slots=True)
class CtyMap(CtyType[dict[str, V]], Generic[V]):
    """
    String-keyed map type in the Cty type system.
    (Rest of docstring remains the same)
    """
    ctype: ClassVar[str] = "map"
    key_type: CtyType[str] = field(kw_only=True)
    value_type: CtyType[V] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        """Validate CtyMap configuration after initialization."""
        # (Implementation remains the same)
        logger.debug("🔌🔍🔄 Validating CtyMap configuration")
        from pyvider.cty.types.primitives import CtyString
        if not isinstance(self.key_type, CtyString):
            error_msg = f"Map key type must be CtyString, got {type(self.key_type).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)
        if not isinstance(self.value_type, CtyType):
            error_msg = f"Expected CtyType for value_type, got {type(self.value_type).__name__}"
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)
        logger.debug("🔌✅🔄 CtyMap configuration validated successfully")


    def validate(self, value: Any) -> "CtyValue":
        """Validate a value against this map type."""
        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        logger.debug(f"🔌🔍🔄 Validating value as CtyMap: {type(value).__name__}")

        # Handle None or empty values
        match value:
            case None:
                logger.debug("🔌🔍✅ None value converted to empty map")
                # <<<< CORRECTED: Use public alias 'type_' for direct call >>>>
                return CtyValue(type_=self, value={}, key_mapping={})
            case {}:
                logger.debug("🔌🔍✅ Empty dict is valid")
                # <<<< CORRECTED: Use public alias 'type_' for direct call >>>>
                return CtyValue(type_=self, value={}, key_mapping={})
            case dict():
                # Continue with validation below
                pass
            case _:
                error_msg = f"Expected dict, got {type(value).__name__}"
                logger.error(f"🔌❌🔄 {error_msg}")
                raise CtyMapValidationError(error_msg)

        # --- Rest of the validation logic (remains the same as previous correction) ---
        validated_map: dict[str, CtyValue] = {}
        key_mapping: dict[str, CtyValue] = {}
        validation_errors = []

        for k, v in value.items():
            map_key: Optional[str] = None
            validated_key_cty: Optional[CtyValue] = None
            validated_value: Optional[CtyValue] = None
            skip_item = False

            # Validate Key
            try:
                if isinstance(k, CtyValue):
                    if not isinstance(k.type, self.key_type.__class__): raise CtyMapValidationError(f"Key type mismatch")
                    if k.is_null or k.is_unknown: raise CtyMapValidationError("Key null/unknown")
                    validated_key_cty = k
                    map_key = str(k.value)
                else:
                    validated_key_cty = self.key_type.validate(k)
                    if validated_key_cty.is_null or validated_key_cty.is_unknown: raise CtyMapValidationError("Key null/unknown")
                    map_key = str(validated_key_cty.value)
                key_mapping[map_key] = validated_key_cty
            except (CtyValidationError, CtyMapValidationError) as e:
                 validation_errors.append(f"Invalid key {k!r}: {e}")
                 skip_item = True
            except Exception as e:
                validation_errors.append(f"Unexpected error validating key {k!r}: {e}")
                skip_item = True
            if skip_item: continue

            # Validate Value
            try:
                if isinstance(v, CtyValue):
                    if not v.type.usable_as(self.value_type): raise CtyMapValidationError(f"Value type mismatch")
                    validated_value = v
                else:
                    validated_value = self.value_type.validate(v)
            except (CtyValidationError, CtyMapValidationError) as e:
                validation_errors.append(f"Invalid value for key '{map_key}': {e}")
                skip_item = True
            except Exception as e:
                validation_errors.append(f"Unexpected error validating value for key '{map_key}': {e}")
                skip_item = True
            if skip_item: continue

            # Add item if both key and value are valid
            if map_key is not None and validated_value is not None:
                validated_map[map_key] = validated_value

        if validation_errors:
             raise CtyMapValidationError("Map validation failed:\n - " + "\n - ".join(validation_errors))

        logger.debug(f"🔌🔍✅ Map validated successfully with {len(validated_map)} entries")
        # <<<< CORRECTED: Use public alias 'type_' for direct call >>>>
        return CtyValue(type_=self, value=validated_map, key_mapping=key_mapping)


    def get(self, map_value: "CtyValue", key: Any, default: Optional["CtyValue"] = None) -> Optional["CtyValue"]:
        """Get a value from the map by key."""
        # (Implementation remains the same as previous correction)
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔌🔍🔄 Getting value for key {key!r} from map")
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise TypeError(f"Expected CtyValue with CtyMap type")
        if map_value.is_null or map_value.is_unknown:
            if default is not None: return default
            return CtyValue.null(self.value_type) if map_value.is_null else CtyValue.unknown(self.value_type)
        str_key = None
        try:
            if isinstance(key, CtyValue):
                if isinstance(key.type, self.key_type.__class__) and not key.is_null and not key.is_unknown: str_key = str(key.value)
            else:
                validated_key = self.key_type.validate(key)
                if not (validated_key.is_null or validated_key.is_unknown): str_key = str(validated_key.value)
        except Exception: pass # Ignore validation errors, key won't be found
        if str_key is None: return default
        map_data = map_value._value
        return map_data.get(str_key, default)


    def set(self, map_value: "CtyValue", key: Any, value: Any) -> "CtyValue":
        """Set a value in a map, returning a new map (immutable)."""
        # (Implementation remains the same - uses evolve correctly)
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔌📝🔄 Setting key {key!r} to value {value!r} in map")
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap): raise TypeError("Expected CtyValue map")
        if map_value.is_null or map_value.is_unknown: raise CtyMapValidationError("Cannot set on null/unknown map")
        new_map = dict(map_value._value)
        key_mapping = dict(map_value._key_mapping)
        validated_key_cty: CtyValue; str_key: str
        try:
            if isinstance(key, CtyValue):
                if not isinstance(key.type, self.key_type.__class__): raise CtyMapValidationError("Key type mismatch")
                if key.is_null or key.is_unknown: raise CtyMapValidationError("Key null/unknown")
                validated_key_cty = key; str_key = str(key.value)
            else:
                validated_key_cty = self.key_type.validate(key)
                if validated_key_cty.is_null or validated_key_cty.is_unknown: raise CtyMapValidationError("Key null/unknown")
                str_key = str(validated_key_cty.value)
        except Exception as e: raise CtyMapValidationError(f"Invalid key {key!r}: {e}") from e
        key_mapping[str_key] = validated_key_cty
        validated_value: CtyValue
        try:
            if isinstance(value, CtyValue):
                if not value.type.usable_as(self.value_type): raise CtyMapValidationError("Value type mismatch")
                validated_value = value
            else: validated_value = self.value_type.validate(value)
        except Exception as e: raise CtyMapValidationError(f"Invalid value for key '{str_key}': {e}") from e
        new_map[str_key] = validated_value
        logger.debug(f"🔌📝✅ Set key {str_key} to value")
        return evolve(map_value, value=new_map, key_mapping=key_mapping)


    def delete(self, map_value: "CtyValue", key: Any) -> "CtyValue":
        """Delete a key from a map, returning a new map (immutable)."""
        # (Implementation remains the same - uses evolve correctly)
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔌📝🔄 Deleting key {key!r} from map")
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap): raise TypeError("Expected CtyValue map")
        if map_value.is_null or map_value.is_unknown: raise CtyMapValidationError("Cannot delete from null/unknown map")
        new_map = dict(map_value._value)
        key_mapping = dict(map_value._key_mapping)
        str_key: Optional[str] = None
        try:
            if isinstance(key, CtyValue):
                if isinstance(key.type, self.key_type.__class__) and not key.is_null and not key.is_unknown: str_key = str(key.value)
            else:
                validated_key = self.key_type.validate(key)
                if not (validated_key.is_null or validated_key.is_unknown): str_key = str(validated_key.value)
        except Exception: pass # If key invalid, it can't be in map
        if str_key is None: return map_value
        if str_key in new_map:
            del new_map[str_key]
            if str_key in key_mapping: del key_mapping[str_key]
            logger.debug(f"🔌📝✅ Deleted key {str_key}")
            return evolve(map_value, value=new_map, key_mapping=key_mapping)
        else: return map_value


    def element_iterator(self, map_value: "CtyValue") -> "ElementIterator":
        """Get an iterator for the elements in a map."""
        # (Implementation remains the same)
        from pyvider.cty.values import CtyValue
        logger.debug(f"🔌🔍🔄 Creating element iterator for map")
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap): raise TypeError("Expected CtyValue map")
        if map_value.is_null or map_value.is_unknown: raise CtyMapValidationError("Cannot iterate null/unknown map")
        return ElementIterator(self.key_type, map_value._value, map_value._key_mapping)

    def equal(self, other: CtyType) -> bool:
        """Check if this type equals another type."""
        # (Implementation remains the same)
        if not isinstance(other, CtyMap): return False
        return self.key_type.equal(other.key_type) and self.value_type.equal(other.value_type)

    def usable_as(self, other: CtyType) -> bool:
        """Check if this type can be used as another type."""
        # (Implementation remains the same)
        if not isinstance(other, CtyMap): return False
        return self.key_type.usable_as(other.key_type) and self.value_type.usable_as(other.value_type)

    def __eq__(self, other: object) -> bool:
        """Equality operator implementation."""
        # (Implementation remains the same)
        if not isinstance(other, CtyMap): return False
        return self.equal(other)

    def __hash__(self) -> int:
        """Hash implementation."""
        # (Implementation remains the same)
        return hash((self.__class__, hash(self.key_type), hash(self.value_type)))

    def __str__(self) -> str:
        """Human-readable string representation."""
        # (Implementation remains the same)
        key_type_name = self.key_type.__class__.__name__
        value_type_name = self.value_type.__class__.__name__
        return f"map({key_type_name}, {value_type_name})"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        # (Implementation remains the same)
        return f"CtyMap(key_type={self.key_type!r}, value_type={self.value_type!r})"


class ElementIterator:
    """Iterator for map elements with consistent ordering."""
    # (Implementation remains the same)
    def __init__(self, key_type: "CtyType", map_data: dict[str, "CtyValue"], key_mapping: dict[str, "CtyValue"]):
        from pyvider.cty.values import CtyValue
        self.key_type = key_type; self.items = []
        for sk, v in map_data.items():
            kv = key_mapping.get(sk)
            if kv is None:
                try: kv = key_type.validate(sk)
                except Exception: kv = CtyValue(type_=key_type, value=sk) # Use type_
            self.items.append((kv, v))
        try: self.items.sort(key=lambda i: str(i[0].value))
        except ValueError: self.items.sort(key=repr)
        self.index = -1
    def next(self) -> bool:
        if self.index < len(self.items) - 1: self.index += 1; return True
        return False
    def key(self) -> "CtyValue":
        if not 0 <= self.index < len(self.items): raise IndexError("No current element")
        return self.items[self.index][0]
    def value(self) -> "CtyValue":
        if not 0 <= self.index < len(self.items): raise IndexError("No current element")
        return self.items[self.index][1]

# 🐍🏗️🐣