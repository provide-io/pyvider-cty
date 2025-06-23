#
# pyvider/cty/path/path.py
#

"""
Path implementation for navigating Cty values.

This module provides a way to build and follow paths through nested Cty values,
similar to how JavaScript allows property access with dot notation or indexing.

Paths can include:
- Attribute names (for objects)
- Indexes (for lists and tuples)
- Keys (for maps)

This follows go-cty's design for path handling.
"""

from abc import ABC, abstractmethod
from decimal import Decimal  # Added for KeyStep.apply_type
from typing import TypeVar

from attrs import define, field

from pyvider.cty.exceptions import (
    AttributePathError,
    CtyTypeMismatchError,
    CtyValidationError,
)
from pyvider.cty.types import (
    CtyType,
)

# Moved from local import in KeyStep.apply to module level
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger

# Type variables for better type hints
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class PathStep(ABC):
    """
    Base class for path steps.

    A path step represents a single segment in a path, such as an attribute
    name, an index, or a map key.
    """

    @abstractmethod
    def apply(self, value: "CtyValue") -> "CtyValue":
        """
        Apply this step to a value to get a nested value.

        Args:
            value: The value to navigate through

        Returns:
            CtyValue: The nested value

        Raises:
            AttributePathError: If the path step can't be applied
        """
        pass

    @abstractmethod
    def apply_type(self, vtype: "CtyType") -> "CtyType":
        """
        Apply this step to a type to get the nested value's type.

        Args:
            vtype: The type to navigate through

        Returns:
            CtyType: The nested value's type

        Raises:
            AttributePathError: If the path step can't be applied
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """String representation of the path step."""
        pass


@define(frozen=True)
class GetAttrStep(PathStep):
    """
    A path step that gets an attribute from an object.

    This step type is used for objects with named attributes, similar to
    JavaScript's obj.attr notation.
    """

    name: str = field()

    @name.validator
    def _validate_name(self, attribute: str, value: str) -> None:
        """Validate that the attribute name is not empty."""
        logger.debug(f"🧰🔍🔄 Validating attribute name: {value}")
        if not value:
            logger.error("🧰❌🔄 Attribute name cannot be empty")
            raise ValueError("Attribute name cannot be empty")
        logger.debug(f"🧰✅🔄 Attribute name {value} is valid")

    def apply(self, value: "CtyValue") -> "CtyValue":
        """
        Get the attribute with the given name from an object value.

        Args:
            value: The object value

        Returns:
            CtyValue: The attribute value

        Raises:
            AttributePathError: If the value is not an object or has no such attribute
        """
        logger.debug(
            f"🧰🔍🔄 Applying path step {self.name} to value type {value.type.__class__.__name__}"
        )

        # Handle different value types appropriately
        from pyvider.cty.types.collections import CtyMap
        from pyvider.cty.types.structural import CtyObject

        # For object values, use get_attribute
        if isinstance(value.type, CtyObject):
            try:
                return value.type.get_attribute(value, self.name)
            except Exception as e:
                error_msg = f"Cannot get attribute '{self.name}' from object: {e}"
                logger.error(f"🧰❌🔄 {error_msg}")
                raise AttributePathError(error_msg) from e

        # For map values, use get method with string key
        elif isinstance(value.type, CtyMap):
            try:
                # self.name is the attribute name we are looking for, used as a key.
                result = value.type.get(value, self.name)
                # CtyMap.get now returns CtyValue.null if key not found and no default.
                if (
                    result is None
                ):  # Should not happen if .get behaves as specified (returns typed null)
                    logger.error(
                        f"🧰❌🔄 CtyMap.get returned Python None unexpectedly for key '{self.name}'"
                    )
                    raise AttributePathError(
                        f"Key '{self.name}' not found in map (unexpected None from get)"
                    )
                if result.is_null:  # Key not found, and no default given to .get
                    error_msg = f"Key '{self.name}' not found in map"
                    logger.debug(
                        f"🧰🔍 GetAttrStep: {error_msg} (got null value)"
                    )  # Changed to debug
                    raise AttributePathError(error_msg)
                return result
            except (TypeError, CtyTypeMismatchError, CtyValidationError) as e:
                # These errors can be raised by CtyMap.get if the key (self.name) is invalid for the map's key_type
                error_msg = f"Error accessing map with key '{self.name}': {e}"
                logger.error(f"🧰❌🔄 {error_msg}")
                raise AttributePathError(error_msg) from e
            # Any other unexpected error during map.get should also be wrapped.
            except Exception as e:
                error_msg = f"Unexpected error getting key '{self.name}' from map: {e}"
                logger.error(f"🧰❌🔄 {error_msg}")
                raise AttributePathError(error_msg) from e

        # For other values, attribute access is not supported
        else:
            error_msg = f"Cannot get attribute from non-object value of type {value.type.__class__.__name__}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

    def apply_type(self, vtype: "CtyType") -> "CtyType":
        """
        Get the type of the attribute with the given name.

        Args:
            vtype: The object type

        Returns:
            CtyType: The attribute's type

        Raises:
            AttributePathError: If the type is not an object or has no such attribute
        """
        logger.debug(f"🧰🔍🔄 Getting type of attribute {self.name} from object type")

        # Check if the type is an object
        from pyvider.cty.types.structural import CtyObject

        if not isinstance(vtype, CtyObject):
            error_msg = (
                f"Cannot get attribute from non-object type {vtype.__class__.__name__}"
            )
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Get the attribute's type
        if not vtype.has_attribute(self.name):
            error_msg = f"Object type has no attribute {self.name}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        attr_type = vtype.attribute_types[self.name]
        logger.debug(f"🧰✅🔄 Found attribute type: {attr_type.__class__.__name__}")
        return attr_type

    def __str__(self) -> str:
        """Get the string representation of this path step."""
        return f".{self.name}"


@define(frozen=True)
class IndexStep(PathStep):
    """
    A path step that indexes into a list, tuple, or string.

    This step type is used for collections with numeric indexes, similar to
    JavaScript's arr[i] notation.
    """

    index: int = field()

    def apply(self, value: "CtyValue") -> "CtyValue":
        """
        Get the element at the given index from a list or tuple value.

        Args:
            value: The list or tuple value

        Returns:
            CtyValue: The element value

        Raises:
            AttributePathError: If the value is not a list or tuple, or the index is out of bounds
        """
        logger.debug(f"🧰🔍🔄 Getting element at index {self.index} from collection")

        # Check for null values
        if value.is_null:
            logger.error("🧰❌🔄 Cannot index into null value")
            raise AttributePathError("Cannot index into null value")

        # Handle unknown values
        if value.is_unknown:
            logger.debug("🧰🔍🔄 Handling unknown value - creating unknown element")
            # Get the element's type
            elem_type = self.apply_type(value.type)

            # Import here to avoid circular imports
            from pyvider.cty.values import CtyValue

            # Create an unknown value of the element's type
            return CtyValue(vtype=elem_type, is_unknown=True)

        # Check if the type is a list or tuple
        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyTuple

        try:
            collection_value = value.value
            calculated_index = self.index

            # Handle negative indices
            if calculated_index < 0:
                logger.debug(
                    f"🧰🔍🔄 Converting negative index {calculated_index} to positive"
                )
                collection_len = len(collection_value)
                calculated_index = collection_len + calculated_index
                logger.debug(f"🧰🔍🔄 Converted to positive index {calculated_index}")

            # Check bounds (happens in both paths below but we do an explicit check here)
            if calculated_index < 0 or calculated_index >= len(collection_value):
                raise IndexError(
                    f"Index {self.index} out of bounds (0-{len(collection_value) - 1})"
                )

            if isinstance(value.type, CtyList):
                # For lists, use element_at method
                logger.debug("🧰🔍🔄 Using element_at for list type")
                result = value.type.element_at(collection_value, calculated_index)
                logger.debug(f"🧰✅🔄 Retrieved element at index {calculated_index}")
                return result
            elif isinstance(value.type, CtyTuple):
                # For tuples, use element_at method
                logger.debug("🧰🔍🔄 Using element_at for tuple type")
                result = value.type.element_at(collection_value, calculated_index)
                logger.debug(f"🧰✅🔄 Retrieved element at index {calculated_index}")
                return result
            else:
                error_msg = (
                    f"Cannot index into value of type {type(value.type).__name__}"
                )
                logger.error(f"🧰❌🔄 {error_msg}")
                raise AttributePathError(error_msg)

        except IndexError as e:
            error_msg = f"Index out of bounds: {e}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get element at index {self.index}: {e}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg) from e

    def apply_type(self, vtype: "CtyType") -> "CtyType":
        """
        Get the type of the element at the given index.

        Args:
            vtype: The collection type

        Returns:
            CtyType: The element's type

        Raises:
            AttributePathError: If the type is not a collection
        """
        logger.debug(
            f"🧰🔍🔄 Getting type of element at index {self.index} from collection type"
        )

        # Import types to avoid circular imports
        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyTuple

        # Check if the type is a list
        if isinstance(vtype, CtyList):
            logger.debug(
                f"🧰✅🔄 Found list type, element type is {vtype.element_type.__class__.__name__}"
            )
            return vtype.element_type

        # Check if the type is a tuple
        if isinstance(vtype, CtyTuple):
            if 0 <= self.index < len(vtype.element_types):
                elem_type = vtype.element_types[self.index]
                logger.debug(
                    f"🧰✅🔄 Found tuple element type at index {self.index}: {elem_type.__class__.__name__}"
                )
                return elem_type

            if self.index < 0 and abs(self.index) <= len(vtype.element_types):
                # Handle negative indices for tuples
                elem_type = vtype.element_types[len(vtype.element_types) + self.index]
                logger.debug(
                    f"🧰✅🔄 Found tuple element type at negative index {self.index}: {elem_type.__class__.__name__}"
                )
                return elem_type

            error_msg = f"Tuple index {self.index} out of bounds (0-{len(vtype.element_types) - 1})"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Not a collection
        error_msg = f"Cannot index into non-collection type {vtype.__class__.__name__}"
        logger.error(f"🧰❌🔄 {error_msg}")
        raise AttributePathError(error_msg)

    def __str__(self) -> str:
        """Get the string representation of this path step."""
        return f"[{self.index}]"


@define(frozen=True)
class KeyStep(PathStep):
    """
    A path step that gets a value from a map by key.

    This step type is used for maps with non-numeric keys, similar to
    JavaScript's obj["key"] notation.
    """

    key: object = field()

    def apply(self, value: "CtyValue") -> "CtyValue":
        """
        Get the value associated with the given key from a map value.

        Args:
            value: The map value

        Returns:
            CtyValue: The associated value

        Raises:
            AttributePathError: If the value is not a map or has no such key
        """
        logger.debug(f"🧰🔍🔄 Getting value for key {self.key} from map")

        # Check for null values
        if value.is_null:
            logger.error("🧰❌🔄 Cannot get key from null value")
            raise AttributePathError("Cannot get key from null value")

        # Handle unknown values
        if value.is_unknown:
            logger.debug("🧰🔍🔄 Handling unknown value - creating unknown map value")
            # Get the value's type
            val_type = self.apply_type(value.type)

            # Create an unknown value of the value's type
            return CtyValue(vtype=val_type, is_unknown=True)

        # Import types here to avoid circular imports at module level
        from pyvider.cty.types.collections import CtyMap
        from pyvider.cty.types.primitives import CtyNumber, CtyString  # Added CtyString
        from pyvider.cty.types.structural import CtyDynamic

        if isinstance(value.type, CtyDynamic):
            logger.debug("🧰🔍🔄 KeyStep.apply operating on CtyDynamic value")
            current_value_for_lookup = value
            target_internal_value = value.value

            if isinstance(target_internal_value, CtyValue):
                current_value_for_lookup = target_internal_value
                target_internal_value = current_value_for_lookup.value

            if isinstance(target_internal_value, dict):
                str_lookup_key: str
                if isinstance(self.key, CtyValue):
                    # Use the CtyValue's actual value, converting numbers to strings for dict lookup
                    if isinstance(self.key.type, CtyNumber) or isinstance(
                        self.key.type, CtyString
                    ):
                        str_lookup_key = str(self.key.value)
                    else:  # Other CtyValue types are not typical for raw dict keys
                        raise AttributePathError(
                            f"Unsupported CtyValue key type for raw dictionary lookup: {self.key.type}"
                        )
                elif isinstance(self.key, str):
                    str_lookup_key = self.key
                elif isinstance(self.key, int | float | Decimal):  # Raw numeric key
                    str_lookup_key = str(self.key)
                else:
                    raise AttributePathError(
                        f"Unsupported key type for raw dictionary lookup: {type(self.key).__name__}"
                    )

                if str_lookup_key in target_internal_value:
                    retrieved_raw_value = target_internal_value[str_lookup_key]
                    # Since the container is CtyDynamic, the retrieved value is also considered dynamic.
                    return CtyDynamic().validate(retrieved_raw_value)
                else:
                    raise AttributePathError(
                        f"Key '{str_lookup_key}' not found in CtyDynamic's internal dictionary."
                    )
            else:
                raise AttributePathError(
                    f"Cannot get key from CtyDynamic whose internal value is not a dictionary (got {type(target_internal_value).__name__})."
                )

        elif isinstance(value.type, CtyMap):
            # Get the value
            try:
                # CtyMap.get handles key validation and returns a typed CtyValue (or typed null if not found)
                result = value.type.get(value, self.key)

                # Check if the key was actually absent vs. value being explicitly null
                # value.value is the internal dict of the map, value.type.key_type is the CtyType of keys
                # self.key is the key we are looking for

                # Determine the string representation of the key for internal dict lookup
                str_key_for_check: str
                if isinstance(self.key, CtyValue):
                    if (
                        self.key.is_null or self.key.is_unknown
                    ):  # Should be caught by CtyMap.get ideally
                        raise AttributePathError(
                            "Map key in path cannot be null or unknown."
                        )
                    # Convert CtyValue key to its string representation based on map's key_type
                    # This logic assumes map keys are ultimately stored/looked up as strings of their values
                    validated_key_for_check = value.type.key_type.validate(
                        self.key.value
                    )  # Validate raw value
                    str_key_for_check = str(validated_key_for_check.value)

                elif isinstance(self.key, (str, int, float, Decimal)):
                    # Validate raw key against map's key_type then stringify
                    validated_raw_key_for_check = value.type.key_type.validate(self.key)
                    if (
                        validated_raw_key_for_check.is_null
                        or validated_raw_key_for_check.is_unknown
                    ):
                        raise AttributePathError(
                            "Map key in path is null or unknown after validation."
                        )
                    str_key_for_check = str(validated_raw_key_for_check.value)
                else:
                    # This case should ideally be caught by CtyMap.get if the key type is wrong
                    raise AttributePathError(
                        f"Unsupported key type for map lookup: {type(self.key)}"
                    )

                if result.is_null and str_key_for_check not in value.value:
                    raise AttributePathError(
                        f"Map has no key {self.key!r} (key was '{str_key_for_check}')"
                    )
                return result

            except AttributePathError:
                raise  # Re-raise if it's already an AttributePathError (e.g. from key validation in CtyMap.get)
            except Exception as e:  # Catch other errors from CtyMap.get
                error_msg = f"Failed to get value for key {self.key!r} from map: {e}"
                logger.error(f"🧰❌🔄 {error_msg}")
                raise AttributePathError(error_msg) from e
        else:
            error_msg = f"Cannot get key from non-map/non-dynamic value of type {type(value.type).__name__}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

    def apply_type(self, vtype: "CtyType") -> "CtyType":
        """
        Get the type of the value associated with the given key.

        Args:
            vtype: The map type

        Returns:
            CtyType: The value's type

        Raises:
            AttributePathError: If the type is not a map
        """
        from pyvider.cty.types.collections import CtyMap  # Moved import
        from pyvider.cty.types.structural import CtyDynamic  # Moved import

        logger.debug(
            f"🧰🔍🔄 Getting type of value for key {self.key} from type {vtype.__class__.__name__}"
        )

        if isinstance(vtype, CtyDynamic):
            logger.debug("🧰✅🔄 Key access on CtyDynamic type yields CtyDynamic")
            return CtyDynamic()

        if not isinstance(vtype, CtyMap):
            error_msg = f"Cannot get key from non-map type {vtype.__class__.__name__}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Validate the key type compatibility (simplified check, CtyMap.get would do more detailed)
        # We are determining the *resulting type*, so if key is valid for the map's key_type,
        # then the result is the map's value_type.
        # A full key validation (like in apply) is not strictly needed here,
        # but we should check if the key *could* be valid.
        # For simplicity and consistency with go-cty (which allows any key for type navigation),
        # we assume the key is valid for type navigation and directly return value_type.
        # More complex validation could be added if strict key type checking at type-level is needed.
        # Example: if self.key is CtyValue(CtyNumber(1)) and map key_type is CtyString,
        # this would still return map's value_type. The apply method handles the actual lookup failure.

        logger.debug(
            f"🧰✅🔄 Map type found, value type is {vtype.value_type.__class__.__name__}"
        )
        return vtype.value_type

    def __str__(self) -> str:
        """Get the string representation of this path step."""
        # Use repr for the key to handle quoting strings
        return f"[{self.key!r}]"


@define
class CtyPath:
    """
    A path through a nested Cty value.

    A path consists of a sequence of steps, where each step navigates from a
    value to a nested value. Paths can be constructed incrementally and then
    applied to values to extract nested data.
    """

    steps: list[PathStep] = field(factory=list)

    @classmethod
    def empty(cls) -> "CtyPath":
        """Create an empty path."""
        logger.debug("🧰🔍🔄 Creating empty path")
        return cls([])

    @classmethod
    def get_attr(cls, name: str) -> "CtyPath":
        """Create a path with a single attribute step."""
        logger.debug(f"🧰🔍🔄 Creating path with attribute step: {name}")
        return cls([GetAttrStep(name)])

    @classmethod
    def index(cls, index: int) -> "CtyPath":
        """Create a path with a single index step."""
        logger.debug(f"🧰🔍🔄 Creating path with index step: {index}")
        return cls([IndexStep(index)])

    @classmethod
    def key(cls, key: object) -> "CtyPath":
        """Create a path with a single key step."""
        logger.debug(f"🧰🔍🔄 Creating path with key step: {key}")
        return cls([KeyStep(key)])

    def child(self, name: str) -> "CtyPath":
        """Append an attribute step to this path."""
        logger.debug(f"🧰🔍🔄 Adding child attribute step: {name}")
        return CtyPath([*self.steps, GetAttrStep(name)])

    def index_step(self, index: int) -> "CtyPath":
        """Append an index step to this path."""
        logger.debug(f"🧰🔍🔄 Adding index step: {index}")
        return CtyPath([*self.steps, IndexStep(index)])

    def key_step(self, key: object) -> "CtyPath":
        """Append a key step to this path."""
        logger.debug(f"🧰🔍🔄 Adding key step: {key}")
        return CtyPath([*self.steps, KeyStep(key)])

    def apply_path(self, value: object) -> "CtyValue":
        """
        Apply this path to a value to get a nested value.

        Args:
            value: The value to navigate through

        Returns:
            CtyValue: The nested value

        Raises:
            AttributePathError: If the path can't be applied
        """
        logger.debug(f"🧰🔍🔄 Applying path {self} to value")

        # Handle empty path
        if not self.steps:
            logger.debug("🧰✅🔄 Empty path, returning value as is")
            # Return the value directly for empty paths
            return value

        # Start with the given value
        from pyvider.cty.values import CtyValue

        # Make sure we have a CtyValue to start with
        if not isinstance(value, CtyValue):
            error_msg = f"Cannot apply path to non-CtyValue: {type(value).__name__}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        current = value

        # Apply each step in sequence
        for i, step in enumerate(self.steps):
            logger.debug(f"🧰🔍🔄 Applying path step {i + 1}/{len(self.steps)}: {step}")
            try:
                current = step.apply(current)
                logger.debug(f"🧰✅🔄 Step result type: {type(current).__name__}")
            except AttributePathError as e:
                # Preserve the original error message but add path context
                error_msg = f"Error at step {i + 1} ({step}): {e}"
                logger.error(f"🧰❌🔄 {error_msg}")
                raise AttributePathError(error_msg) from e

        logger.debug("🧰✅🔄 Path application complete")
        return current

    def apply_path_type(self, vtype: "CtyType") -> "CtyType":
        """
        Apply this path to a type to get the nested value's type.

        Args:
            vtype: The type to navigate through

        Returns:
            CtyType: The nested value's type

        Raises:
            AttributePathError: If the path can't be applied
        """
        logger.debug(f"🧰🔍🔄 Applying path {self} to type")

        # Handle empty path
        if not self.steps:
            logger.debug("🧰✅🔄 Empty path, returning type as is")
            return vtype

        # Start with the given type
        current = vtype

        # Apply each step in sequence
        for i, step in enumerate(self.steps):
            logger.debug(
                f"🧰🔍🔄 Applying type path step {i + 1}/{len(self.steps)}: {step}"
            )
            try:
                current = step.apply_type(current)
                logger.debug(f"🧰✅🔄 Step result type: {current.__class__.__name__}")
            except AttributePathError as e:
                # Preserve the original error message but add path context
                error_msg = f"Error at type step {i + 1} ({step}): {e}"
                logger.error(f"🧰❌🔄 {error_msg}")
                raise AttributePathError(error_msg) from e

        logger.debug("🧰✅🔄 Path type application complete")
        return current

    def string(self) -> str:
        """Get a string representation of this path."""
        if not self.steps:
            logger.debug("🧰🔍🔄 Empty path has empty string representation")
            return ""

        # Use the string representation of each step
        path_str = "".join(str(step) for step in self.steps)
        logger.debug(f"🧰🔍🔄 Path string representation: {path_str}")
        return path_str

    def __str__(self) -> str:
        """Get a descriptive string representation of this path."""
        path_str = self.string()
        if not path_str:
            return "(empty path)"
        return path_str


# 🐍🏗️🐣
