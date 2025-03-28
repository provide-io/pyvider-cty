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

import asyncio
from abc import ABC, abstractmethod
from typing import Any, List, Optional, TypeVar, cast

import attrs

from pyvider.cty.logger import logger
from pyvider.cty.exceptions import AttributePathError, ValidationError

# Import here to avoid circular import issues
from pyvider.cty.values.base import CtyValue

# Type variables for better type hints
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class PathStep(ABC):
    """
    Base class for path steps.

    A path step represents a single segment in a path, such as an attribute
    name, an index, or a map key.
    """

    @abstractmethod
    async def apply(self, value: CtyValue) -> CtyValue:
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
    async def apply_type(self, type_: "CtyType") -> "CtyType":
        """
        Apply this step to a type to get the nested value's type.

        Args:
            type_: The type to navigate through

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

@attrs.define(frozen=True)
class GetAttrStep(PathStep):
    """
    A path step that gets an attribute from an object.

    This step type is used for objects with named attributes, similar to
    JavaScript's obj.attr notation.
    """
    name: str = attrs.field()

    @name.validator
    def _validate_name(self, attribute, value):
        if not value:
            raise ValueError("Attribute name cannot be empty")

    async def apply(self, value: CtyValue) -> CtyValue:
        """
        Get the attribute with the given name from an object value.

        Args:
            value: The object value

        Returns:
            CtyValue: The attribute value

        Raises:
            AttributePathError: If the value is not an object or has no such attribute
        """
        logger.debug(f"🧰🔍✅ Getting attribute {self.name} from object")

        # Check for null values
        if value.is_null:
            raise AttributePathError("Cannot get attribute from null value")

        # Handle unknown values
        if value.is_unknown:
            # If we have a refinement that constrains the object, we might
            # be able to get the attribute's type
            attr_type = await self.apply_type(value.type)

            # Create an unknown value of the attribute's type
            from pyvider.cty.values import CtyValue
            return CtyValue(type_=attr_type, is_unknown=True)

        # Check if the type is an object
        from pyvider.cty.types.structural import CtyObject
        if not isinstance(value.type, CtyObject):
            raise AttributePathError(
                f"Cannot get attribute from non-object value of type {type(value.type).__name__}"
            )

        # Get the attribute
        try:
            # Use get_attribute method from CtyObject
            return value.type.get_attribute(value.value, self.name)
        except Exception as e:
            raise AttributePathError(f"Failed to get attribute {self.name}: {e}")

    async def apply_type(self, type_: "CtyType") -> "CtyType":
        """
        Get the type of the attribute with the given name.

        Args:
            type_: The object type

        Returns:
            CtyType: The attribute's type

        Raises:
            AttributePathError: If the type is not an object or has no such attribute
        """
        logger.debug(f"🧰🔍✅ Getting type of attribute {self.name} from object type")

        # Check if the type is an object
        from pyvider.cty.types.structural import CtyObject
        if not isinstance(type_, CtyObject):
            raise AttributePathError(
                f"Cannot get attribute from non-object type {type_.__class__.__name__}"
            )

        # Get the attribute's type
        if not type_.has_attribute(self.name):
            raise AttributePathError(f"Object type has no attribute {self.name}")

        return type_.attribute_types[self.name]

    def __str__(self) -> str:
        return f".{self.name}"

@attrs.define(frozen=True)
class IndexStep(PathStep):
    """
    A path step that indexes into a list, tuple, or string.

    This step type is used for collections with numeric indexes, similar to
    JavaScript's arr[i] notation.
    """
    index: int = attrs.field()

    async def apply(self, value: CtyValue) -> CtyValue:
        """
        Get the element at the given index from a list or tuple value.

        Args:
            value: The list or tuple value

        Returns:
            CtyValue: The element value

        Raises:
            AttributePathError: If the value is not a list or tuple, or the index is out of bounds
        """
        logger.debug(f"🧰🔍✅ Getting element at index {self.index} from collection")

        # Check for null values
        if value.is_null:
            raise AttributePathError("Cannot index into null value")

        # Handle unknown values
        if value.is_unknown:
            # If we have a refinement that constrains the list, we might
            # be able to get the element's type
            elem_type = await self.apply_type(value.type)

            # Create an unknown value of the element's type
            from pyvider.cty.values import CtyValue
            return CtyValue(type_=elem_type, is_unknown=True)

        # Check if the type is a list, tuple, or string
        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyTuple

        if isinstance(value.type, CtyList):
            # For lists, use element_at method
            try:
                list_value = value.value
                return value.type.element_at(list_value, self.index)
            except IndexError as e:
                raise AttributePathError(f"Index out of bounds: {e}")
            except Exception as e:
                raise AttributePathError(f"Failed to get element at index {self.index}: {e}")

        elif isinstance(value.type, CtyTuple):
            # For tuples, use element_at method
            try:
                tuple_value = value.value
                return value.type.element_at(tuple_value, self.index)
            except IndexError as e:
                raise AttributePathError(f"Index out of bounds: {e}")
            except Exception as e:
                raise AttributePathError(f"Failed to get element at index {self.index}: {e}")

        else:
            raise AttributePathError(
                f"Cannot index into value of type {type(value.type).__name__}"
            )

    async def apply_type(self, type_: "CtyType") -> "CtyType":
        """
        Get the type of the element at the given index.

        Args:
            type_: The collection type

        Returns:
            CtyType: The element's type

        Raises:
            AttributePathError: If the type is not a collection
        """
        logger.debug(f"🧰🔍✅ Getting type of element at index {self.index} from collection type")

        # Import types to avoid circular imports
        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyTuple

        # Check if the type is a list
        if isinstance(type_, CtyList):
            return type_.element_type

        # Check if the type is a tuple
        if isinstance(type_, CtyTuple):
            if self.index < 0 or self.index >= len(type_.element_types):
                raise AttributePathError(f"Tuple index {self.index} out of bounds")

            return type_.element_types[self.index]

        # Not a collection
        raise AttributePathError(
            f"Cannot index into non-collection type {type_.__class__.__name__}"
        )

    def __str__(self) -> str:
        return f"[{self.index}]"

@attrs.define(frozen=True)
class KeyStep(PathStep):
    """
    A path step that gets a value from a map by key.

    This step type is used for maps with non-numeric keys, similar to
    JavaScript's obj["key"] notation.
    """
    key: Any = attrs.field()

    async def apply(self, value: CtyValue) -> CtyValue:
        """
        Get the value associated with the given key from a map value.

        Args:
            value: The map value

        Returns:
            CtyValue: The associated value

        Raises:
            AttributePathError: If the value is not a map or has no such key
        """
        logger.debug(f"🧰🔍✅ Getting value for key {self.key} from map")

        # Check for null values
        if value.is_null:
            raise AttributePathError("Cannot get key from null value")

        # Handle unknown values
        if value.is_unknown:
            # If we have a refinement that constrains the map, we might
            # be able to get the value's type
            val_type = await self.apply_type(value.type)

            # Create an unknown value of the value's type
            from pyvider.cty.values import CtyValue
            return CtyValue(type_=val_type, is_unknown=True)

        # Check if the value is a map
        from pyvider.cty.types.collections import CtyMap
        if not isinstance(value.type, CtyMap):
            raise AttributePathError(
                f"Cannot get key from non-map value of type {type(value.type).__name__}"
            )

        # Get the value
        try:
            # Use the get method from CtyMap
            map_value = value.value
            result = value.type.get(map_value, self.key)

            if result is None:
                raise AttributePathError(f"Map has no key {self.key}")

            return result
        except AttributePathError:
            # Re-raise AttributePathError
            raise
        except Exception as e:
            raise AttributePathError(f"Failed to get value for key {self.key}: {e}")

    async def apply_type(self, type_: "CtyType") -> "CtyType":
        """
        Get the type of the value associated with the given key.

        Args:
            type_: The map type

        Returns:
            CtyType: The value's type

        Raises:
            AttributePathError: If the type is not a map
        """
        logger.debug(f"🧰🔍✅ Getting type of value for key {self.key} from map type")

        # Check if the type is a map
        from pyvider.cty.types.collections import CtyMap
        if not isinstance(type_, CtyMap):
            raise AttributePathError(
                f"Cannot get key from non-map type {type_.__class__.__name__}"
            )

        # Validate the key
        try:
            str_key = str(self.key)
            type_.key_type.validate(str_key)
        except ValidationError as e:
            raise AttributePathError(f"Invalid key for map: {e}")

        # Return the value type
        return type_.value_type

    def __str__(self) -> str:
        return f"[{self.key!r}]"

@attrs.define
class Path:
    """
    A path through a nested Cty value.

    A path consists of a sequence of steps, where each step navigates from a
    value to a nested value. Paths can be constructed incrementally and then
    applied to values to extract nested data.
    """
    steps: List[PathStep] = attrs.field(factory=list)

    @classmethod
    def empty(cls) -> 'Path':
        """Create an empty path."""
        return cls([])

    @classmethod
    def get_attr(cls, name: str) -> 'Path':
        """Create a path with a single attribute step."""
        return cls([GetAttrStep(name)])

    @classmethod
    def index(cls, index: int) -> 'Path':
        """Create a path with a single index step."""
        return cls([IndexStep(index)])

    @classmethod
    def key(cls, key: Any) -> 'Path':
        """Create a path with a single key step."""
        return cls([KeyStep(key)])

    def child(self, name: str) -> 'Path':
        """Append an attribute step to this path."""
        return Path(self.steps + [GetAttrStep(name)])

    def index_step(self, index: int) -> 'Path':
        """Append an index step to this path."""
        return Path(self.steps + [IndexStep(index)])

    def key_step(self, key: Any) -> 'Path':
        """Append a key step to this path."""
        return Path(self.steps + [KeyStep(key)])

    async def apply_path(self, value: Any) -> CtyValue:
        """
        Apply this path to a value to get a nested value.

        Args:
            value: The value to navigate through

        Returns:
            CtyValue: The nested value

        Raises:
            AttributePathError: If the path can't be applied
        """
        logger.debug(f"🧰🔍✅ Applying path {self} to value")

        # Start with the given value
        from pyvider.cty.values import CtyValue

        # Ensure we have a CtyValue
        if not isinstance(value, CtyValue):
            # This handles the case where we're given a raw dictionary
            # (like in tests where we validate an object and then pass the
            # validated dictionary directly)
            if isinstance(value, dict) and hasattr(value, "get"):
                # We need to know the type - we'll try to infer it from the test
                from pyvider.cty.types.structural import CtyObject

                # Create a dynamic type based on the keys and values in the dict
                attribute_types = {}
                for k, v in value.items():
                    if hasattr(v, "type"):
                        attribute_types[k] = v.type

                # Create a CtyObject type
                if attribute_types:
                    obj_type = CtyObject(attribute_types=attribute_types)
                    current = CtyValue(type_=obj_type, value=value)
                else:
                    # We can't determine the type, warn and continue
                    logger.warning("🧰❗⚠️ Unable to determine type for raw dictionary")
                    raise AttributePathError("Cannot apply path to raw dictionary without known type")
            else:
                raise AttributePathError(f"Cannot apply path to non-CtyValue: {type(value).__name__}")
        else:
            current = value

        # Apply each step in sequence
        for step in self.steps:
            current = await step.apply(current)

        return current

    async def apply_path_type(self, type_: "CtyType") -> "CtyType":
        """
        Apply this path to a type to get the nested value's type.

        Args:
            type_: The type to navigate through

        Returns:
            CtyType: The nested value's type

        Raises:
            AttributePathError: If the path can't be applied
        """
        logger.debug(f"🧰🔍✅ Applying path {self} to type")

        # Start with the given type
        current = type_

        # Apply each step in sequence
        for step in self.steps:
            current = await step.apply_type(current)

        return current

    def string(self) -> str:
        """Get a string representation of this path."""
        if not self.steps:
            return ""

        # Use the string representation of each step
        return "".join(str(step) for step in self.steps)

    def __str__(self) -> str:
        return self.string() or "(empty path)"
