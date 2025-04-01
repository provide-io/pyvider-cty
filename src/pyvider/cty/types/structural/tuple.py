#
# pyvider/cty/types/structural/tuple.py
#

"""
CtyTuple implementation for Cty tuple types.

Provides a complete implementation of tuple types with fixed-position elements
that may have different types from each other.
"""

from typing import Any, ClassVar, Sequence, cast, List, Tuple

from attrs import define, field

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType


@define(frozen=True, slots=True)
class CtyTuple(CtyType[tuple[Any, ...]]):
    """
    Represents a Cty tuple type with fixed-position elements of potentially different types.

    A tuple is similar to a list but with a fixed number of elements, each potentially
    having a different type. This matches Go-CTY's tuple type semantics.
    """
    ctype: ClassVar[str] = "tuple"
    element_types: tuple[CtyType, ...] = field()

    @element_types.validator
    def _validate_element_types(self, attribute, value):
        """Validate that element_types contains only CtyType instances."""
        logger.debug(f"🧩🔍🔄 Validating tuple element types: {value}")

        if not isinstance(value, tuple):
            error_msg = f"element_types must be a tuple, got {type(value).__name__}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise TypeError(error_msg)

        for i, typ in enumerate(value):
            if not isinstance(typ, CtyType):
                error_msg = f"Element type at index {i} must be a CtyType, got {type(typ).__name__}"
                logger.error(f"🧩❌🔄 {error_msg}")
                raise TypeError(error_msg)

        logger.debug(f"🧩✅🔄 Tuple element types validated successfully: {len(value)} types")

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate a value against this tuple type.

        Args:
            value: Value to validate

        Returns:
            The validated tuple value

        Raises:
            CtyValidationError: If the value doesn't match this tuple type
        """
        from pyvider.cty.values import CtyValue
        logger.debug(f"🧩🔍🔄 Validating value against CtyTuple: {value}")

        # Validate basic type
        if not isinstance(value, (tuple, list)):
            error_msg = f"Expected tuple or list, got {type(value).__name__}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise CtyValidationError(error_msg)

        # Check length
        if len(value) != len(self.element_types):
            error_msg = f"Expected {len(self.element_types)} elements, got {len(value)}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise CtyValidationError(error_msg)

        # Validate each element against its corresponding type
        validated_elements = []

        for i, (element, element_type) in enumerate(zip(value, self.element_types)):
            try:
                logger.debug(f"🧩🔍🔄 Validating tuple element {i} against {element_type}")
                validated_element = element_type.validate(element)
                validated_elements.append(validated_element)
                logger.debug(f"🧩✅🔄 Tuple element {i} validated successfully")
            except CtyValidationError as e:
                error_msg = f"Invalid value for tuple element {i}: {e}"
                logger.error(f"🧩❌🔄 {error_msg}")
                raise CtyValidationError(error_msg) from e
            except Exception as e:
                error_msg = f"Unexpected error validating tuple element {i}: {e}"
                logger.error(f"🧩❌🔄 {error_msg}")
                raise CtyValidationError(error_msg) from e

        logger.debug(f"🧩✅🔄 Tuple validated successfully with {len(validated_elements)} elements")
        return CtyValue(type_=self, value=tuple(validated_elements))

    def element_at(self, container: Any, index: int) -> "CtyValue":
        """
        Get an element at a specific index in the tuple.

        Args:
            container: The tuple or CtyTuple to get the element from
            index: The index to get the element at

        Returns:
            The element at the specified index

        Raises:
            CtyValidationError: If the container is not a tuple or CtyTuple
            IndexError: If the index is out of bounds
        """
        logger.debug(f"🧩🔍🔄 Getting element at index {index} from tuple")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        # Handle different container types
        container_value = None
        if hasattr(container, 'value'):
            # Handle CtyValue containing a tuple
            container_value = container.value
        elif isinstance(container, (tuple, list)):
            # Handle raw tuple
            container_value = container
        else:
            error_msg = f"Expected tuple, list, or CtyValue, got {type(container).__name__}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise CtyValidationError(error_msg)

        # Handle negative indices
        elem_count = len(container_value)
        if index < 0:
            index = elem_count + index

        # Check bounds
        if not 0 <= index < elem_count:
            error_msg = f"Index {index} out of bounds (0-{elem_count-1})"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise IndexError(error_msg)

        # Return the element at the specified index
        element = container_value[index]
        logger.debug(f"🧩✅🔄 Got element at index {index}")
        return element

    def slice(self, container: Any, start: int, end: int) -> "CtyValue":
        """
        Get a slice of the tuple.

        Args:
            container: The tuple to slice
            start: The start index (inclusive)
            end: The end index (exclusive)

        Returns:
            A new CtyValue with the sliced tuple

        Raises:
            CtyValidationError: If the container is not a tuple or CtyTuple
            IndexError: If the indices are out of bounds
        """
        logger.debug(f"🧩🔍🔄 Slicing tuple from {start} to {end}")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        # Handle different container types
        container_value = None
        if hasattr(container, 'value'):
            # Handle CtyValue containing a tuple
            container_value = container.value
        elif isinstance(container, (tuple, list)):
            # Handle raw tuple
            container_value = container
        else:
            error_msg = f"Expected tuple, list, or CtyValue, got {type(container).__name__}"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise CtyValidationError(error_msg)

        # Handle negative indices
        elem_count = len(container_value)
        if start < 0:
            start = elem_count + start
        if end < 0:
            end = elem_count + end

        # Check bounds
        if not 0 <= start <= elem_count:
            error_msg = f"Start index {start} out of bounds (0-{elem_count})"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise IndexError(error_msg)

        if not 0 <= end <= elem_count:
            error_msg = f"End index {end} out of bounds (0-{elem_count})"
            logger.error(f"🧩❌🔄 {error_msg}")
            raise IndexError(error_msg)

        # Get the sliced values and types
        sliced_values = container_value[start:end]
        sliced_types = self.element_types[start:end]

        # Create a new tuple type with the sliced types
        sliced_type = CtyTuple(element_types=sliced_types)

        # Create a new CtyValue with the sliced tuple
        logger.debug(f"🧩✅🔄 Created sliced tuple with {len(sliced_values)} elements")
        return CtyValue(type_=sliced_type, value=tuple(sliced_values))

    def equal(self, other: CtyType) -> bool:
        """
        Check if this tuple type is equal to another type.

        Args:
            other: The other type to compare with

        Returns:
            True if the types are equal, False otherwise
        """
        logger.debug(f"🧩🔍🔄 Checking equality with {other.__class__.__name__}")

        if not isinstance(other, CtyTuple):
            logger.debug(f"🧩❌🔄 Not equal: {other.__class__.__name__} is not CtyTuple")
            return False

        if len(self.element_types) != len(other.element_types):
            logger.debug(f"🧩❌🔄 Not equal: different number of elements ({len(self.element_types)} vs {len(other.element_types)})")
            return False

        for i, (self_type, other_type) in enumerate(zip(self.element_types, other.element_types)):
            if not self_type.equal(other_type):
                logger.debug(f"🧩❌🔄 Not equal: element type at index {i} differs")
                return False

        logger.debug("🧩✅🔄 Tuple types are equal")
        return True

    def usable_as(self, other: CtyType) -> bool:
        """
        Check if this tuple type can be used as another type.

        Args:
            other: The other type to check compatibility with

        Returns:
            True if this type can be used as the other type, False otherwise
        """
        logger.debug(f"🧩🔍🔄 Checking usability as {other.__class__.__name__}")

        if not isinstance(other, CtyTuple):
            logger.debug(f"🧩❌🔄 Not usable as: {other.__class__.__name__} is not CtyTuple")
            return False

        if len(self.element_types) != len(other.element_types):
            logger.debug(f"🧩❌🔄 Not usable as: different number of elements ({len(self.element_types)} vs {len(other.element_types)})")
            return False

        for i, (self_type, other_type) in enumerate(zip(self.element_types, other.element_types)):
            if not self_type.usable_as(other_type):
                logger.debug(f"🧩❌🔄 Not usable as: element type at index {i} not compatible")
                return False

        logger.debug("🧩✅🔄 Tuple type is usable as target type")
        return True

    def __str__(self) -> str:
        """Get string representation of the tuple type."""
        elements = ", ".join(type_.__class__.__name__ for type_ in self.element_types)
        return f"tuple({elements})"

    def __repr__(self) -> str:
        """Get detailed string representation of the tuple type."""
        elements = ", ".join(repr(t) for t in self.element_types)
        return f"CtyTuple(element_types=({elements}))"

# 🐍🏗️🐣
