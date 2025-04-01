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
from typing import Any, List, Optional, TypeVar, cast, Sequence

from attrs import define, field

from pyvider.cty.logger import logger
from pyvider.cty.exceptions import AttributePathError, CtyValidationError
from pyvider.cty.types import (
    CtyType,
    CtyList,
    CtyMap,
    CtyObject,
    CtyTuple,
)
from pyvider.cty.values import CtyValue

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
    def apply_type(self, type_: "CtyType") -> "CtyType":
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

@define(frozen=True)
class GetAttrStep(PathStep):
    """
    A path step that gets an attribute from an object.

    This step type is used for objects with named attributes, similar to
    JavaScript's obj.attr notation.
    """
    name: str = field()

    @name.validator
    def _validate_name(self, attribute, value):
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
        logger.debug(f"🧰🔍🔄 Getting attribute {self.name} from object")

        # Check for null values
        if value.is_null:
            logger.error(f"🧰❌🔄 Cannot get attribute from null value")
            raise AttributePathError("Cannot get attribute from null value")

        # Handle unknown values
        if value.is_unknown:
            logger.debug(f"🧰🔍🔄 Handling unknown value - creating unknown attribute")
            # Get the attribute's type
            attr_type = self.apply_type(value.type)
            
            # Import here to avoid circular imports
            from pyvider.cty.values import CtyValue
            # Create an unknown value of the attribute's type
            return CtyValue(type_=attr_type, is_unknown=True)

        # Check if the type is an object
        from pyvider.cty.types.structural import CtyObject
        if not isinstance(value.type, CtyObject):
            error_msg = f"Cannot get attribute from non-object value of type {type(value.type).__name__}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Get the attribute
        try:
            # For CtyValue containing object data, the value is a dictionary
            object_value = value.value
            
            for k, v in object_value.items():
                if k == self.name:
                    logger.debug(f"🧰✅🔄 Found attribute {self.name}")
                    return v
                    
            # If we get here, the attribute was not found
            error_msg = f"Object has no attribute '{self.name}'"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)
        except Exception as e:
            error_msg = f"Failed to get attribute {self.name}: {e}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

    def apply_type(self, type_: "CtyType") -> "CtyType":
        """
        Get the type of the attribute with the given name.

        Args:
            type_: The object type

        Returns:
            CtyType: The attribute's type

        Raises:
            AttributePathError: If the type is not an object or has no such attribute
        """
        logger.debug(f"🧰🔍🔄 Getting type of attribute {self.name} from object type")

        # Check if the type is an object
        from pyvider.cty.types.structural import CtyObject
        if not isinstance(type_, CtyObject):
            error_msg = f"Cannot get attribute from non-object type {type_.__class__.__name__}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Get the attribute's type
        if not type_.has_attribute(self.name):
            error_msg = f"Object type has no attribute {self.name}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        attr_type = type_.attribute_types[self.name]
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
            logger.error(f"🧰❌🔄 Cannot index into null value")
            raise AttributePathError("Cannot index into null value")

        # Handle unknown values
        if value.is_unknown:
            logger.debug(f"🧰🔍🔄 Handling unknown value - creating unknown element")
            # Get the element's type
            elem_type = self.apply_type(value.type)
            
            # Import here to avoid circular imports
            from pyvider.cty.values import CtyValue
            # Create an unknown value of the element's type
            return CtyValue(type_=elem_type, is_unknown=True)

        # Check if the type is a list or tuple
        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyTuple

        try:
            collection_value = value.value
            calculated_index = self.index
            
            # Handle negative indices
            if calculated_index < 0:
                logger.debug(f"🧰🔍🔄 Converting negative index {calculated_index} to positive")
                collection_len = len(collection_value)
                calculated_index = collection_len + calculated_index
                logger.debug(f"🧰🔍🔄 Converted to positive index {calculated_index}")
                
            # Check bounds (happens in both paths below but we do an explicit check here)
            if calculated_index < 0 or calculated_index >= len(collection_value):
                raise IndexError(f"Index {self.index} out of bounds (0-{len(collection_value)-1})")
                
            if isinstance(value.type, CtyList):
                # For lists, use element_at method
                logger.debug(f"🧰🔍🔄 Using element_at for list type")
                result = value.type.element_at(collection_value, calculated_index)
                logger.debug(f"🧰✅🔄 Retrieved element at index {calculated_index}")
                return result
            elif isinstance(value.type, CtyTuple):
                # For tuples, use element_at method
                logger.debug(f"🧰🔍🔄 Using element_at for tuple type")
                result = value.type.element_at(collection_value, calculated_index)
                logger.debug(f"🧰✅🔄 Retrieved element at index {calculated_index}")
                return result
            else:
                error_msg = f"Cannot index into value of type {type(value.type).__name__}"
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

    def apply_type(self, type_: "CtyType") -> "CtyType":
        """
        Get the type of the element at the given index.

        Args:
            type_: The collection type

        Returns:
            CtyType: The element's type

        Raises:
            AttributePathError: If the type is not a collection
        """
        logger.debug(f"🧰🔍🔄 Getting type of element at index {self.index} from collection type")

        # Import types to avoid circular imports
        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyTuple

        # Check if the type is a list
        if isinstance(type_, CtyList):
            logger.debug(f"🧰✅🔄 Found list type, element type is {type_.element_type.__class__.__name__}")
            return type_.element_type

        # Check if the type is a tuple
        if isinstance(type_, CtyTuple):
            if 0 <= self.index < len(type_.element_types):
                elem_type = type_.element_types[self.index]
                logger.debug(f"🧰✅🔄 Found tuple element type at index {self.index}: {elem_type.__class__.__name__}")
                return elem_type
                
            if self.index < 0 and abs(self.index) <= len(type_.element_types):
                # Handle negative indices for tuples
                elem_type = type_.element_types[len(type_.element_types) + self.index]
                logger.debug(f"🧰✅🔄 Found tuple element type at negative index {self.index}: {elem_type.__class__.__name__}")
                return elem_type
                
            error_msg = f"Tuple index {self.index} out of bounds (0-{len(type_.element_types)-1})"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Not a collection
        error_msg = f"Cannot index into non-collection type {type_.__class__.__name__}"
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
    key: Any = field()

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
            logger.error(f"🧰❌🔄 Cannot get key from null value")
            raise AttributePathError("Cannot get key from null value")

        # Handle unknown values
        if value.is_unknown:
            logger.debug(f"🧰🔍🔄 Handling unknown value - creating unknown map value")
            # Get the value's type
            val_type = self.apply_type(value.type)
            
            # Import here to avoid circular imports
            from pyvider.cty.values import CtyValue
            # Create an unknown value of the value's type
            return CtyValue(type_=val_type, is_unknown=True)

        # Check if the type is a map
        from pyvider.cty.types.collections import CtyMap
        if not isinstance(value.type, CtyMap):
            error_msg = f"Cannot get key from non-map value of type {type(value.type).__name__}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Get the value
        try:
            # For map types, we need to validate and then search for the key
            map_value = value.value
            
            # Try to validate the key
            key_type = value.type.key_type
            if not isinstance(self.key, type(key_type)):
                # Validate the key
                validated_key = key_type.validate(self.key)
            else:
                validated_key = self.key
                
            # Search for the key in the map
            for k, v in map_value.items():
                if hasattr(k, 'value') and hasattr(validated_key, 'value'):
                    # Compare CtyValues by their internal values
                    if k.value == validated_key.value:
                        logger.debug(f"🧰✅🔄 Found value for key {self.key}")
                        return v
                elif k == validated_key:
                    # Direct comparison
                    logger.debug(f"🧰✅🔄 Found value for key {self.key}")
                    return v
                    
            # Key not found
            error_msg = f"Map has no key {self.key}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)
                
        except AttributePathError:
            # Re-raise AttributePathError
            raise
        except Exception as e:
            error_msg = f"Failed to get value for key {self.key}: {e}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

    def apply_type(self, type_: "CtyType") -> "CtyType":
        """
        Get the type of the value associated with the given key.

        Args:
            type_: The map type

        Returns:
            CtyType: The value's type

        Raises:
            AttributePathError: If the type is not a map
        """
        logger.debug(f"🧰🔍🔄 Getting type of value for key {self.key} from map type")

        # Check if the type is a map
        from pyvider.cty.types.collections import CtyMap
        if not isinstance(type_, CtyMap):
            error_msg = f"Cannot get key from non-map type {type_.__class__.__name__}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Validate the key
        try:
            key_str = str(self.key)
            type_.key_type.validate(key_str)
            logger.debug(f"🧰✅🔄 Key {key_str} is valid for this map type")
        except CtyValidationError as e:
            error_msg = f"Invalid key for map: {e}"
            logger.error(f"🧰❌🔄 {error_msg}")
            raise AttributePathError(error_msg)

        # Return the value type
        logger.debug(f"🧰✅🔄 Found value type: {type_.value_type.__class__.__name__}")
        return type_.value_type

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
    steps: List[PathStep] = field(factory=list)

    @classmethod
    def empty(cls) -> 'Path':
        """Create an empty path."""
        logger.debug("🧰🔍🔄 Creating empty path")
        return cls([])

    @classmethod
    def get_attr(cls, name: str) -> 'Path':
        """Create a path with a single attribute step."""
        logger.debug(f"🧰🔍🔄 Creating path with attribute step: {name}")
        return cls([GetAttrStep(name)])

    @classmethod
    def index(cls, index: int) -> 'Path':
        """Create a path with a single index step."""
        logger.debug(f"🧰🔍🔄 Creating path with index step: {index}")
        return cls([IndexStep(index)])

    @classmethod
    def key(cls, key: Any) -> 'Path':
        """Create a path with a single key step."""
        logger.debug(f"🧰🔍🔄 Creating path with key step: {key}")
        return cls([KeyStep(key)])

    def child(self, name: str) -> 'Path':
        """Append an attribute step to this path."""
        logger.debug(f"🧰🔍🔄 Adding child attribute step: {name}")
        return CtyPath(self.steps + [GetAttrStep(name)])

    def index_step(self, index: int) -> 'Path':
        """Append an index step to this path."""
        logger.debug(f"🧰🔍🔄 Adding index step: {index}")
        return CtyPath(self.steps + [IndexStep(index)])

    def key_step(self, key: Any) -> 'Path':
        """Append a key step to this path."""
        logger.debug(f"🧰🔍🔄 Adding key step: {key}")
        return CtyPath(self.steps + [KeyStep(key)])

    def apply_path(self, value: Any) -> "CtyValue":
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
            logger.debug(f"🧰🔍🔄 Applying path step {i+1}/{len(self.steps)}: {step}")
            try:
                current = step.apply(current)
                logger.debug(f"🧰✅🔄 Step result type: {type(current).__name__}")
            except AttributePathError as e:
                # Preserve the original error message but add path context
                error_msg = f"Error at step {i+1} ({step}): {e}"
                logger.error(f"🧰❌🔄 {error_msg}")
                raise AttributePathError(error_msg) from e

        logger.debug(f"🧰✅🔄 Path application complete")
        return current

    def apply_path_type(self, type_: "CtyType") -> "CtyType":
        """
        Apply this path to a type to get the nested value's type.

        Args:
            type_: The type to navigate through

        Returns:
            CtyType: The nested value's type

        Raises:
            AttributePathError: If the path can't be applied
        """
        logger.debug(f"🧰🔍🔄 Applying path {self} to type")

        # Handle empty path
        if not self.steps:
            logger.debug("🧰✅🔄 Empty path, returning type as is")
            return type_

        # Start with the given type
        current = type_
        
        # Apply each step in sequence
        for i, step in enumerate(self.steps):
            logger.debug(f"🧰🔍🔄 Applying type path step {i+1}/{len(self.steps)}: {step}")
            try:
                current = step.apply_type(current)
                logger.debug(f"🧰✅🔄 Step result type: {current.__class__.__name__}")
            except AttributePathError as e:
                # Preserve the original error message but add path context
                error_msg = f"Error at type step {i+1} ({step}): {e}"
                logger.error(f"🧰❌🔄 {error_msg}")
                raise AttributePathError(error_msg) from e

        logger.debug(f"🧰✅🔄 Path type application complete")
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
