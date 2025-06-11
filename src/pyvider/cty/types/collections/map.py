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

from typing import Any, ClassVar, Generic, TypeVar

from attrs import define, evolve, field

from pyvider.cty.exceptions import CtyMapValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyString
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger

V = TypeVar("V")  # Value type is variable


@define(
    frozen=True, slots=True, eq=False
)  # Added eq=False for consistent __eq__ behavior via CtyType
class CtyMap(CtyType[dict[str, V]], Generic[V]):
    """
    String-keyed map type in the Cty type system.
    """

    ctype: ClassVar[str] = "map"
    key_type: CtyType[str] = field(kw_only=True)
    value_type: CtyType[V] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        logger.debug("🔌🔍🔄 Validating CtyMap configuration")
        if not isinstance(self.key_type, CtyString):
            error_msg = (
                f"Map key type must be CtyString, got {type(self.key_type).__name__}"
            )
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)
        if not isinstance(self.value_type, CtyType):  # Check if it's a CtyType instance
            error_msg = (
                f"Expected CtyType for value_type, got {type(self.value_type).__name__}"
            )
            logger.error(f"🔌❌🔄 {error_msg}")
            raise CtyMapValidationError(error_msg)
        logger.debug("🔌✅🔄 CtyMap configuration validated successfully")

    def validate(self, value: Any) -> CtyValue:
        logger.debug(f"🔌🔍🔄 Validating value as CtyMap: {type(value).__name__}")

        input_dict: dict | None = None
        if value is None:
            logger.debug("🔌🔍✅ None value converted to empty map")
            return CtyValue(vtype=self, value={}, key_mapping={})
        elif isinstance(value, dict):
            input_dict = value
        elif isinstance(value, CtyValue):
            logger.debug("🔌🔍🔄 Input is a CtyValue, checking type...")
            if isinstance(value.type, CtyMap):
                # If types are equal or usable, we need to process its internal value.
                # The primary difference for `equal` vs `usable_as` might be optimizations
                # if we could trust an equal-typed CtyValue to be fully validated already.
                # However, to be robust, especially if internal state could be manipulated,
                # re-processing value.value is safer.
                if self.equal(value.type) or value.type.usable_as(self):
                    logger.debug(
                        f"🔌🔍🔄 Input CtyValue has {'matching' if self.equal(value.type) else 'usable'} map type, processing its internal value."
                    )
                    try:
                        inner_value = value.value
                        if not isinstance(inner_value, dict):
                            # This is the specific error for test_validate_ctyvalue_internal_value_not_dict
                            raise CtyMapValidationError(
                                f"Internal value of CtyValue map is not a dict: {type(inner_value).__name__}"
                            )

                        # If types are exactly equal, we might assume keys/values are already CtyValues,
                        # but to cover conversion from a usable type (e.g. map<string,dynamic> to map<string,string>),
                        # we should treat inner_value elements as potentially needing validation.
                        # The original code path for usable_as already did this by reconstructing input_dict_with_cty_keys.
                        # We'll use that same logic.
                        inner_key_mapping = getattr(value, "_key_mapping", {})
                        input_dict_with_cty_keys = {}
                        for (
                            str_key,
                            val_element,
                        ) in (
                            inner_value.items()
                        ):  # val_element could be raw or CtyValue
                            original_cty_key = inner_key_mapping.get(str_key)

                            # The key for input_dict_with_cty_keys should be the CtyValue version of the key
                            # The value (val_element) will be validated in the main loop later.
                            if original_cty_key:
                                input_dict_with_cty_keys[original_cty_key] = val_element
                            else:
                                # If no original CtyValue key, create one from str_key
                                input_dict_with_cty_keys[
                                    CtyString().validate(str_key)
                                ] = val_element
                        input_dict = input_dict_with_cty_keys
                    except Exception as e:
                        # Catch if getattr or inner_value access fails, or other unexpected issues.
                        # This also catches the CtyMapValidationError from the isinstance check.
                        logger.error(f"🔌❌🔄 Error processing CtyValue input map: {e}")
                        # Re-raise specific errors if they are already CtyMapValidationError, otherwise wrap
                        if isinstance(e, CtyMapValidationError):
                            raise
                        raise CtyMapValidationError(
                            f"Error processing CtyValue input map: {e}"
                        ) from e
                else:  # Not equal and not usable_as
                    raise CtyMapValidationError(
                        f"Input CtyValue map type {value.type} is not compatible with target type {self}"
                    )
            else:  # Not a CtyMap CtyValue
                raise CtyMapValidationError(
                    f"Input CtyValue has type {value.type}, expected compatible map type"
                )
        else:  # Not a dict and not a CtyValue
            raise CtyMapValidationError(
                f"Expected dict or CtyValue map, got {type(value).__name__}"
            )

        if not input_dict:  # This can happen if input was CtyValue but its .value was empty or became empty.
            logger.debug("🔌🔍✅ Empty dictionary (possibly from CtyValue) is valid")
            return CtyValue(vtype=self, value={}, key_mapping={})

        validated_map: dict[str, CtyValue] = {}
        key_mapping: dict[str, CtyValue] = {}
        validation_errors = []

        for k, v in input_dict.items():
            map_key_str: str | None = None
            validated_key_cty: CtyValue | None = None
            item_errors = []

            try:
                if isinstance(k, CtyValue):
                    if not isinstance(k.type, CtyString):
                        raise CtyMapValidationError(
                            f"Key type mismatch: expected CtyString, got {k.type.__class__.__name__}"
                        )
                    if k.is_null or k.is_unknown:
                        raise CtyMapValidationError(
                            "Map keys cannot be null or unknown"
                        )
                    validated_key_cty = k
                    map_key_str = str(k.value)
                else:
                    string_validator = CtyString()
                    validated_key_cty = string_validator.validate(k)
                    if validated_key_cty.is_null or validated_key_cty.is_unknown:
                        raise CtyMapValidationError(
                            "Map keys cannot be null or unknown after validation"
                        )
                    map_key_str = str(validated_key_cty.value)
            except Exception as key_err:
                item_errors.append(f"Invalid key {k!r}: {key_err}")

            if item_errors:
                validation_errors.extend(item_errors)
                continue
            assert map_key_str is not None, (
                f"Internal error: map_key_str is None for key {k!r} after key validation"
            )

            validated_value_cty: CtyValue | None = (
                None  # ensure it's defined before try
            )
            try:
                validated_value_cty = self.value_type.validate(v)
            except Exception as val_err:
                item_errors.append(f"Invalid value for key '{map_key_str}': {val_err}")

            if item_errors:
                validation_errors.extend(item_errors)
                continue

            if validated_key_cty is not None and validated_value_cty is not None:
                validated_map[map_key_str] = validated_value_cty
                key_mapping[map_key_str] = validated_key_cty
            else:
                if not item_errors:
                    validation_errors.append(
                        f"Internal error: validation parts are None for key {k!r}"
                    )

        if validation_errors:
            raise CtyMapValidationError(
                "Map validation failed:\n - " + "\n - ".join(validation_errors)
            )

        logger.debug(
            f"🔌🔍✅ Map validated successfully with {len(validated_map)} entries"
        )
        return CtyValue(vtype=self, value=validated_map, key_mapping=key_mapping)

    def get(
        self, map_value: CtyValue, key: Any, default: CtyValue | None = None
    ) -> CtyValue | None:
        logger.debug(f"🔌🔍🔄 Getting value for key {key!r} from map")
        if not isinstance(map_value, CtyValue) or not isinstance(
            map_value.type, CtyMap
        ):
            raise TypeError(
                f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            )
        if map_value.is_null or map_value.is_unknown:
            logger.debug(
                "🔌🔍⚠️ Cannot get from null/unknown map, returning default or special value"
            )
            if default is not None:
                return default
            return (
                CtyValue.null(self.value_type)
                if map_value.is_null
                else CtyValue.unknown(self.value_type)
            )
        str_key: str | None = None
        try:
            if isinstance(key, CtyValue):
                if (
                    isinstance(key.type, CtyString)
                    and not key.is_null
                    and not key.is_unknown
                ):
                    str_key = str(key.value)
            else:
                validated_key = CtyString().validate(key)
                if not validated_key.is_null and not validated_key.is_unknown:
                    str_key = str(validated_key.value)
        except Exception as e:
            logger.debug(f"🔌🔍⚠️ Key validation failed for get: {e}")
        if str_key is None:
            return default
        internal_map = map_value.value
        if not isinstance(internal_map, dict):
            return default
        result = internal_map.get(str_key)
        if result is not None:
            return result
        return default

    def set(self, map_value: CtyValue, key: Any, value: Any) -> CtyValue:
        logger.debug(f"🔌📝🔄 Setting key {key!r} to value {value!r} in map")
        if not isinstance(map_value, CtyValue) or not isinstance(
            map_value.type, CtyMap
        ):
            raise TypeError(
                f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            )
        if map_value.is_null or map_value.is_unknown:
            raise CtyMapValidationError("Cannot set on null or unknown map")
        validated_key_cty: CtyValue | None = None
        str_key: str | None = None
        try:
            if isinstance(key, CtyValue):
                if not isinstance(key.type, CtyString):
                    raise CtyMapValidationError(
                        f"Key type mismatch: expected CtyString, got {key.type.__class__.__name__}"
                    )
                if key.is_null or key.is_unknown:
                    raise CtyMapValidationError("Map keys cannot be null or unknown")
                validated_key_cty = key
                str_key = str(key.value)
            else:
                validated_key_cty = CtyString().validate(key)
                if validated_key_cty.is_null or validated_key_cty.is_unknown:
                    raise CtyMapValidationError("Map keys cannot be null or unknown")
                str_key = str(validated_key_cty.value)
        except Exception as e:
            raise CtyMapValidationError(f"Invalid key {key!r}: {e}") from e
        assert str_key is not None and validated_key_cty is not None
        validated_value_cty = self.value_type.validate(value)
        assert validated_value_cty is not None
        current_map = map_value.value
        current_key_mapping = getattr(map_value, "_key_mapping", {})
        new_map = dict(current_map)
        new_key_mapping = dict(current_key_mapping)
        new_map[str_key] = validated_value_cty
        new_key_mapping[str_key] = validated_key_cty
        return evolve(map_value, value=new_map, key_mapping=new_key_mapping)

    def delete(self, map_value: CtyValue, key: Any) -> CtyValue:
        logger.debug(f"🔌📝🔄 Deleting key {key!r} from map")
        if not isinstance(map_value, CtyValue) or not isinstance(
            map_value.type, CtyMap
        ):
            raise TypeError(
                f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            )
        if map_value.is_null or map_value.is_unknown:
            raise CtyMapValidationError("Cannot delete from null or unknown map")
        str_key: str | None = None
        try:
            if isinstance(key, CtyValue):
                if (
                    isinstance(key.type, CtyString)
                    and not key.is_null
                    and not key.is_unknown
                ):
                    str_key = str(key.value)
            else:
                validated_key = CtyString().validate(key)
                if not validated_key.is_null and not validated_key.is_unknown:
                    str_key = str(validated_key.value)
        except Exception:
            return map_value
        if str_key is None:
            return map_value
        current_map = map_value.value
        current_key_mapping = getattr(map_value, "_key_mapping", {})
        if str_key not in current_map:
            return map_value
        new_map = dict(current_map)
        new_key_mapping = dict(current_key_mapping)
        del new_map[str_key]
        new_key_mapping.pop(str_key, None)
        return evolve(map_value, value=new_map, key_mapping=new_key_mapping)

    def element_iterator(self, map_value: CtyValue) -> "ElementIterator":
        logger.debug("🔌🔍🔄 Creating element iterator for map")
        if not isinstance(map_value, CtyValue) or not isinstance(
            map_value.type, CtyMap
        ):
            raise TypeError(
                f"Expected CtyValue with CtyMap type, got {type(map_value).__name__}"
            )
        if map_value.is_null or map_value.is_unknown:
            raise CtyMapValidationError("Cannot iterate null or unknown map")
        internal_map = map_value.value
        key_mapping = getattr(map_value, "_key_mapping", {})
        if not isinstance(internal_map, dict):
            raise TypeError(
                f"Internal map value is not a dict: {type(internal_map).__name__}"
            )
        return ElementIterator(self.key_type, internal_map, key_mapping)

    def equal(self, other: CtyType) -> bool:
        logger.debug(f"🔌🔍🔄 Checking equality with {type(other).__name__}")
        if not isinstance(other, CtyMap):
            return False
        return self.key_type.equal(other.key_type) and self.value_type.equal(
            other.value_type
        )

    def usable_as(self, other: CtyType) -> bool:
        logger.debug(f"🔌🔍🔄 Checking usability as {type(other).__name__}")
        if not isinstance(other, CtyMap):
            return False
        return self.key_type.usable_as(other.key_type) and self.value_type.usable_as(
            other.value_type
        )

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
    """Iterator for map elements with consistent ordering."""

    def __init__(
        self,
        key_type: "CtyType",
        map_data: dict[str, CtyValue],
        key_mapping: dict[str, CtyValue],
    ) -> None:
        self.key_type = key_type
        self.items = []
        for string_key, value in map_data.items():
            key_value = key_mapping.get(string_key)
            if key_value is None:
                try:
                    key_value = key_type.validate(string_key)
                except Exception:
                    key_value = CtyValue(vtype=key_type, value=string_key)  # type: ignore
            self.items.append((key_value, value))
        try:
            self.items.sort(key=lambda item: str(item[0].value))
        except ValueError:
            self.items.sort(key=lambda item: repr(item[0]))
        self.index = -1  # Current position is before the first element

    def next(self) -> bool:
        if self.index < len(self.items) - 1:
            self.index += 1
            return True
        else:
            # Mark as exhausted for subsequent key/value calls by moving index out of valid range
            self.index = len(self.items)
            return False

    def key(self) -> CtyValue:
        if self.index < 0 or self.index >= len(self.items):
            raise IndexError("ElementIterator: no current element")
        return self.items[self.index][0]

    def value(self) -> CtyValue:
        if self.index < 0 or self.index >= len(self.items):
            raise IndexError("ElementIterator: no current element")
        return self.items[self.index][1]


# Using slots=False here as a simpler change than refactoring __init__ to full attrs style for now.
# A full attrs style would involve factory or converter for 'items'.
@define(slots=False)
class ElementIterator:
    """Iterator for map elements with consistent ordering."""

    def __init__(
        self,
        key_type: "CtyType",
        map_data: dict[str, CtyValue],
        key_mapping: dict[str, CtyValue],
    ) -> None:
        self.key_type = key_type
        self.items = []
        for string_key, value in map_data.items():
            key_value = key_mapping.get(string_key)
            if key_value is None:
                try:
                    key_value = key_type.validate(string_key)
                except Exception:
                    key_value = CtyValue(vtype=key_type, value=string_key)
            self.items.append((key_value, value))
        try:
            self.items.sort(key=lambda item: str(item[0].value))
        except ValueError:
            self.items.sort(key=lambda item: repr(item[0]))
        self.index = -1

    def next(self) -> bool:
        if self.index < len(self.items) - 1:
            self.index += 1
            return True
        return False

    def key(self) -> CtyValue:
        if self.index < 0 or self.index >= len(self.items):
            raise IndexError("ElementIterator: no current element")
        return self.items[self.index][0]

    def value(self) -> CtyValue:
        if self.index < 0 or self.index >= len(self.items):
            raise IndexError("ElementIterator: no current element")
        return self.items[self.index][1]


# 🐍🏗️🐣
