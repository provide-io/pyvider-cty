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

from pyvider.cty.exceptions import AttributePathError, CtyValidationError
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
    def _validate_name(self, attribute, value) -> None:
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
                raise AttributePathError(error_msg)

        # For map values, use get method with string key
        elif isinstance(value.type, CtyMap):
            result = value.type.get(value, self.name)
            if result is None:
                error_msg = f"Key '{self.name}' not found in map"
                logger.error(f"🧰❌🔄 {error_msg}")
                raise AttributePathError(error_msg)
            return result

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
            raise AttributePathError(error_msg)
        except Exception as e:
            error_msg = f"Failed to get element at index {self.index}: {e}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

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

        # Check if the type is a map
        from pyvider.cty.types.collections import CtyMap

        if not isinstance(value.type, CtyMap):
            error_msg = (
                f"Cannot get key from non-map value of type {type(value.type).__name__}"
            )
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Get the value
        try:
            map_value = (
                value.value
            )  # This is the Python dict: {'str_key': CtyValue_for_val, ...}

            str_lookup_key: str
            # Import CtyNumber and CtyString for type checking
            from pyvider.cty.types.primitives import CtyNumber, CtyString

            if isinstance(self.key, CtyValue):
                if self.key.is_null or self.key.is_unknown:
                    raise AttributePathError(
                        f"Invalid CtyValue key in path step: {self.key!r}"
                    )

                # If the map's key_type is CtyString and the path key is CtyNumber, convert to string for lookup.
                if isinstance(value.type.key_type, CtyString) and isinstance(
                    self.key.type, CtyNumber
                ):
                    str_lookup_key = str(self.key.value)
                    logger.debug(
                        f"🧰🔑🔄 Converted CtyNumber path key to string '{str_lookup_key}' for map lookup (map key type is CtyString)"
                    )
                elif isinstance(
                    self.key.type, value.type.key_type.__class__
                ):  # Key type matches map's key_type
                    # Assuming the CtyValue's internal value is directly usable or stringifiable if it's a CtyString.
                    # For CtyString keys, self.key.value should already be a string.
                    str_lookup_key = str(self.key.value)
                else:
                    # This case should ideally be caught by apply_type's usable_as check first,
                    # but as a safeguard or for direct apply calls:
                    raise AttributePathError(
                        f"Path key type {self.key.type} is not directly compatible with map key type {value.type.key_type} for lookup."
                    )

            elif isinstance(
                self.key, str | int | float | Decimal
            ):  # Raw Python type for key
                # If map key_type is CtyString, convert raw numeric key to string for lookup
                if isinstance(value.type.key_type, CtyString) and isinstance(
                    self.key, int | float | Decimal
                ):
                    str_lookup_key = str(self.key)
                    logger.debug(
                        f"🧰🔑🔄 Converted raw numeric path key to string '{str_lookup_key}' for map lookup (map key type is CtyString)"
                    )
                elif isinstance(self.key, str) and isinstance(
                    value.type.key_type, CtyString
                ):
                    str_lookup_key = self.key
                else:
                    # For other raw key types or non-string map key_types,
                    # we might need more sophisticated handling or rely on direct match.
                    # For now, assume direct string conversion if not string already.
                    # This part might need refinement if maps can have non-string raw keys that aren't CtyString typed.
                    # However, CtyMap typically implies CtyString or other CtyPrimitive keys.
                    # The most robust way is to validate and convert, similar to apply_type.
                    try:
                        validated_raw_key = value.type.key_type.validate(self.key)
                        if (
                            not validated_raw_key.is_unknown
                            and not validated_raw_key.is_null
                        ):
                            str_lookup_key = str(validated_raw_key.value)
                        else:
                            raise AttributePathError(
                                f"Raw key in path step is null or unknown after validation: {self.key!r}"
                            )
                    except CtyValidationError as e:
                        raise AttributePathError(
                            f"Invalid raw key type in path step: {self.key!r} ({e})"
                        )
            else:
                raise AttributePathError(
                    f"Unsupported key type in path step: {type(self.key).__name__}"
                )

            if str_lookup_key in map_value:
                logger.debug(f"🧰✅🔄 Found value for key {str_lookup_key}")
                return map_value[str_lookup_key]

            # Key not found
            error_msg = f"Map has no key {self.key!r}"  # Use self.key for error reporting to show original key
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        except AttributePathError:
            # Re-raise AttributePathError
            raise
        except Exception as e:
            error_msg = f"Failed to get value for key {self.key!r}: {e}"  # Use self.key for error reporting
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
        logger.debug(f"🧰🔍🔄 Getting type of value for key {self.key} from map type")

        # Check if the type is a map
        from pyvider.cty.types.collections import CtyMap

        if not isinstance(vtype, CtyMap):
            error_msg = f"Cannot get key from non-map type {vtype.__class__.__name__}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Validate the key
        key_to_validate: object
        original_key_for_error_reporting = (
            self.key
        )  # Store original key for error messages

        if isinstance(self.key, CtyValue):
            # Import CtyNumber and CtyString for this specific check
            from pyvider.cty.types.primitives import (
                CtyNumber as PrimitivesCtyNumber,  # Use alias to avoid conflict
                CtyString as PrimitivesCtyString,  # Use alias
            )

            is_number_key_for_string_map = isinstance(
                self.key.type, PrimitivesCtyNumber
            ) and isinstance(vtype.key_type, PrimitivesCtyString)

            if not is_number_key_for_string_map and not self.key.type.usable_as(
                vtype.key_type
            ):
                raise AttributePathError(
                    f"Invalid CtyValue key type in path step: {self.key.type} is not usable as {vtype.key_type}"
                )

            if self.key.is_null or self.key.is_unknown:
                raise AttributePathError(
                    f"Key in path step is null or unknown: {self.key!r}"
                )

            key_to_validate = self.key.value
            original_key_for_error_reporting = self.key.value

            if is_number_key_for_string_map:
                key_to_validate = str(key_to_validate)
                logger.debug(
                    f"🧰🔑🔄 Converted CtyNumber key's value to string for CtyString map key validation: '{key_to_validate}'"
                )
        else:
            # If the key is a raw Python value, it will be stringified by CtyString.validate if key_type is CtyString.
            key_to_validate = self.key
            # For raw Python keys that are numbers and map key_type is string, CtyString.validate would fail.
            # We need to convert them to string here as well.
            from pyvider.cty.types.primitives import (
                CtyString,  # Ensure CtyString is available
            )

            # We also need CtyNumber to check the type of raw key_to_validate
            # However, raw Python ints/floats are not CtyNumber.
            # We rely on CtyString.validate to attempt conversion or fail for raw types.
            # This part might need adjustment if CtyString.validate is too strict for raw numbers.
            # For now, the primary fix is for CtyValue keys.
            # Let's add a specific check for raw numbers if the map key is CtyString
            if isinstance(key_to_validate, int | float | Decimal) and isinstance(
                vtype.key_type, CtyString
            ):
                key_to_validate = str(key_to_validate)
                logger.debug(
                    f"🧰🔑🔄 Converted raw numeric key to string for CtyString map key validation: '{key_to_validate}'"
                )

        try:
            # The map's key_type (e.g., CtyString) validates the key_to_validate.
            vtype.key_type.validate(
                key_to_validate
            )  # Now CtyString.validate receives a string if conversion happened
            logger.debug(
                f"🧰✅🔄 Key {key_to_validate!r} is valid for this map type {vtype.key_type}"
            )
        except CtyValidationError as e:
            # This message should reflect that the key_to_validate (derived from self.key) is not valid.
            # Use original_key_for_error_reporting for consistency in error messages.
            error_msg = f"Invalid key for map: {original_key_for_error_reporting!r} is not a valid {vtype.key_type} (validation error: {e})"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Return the value type
        logger.debug(f"🧰✅🔄 Found value type: {vtype.value_type.__class__.__name__}")
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
