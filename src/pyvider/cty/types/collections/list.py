#
# pyvider/cty/types/collections/list.py
#

"""
List type implementation for the Cty type system.

This module provides CtyList, representing ordered collections of elements with the
same type in the Cty type system. Lists maintain insertion order, allow duplicates,
and support indexed access, slicing, and other sequence operations.

CtyList follows the go-cty list semantics, ensuring type safety for all elements
while providing Pythonic operations like slicing and iteration. All operations maintain
immutability by returning new instances rather than modifying existing ones.
"""

from collections.abc import Sequence
from typing import Any, ClassVar, Generic, TypeVar, Union, final

from attrs import define, evolve, field

from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty.types.base import CtyType
from pyvider.telemetry import logger

# Type variable representing the type of values in the list
T = TypeVar('T')

@final
@define(frozen=True, slots=True)
class CtyList(CtyType[list[T]], Generic[T]):
    """
    Represents an ordered list type in the Cty type system.

    Lists are ordered collections of values of a specific element type.
    Unlike sets, lists can contain duplicate values and maintain insertion order.
    CtyList supports indexing, slicing, concatenation, and other sequence operations
    while ensuring all elements conform to the specified element type.

    All operations maintain immutability by returning new instances rather than
    modifying existing ones.

    Attributes:
        ctype (ClassVar[str]): Type identifier constant, always "list"
        element_type (CtyType[T]): The type of elements contained in the list
        value (list[T]): The actual list of values (all of which are of type T)

    Examples:
        Creating a list of strings:
        >>> string_type = CtyString()
        >>> string_list = CtyList(element_type=string_type)

        Validating a list of values:
        >>> validated = string_list.validate(["a", "b", "c"])
        >>> len(validated)
        3
    """
    ctype: ClassVar[str] = "list"
    element_type: CtyType[T] = field(kw_only=True)  # Mandatory as keyword-only
    value: list[T] = field(factory=list, kw_only=True)  # Allow passing value via kw_only

    def __attrs_post_init__(self) -> None:
        """
        Validate element_type after initialization.

        Ensures that element_type is a valid CtyType instance, providing early
        validation of list type definitions.

        Raises:
            CtyListValidationError: If element_type is not a CtyType
        """
        if not isinstance(self.element_type, CtyType):
            message = f"Expected CtyType for element_type, got {type(self.element_type).__name__}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value conforms to this list type.

        Performs comprehensive validation of the input value against this list type.
        Accepts lists and tuples as inputs, validates each element against the
        element_type, and returns a properly typed CtyValue with validated elements.

        Empty lists and None are converted to empty lists. Invalid inputs or
        elements that don't match the element_type raise validation errors.

        Args:
            value: The value to validate, typically a list, tuple, or None

        Returns:
            CtyValue: A CtyValue instance wrapping the validated list

        Raises:
            CtyListValidationError: If value is not a list/tuple or contains
                elements that don't conform to element_type
        """
        logger.debug(f"🔌📝🔄 Validating value as CtyList: {type(value).__name__}")

        # Import locally to avoid circular imports
        from pyvider.cty.types import CtyDynamic  # For CtyDynamic check
        from pyvider.cty.values import CtyValue

        # Handle None
        if value is None:
            # Consistent with other types, None input to validate usually means "null value of this type"
            # or an error if the type cannot be null. For collections, usually means empty or null.
            # However, the original code raised error for None. Let's stick to that for now or make it return null list.
            # For now, let's assume None means "I want a null list" if that's a concept, or error.
            # The previous code raised: CtyListValidationError(f"Expected list or tuple, got NoneType")
            # Let's make it more specific if None is truly disallowed.
            # Based on how CtyValue.list handles None, it results in a null list value.
            # CtyList().validate(None) should probably align or be clearly defined.
            # For now, keeping original behavior of raising error if None is passed directly to validate.
            logger.error("🔌❗❌ CtyList.validate received None as input.")
            raise CtyListValidationError("Input to CtyList.validate cannot be None. Use CtyValue.null(CtyList(...)) for a null list.")

        raw_list_to_validate: Sequence[Any] | None = None
        if isinstance(value, CtyValue):
            if value.is_null: # If we get a null CtyValue, it's a null list of this type.
                 logger.debug("🔌📝✅ Input is a null CtyValue, resulting in a null list of this type.")
                 return CtyValue.null(self)
            if value.is_unknown: # If we get an unknown CtyValue, it's an unknown list of this type.
                 logger.debug("🔌📝✅ Input is an unknown CtyValue, resulting in an unknown list of this type.")
                 return CtyValue.unknown(self)

            if isinstance(value.type, CtyList):
                # Check element type compatibility
                # Allow if target element type is dynamic, or source can be used as target.
                if isinstance(self.element_type, CtyDynamic) or \
                   value.type.element_type.usable_as(self.element_type):
                    logger.debug(f"🔌📝🔄 Input CtyValue has compatible list type {value.type}. Validating its elements.")
                    raw_list_to_validate = value.value # .value of a CtyValue(CtyList) is list of CtyValues
                else:
                    raise CtyListValidationError(
                        f"Input CtyValue has incompatible list element type: {value.type.element_type} vs {self.element_type}"
                    )
            else:
                raise CtyListValidationError(
                    f"Input CtyValue is not of a list type, got {value.type}"
                )
        elif isinstance(value, list | tuple):
            raw_list_to_validate = value
        else:
            logger.debug(f"🔌❗❌ Expected list, tuple, or CtyValue list, got {type(value).__name__}")
            raise CtyListValidationError(f"Expected list, tuple, or CtyValue list, got {type(value).__name__}")

        if raw_list_to_validate is None: # Should be theoretically unreachable due to prior checks
             logger.error("🔌❗❌ Internal error: list_to_validate is None after initial checks.")
             raise CtyListValidationError("Internal error: list to validate is None after initial checks.")

        if not raw_list_to_validate:
            logger.debug("🔌📝✅ Empty list - creating empty CtyList")
            return CtyValue(vtype=self, value=[])

        validated_elements = []
        validation_errors = []

        for i, item in enumerate(raw_list_to_validate):
            try:
                # If the item itself is a CtyValue (e.g. from a CtyValue(CtyList) input),
                # we need to validate its underlying value against self.element_type.
                # If item is a raw Python value, validate it directly.

                # Special case: if self.element_type is CtyDynamic and item is already a CtyValue,
                # we can accept it as is, as CtyDynamic can hold any CtyValue.
                if isinstance(self.element_type, CtyDynamic) and isinstance(item, CtyValue):
                    validated_item = item  # Pass through if list is dynamic and item is already CtyValue
                else:
                    value_to_validate = item.value if isinstance(item, CtyValue) else item
                    validated_item = self.element_type.validate(value_to_validate)

                logger.debug(f"🔌📝✅ Validated item {i}: {item} -> {validated_item}")
                validated_elements.append(validated_item)
            except Exception as e:
                error_msg = f"Item {i} ('{item}'): {e!s}" # Make sure item is representable
                logger.debug(f"🔌❗❌ {error_msg}")
                validation_errors.append(error_msg)

        if validation_errors:
            error_msg = "CtyList validation failed:\n - " + "\n - ".join(validation_errors) # Added hyphen for clarity
            logger.error(f"🔌❗❌ {error_msg}") # Changed from debug to error
            raise CtyListValidationError(error_msg)

        logger.debug(f"🔌📝✅ Successfully validated list with {len(validated_elements)} items")
        return CtyValue(vtype=self, value=validated_elements)

    def element_at(self, container: Any, index: int) -> "CtyValue":
        """
        Get an element at a specific index in the list.

        Retrieves a single element from the container at the specified index.
        Supports negative indices for accessing elements from the end of the list.

        This method can operate on CtyValue containers, CtyList instances, or raw
        lists/tuples containing CtyValue elements.

        Args:
            container: The list, tuple, or CtyValue containing a list
            index: The index to get the element at (supports negative indices)

        Returns:
            CtyValue: The element at the specified index

        Raises:
            CtyListValidationError: If container is not a valid list container
            IndexError: If the index is out of bounds
        """
        logger.debug(f"🔌🔍🔄 Getting element at index {index}")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        # Handle CtyValue container
        if isinstance(container, CtyValue):
            if not isinstance(container.type, CtyList):
                message = f"Expected CtyValue with CtyList type, got CtyValue with {type(container.type).__name__}"
                logger.error(f"🔌❗❌ {message}")
                raise CtyListValidationError(message)
            return container.element_at(index)

        # Handle CtyList container directly
        elif isinstance(container, CtyList):
            container_value = container.value
        # Handle raw list or tuple container
        elif isinstance(container, list | tuple):
            container_value = container
        # Handle invalid container type
        else:
            message = f"Expected list, tuple, CtyList, or CtyValue with CtyList type, got {type(container).__name__}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)

        # Get the element at the specified index
        try:
            # Handle negative indices
            list_len = len(container_value)
            if index < 0:
                index = list_len + index

            # Check bounds
            if index < 0 or index >= list_len:
                raise IndexError(f"Index {index} out of bounds (0-{list_len-1})")

            # Return the element at the specified index
            result = container_value[index]
            logger.debug(f"🔌🔍✅ Got element at index {index}: {result}")
            return result
        except IndexError as e:
            message = f"Index out of bounds: {index}"
            logger.error(f"🔌❗❌ {message}")
            raise IndexError(message) from e

    def append(self, item: Any) -> "CtyList[T]":
        """
        Append an item to the list, returning a new list.

        Creates a new list with all existing elements plus the new item.
        This is an immutable operation that preserves the original list.
        The item is validated against the element_type before being added.

        Args:
            item: The item to append (will be validated against element_type)

        Returns:
            CtyList[T]: A new CtyList instance with the item appended

        Raises:
            CtyListValidationError: If the item cannot be validated against element_type
        """
        logger.debug(f"🔌📝🔄 Appending item: {item}")

        try:
            # Validate the item against element_type
            validated_item = self.element_type.validate(item)

            # Create a new list with the additional item
            new_list = list(self.value)
            new_list.append(validated_item)

            logger.debug(f"🔌📝✅ Appended item: {validated_item}")
            return evolve(self, value=new_list)
        except Exception as e:
            message = f"Failed to append item: {e}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)

    def slice(self, start: int, end: int | None = None) -> "CtyList[T]":
        """
        Get a slice of this list, returning a new list.

        Creates a new list containing a range of elements from the original list.
        This is an immutable operation that preserves the original list.
        Supports negative indices and handles index clamping to valid ranges.

        Args:
            start: The start index (inclusive)
            end: The end index (exclusive), or None for end of list

        Returns:
            CtyList[T]: A new CtyList instance with the sliced values
        """
        logger.debug(f"🔌🔍🔄 Slicing list from {start} to {end}")

        list_length = len(self.value)
        if end is None:
            end = list_length

        # Convert negative indices to positive
        if start < 0:
            start = list_length + start
        if end < 0:
            end = list_length + end

        # Clamp indices to valid ranges
        start = max(0, min(start, list_length))
        end = max(start, min(end, list_length))

        # Create a new list with the sliced values
        sliced_value = self.value[start:end]
        logger.debug(f"🔌🔍✅ Sliced list from {start} to {end}, result size: {len(sliced_value)}")

        return evolve(self, value=sliced_value)

    def concat(self, other: "CtyList[T]") -> "CtyList[T]":
        """
        Concatenate this list with another list, returning a new list.

        Creates a new list containing all elements from this list followed by
        all elements from the other list. This is an immutable operation that
        preserves both original lists. The other list must have a compatible
        element type.

        Args:
            other: The other list to concatenate with this one

        Returns:
            CtyList[T]: A new CtyList instance with concatenated values

        Raises:
            CtyListValidationError: If the other list has an incompatible element type
        """
        logger.debug("🔌📝🔄 Concatenating with another list")

        # Ensure other is a CtyList
        if not isinstance(other, CtyList):
            message = f"Expected CtyList, got {type(other).__name__}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)

        # Ensure element types are compatible
        if not self.element_type.equal(other.element_type):
            message = f"Cannot concatenate lists with different element types: {self.element_type} and {other.element_type}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)

        # Create a new list with the concatenated values
        concat_value = list(self.value) + list(other.value)
        logger.debug(f"🔌📝✅ Concatenated lists, result size: {len(concat_value)}")

        return evolve(self, value=concat_value)

    def contains(self, item: Any) -> bool:
        """
        Check if the list contains an item.

        Tests whether the given item matches any element in the list.
        Attempts to validate the item against the element_type before
        checking for membership, allowing for type conversion if possible.

        Returns False if validation fails (rather than raising an exception),
        making it safe to use in boolean expressions.

        Args:
            item: The item to check for (will be validated against element_type)

        Returns:
            bool: True if the validated item is found in the list, False otherwise
        """
        logger.debug(f"🔌🔍🔄 Checking if list contains item: {item}")

        try:
            # Validate the item
            validated_item = self.element_type.validate(item)

            # Check each element in the list
            for list_item in self.value:
                # Compare values within CtyValue objects
                if hasattr(list_item, 'value') and hasattr(validated_item, 'value'):
                    if list_item.value == validated_item.value:
                        logger.debug(f"🔌🔍✅ List contains item: {validated_item.value}")
                        return True

                # Try direct equality
                if list_item == validated_item:
                    logger.debug(f"🔌🔍✅ List contains item: {validated_item}")
                    return True

            return False
        except Exception as e:
            logger.debug(f"🔌🔍❌ Validation failed: {e}")
            return False

    def usable_as(self, other: CtyType) -> bool:
        """
        Check if this type can be used as the other type.

        Determines if values of this list type can be safely used in contexts
        expecting the other type. For lists, this requires the other type to
        be a list with an element type that our element type is usable as.

        Args:
            other: The other type to check against

        Returns:
            bool: True if this type can be used as the other type, False otherwise
        """
        if not isinstance(other, CtyList):
            logger.debug(f"🔌📝❌ CtyList.usable_as: False (other is {type(other).__name__})")
            return False

        result = self.element_type.usable_as(other.element_type)
        logger.debug(f"🔌📝✅ CtyList.usable_as: {result}")
        return result

    def equal(self, other: CtyType) -> bool:
        """
        Check if this type is equal to the other type.

        Determines if this list type is exactly equal to the other type.
        For lists, equality requires the other type to be a list with
        exactly the same element type.

        Args:
            other: The other type to check against

        Returns:
            bool: True if the types are equal, False otherwise
        """
        if not isinstance(other, CtyList):
            logger.debug(f"🔌📝❌ CtyList.equal: False (other is {type(other).__name__})")
            return False

        result = self.element_type.equal(other.element_type)
        logger.debug(f"🔌📝✅ CtyList.equal: {result}")
        return result

    def equal(self, other: "CtyType") -> bool:
        """
        Two list types are equal when the other type is also a CtyList
        and their element types are equal *recursively*.
        """

        logger.debug("📋🔍🔄 CtyList.equal: comparing %s to %s",
                     self, other)
        if not isinstance(other, CtyList):
            logger.debug("📋❌🔄  Other type is not CtyList → not equal")
            return False

        result = self.element_type.equal(other.element_type)
        logger.debug("📋🔍✅  Element‑type equality result: %s", result)
        return result

    def __len__(self) -> int:
        """
        Get the length of this list.

        Returns the number of elements in the list, enabling the use
        of the built-in len() function on CtyList instances.

        Returns:
            int: The number of elements in the list
        """
        return len(self.value)

    def __iter__(self):
        """
        Iterate over the list values.

        Enables iteration over the list elements using Python's
        iteration protocols, making CtyList instances iterable
        in for loops and other contexts.

        Returns:
            iterator: An iterator over the list values
        """
        return iter(self.value)

    def __getitem__(self, index: int | slice) -> Union["CtyValue", "CtyList"]:
        """
        Support for indexing and slicing operations.

        Enables both direct indexing (list[n]) and slicing (list[start:end:step])
        operations on CtyList instances, making them behave like native Python lists.

        For integer indices, returns the element at that position.
        For slices, returns a new CtyList containing the selected elements.

        Args:
            index: An integer index or slice object

        Returns:
            CtyValue: The element at the specified index (for integer indices)
            CtyList: A new CtyList with sliced elements (for slice objects)

        Raises:
            IndexError: If the index is out of range
        """
        if isinstance(index, slice):
            start = index.start if index.start is not None else 0
            stop = index.stop if index.stop is not None else len(self.value)
            if index.step is None or index.step == 1:
                return self.slice(start, stop)
            else:
                # Handle step parameter
                result = []
                for i in range(start, stop, index.step):
                    if i < len(self.value):
                        result.append(self.value[i])

                return evolve(self, value=result)

        try:
            return self.value[index]
        except IndexError:
            raise IndexError("list index out of range")

    def __str__(self) -> str:
        """
        Get a string representation of this list type.

        Provides a human-readable representation of the list type
        suitable for display and debugging.

        Returns:
            str: A string representation like "list(CtyString)"
        """
        # Handle nested lists properly
        element_class = self.element_type.__class__.__name__
        if element_class == "CtyList":
            # For nested lists, include the inner element type
            return f"list({self.element_type!s})"
        return f"list({element_class})"

    def __repr__(self) -> str:
        """
        Get a detailed string representation of this list.

        Provides a detailed representation of the list type
        suitable for debugging and introspection, including
        complete information about the element type.

        Returns:
            str: A detailed string representation
        """
        return f"CtyList(element_type={self.element_type!r})"

    def is_collection_type(self) -> bool:
        """Check if this type is a collection type."""
        return True

    def is_list_type(self) -> bool:
        """Check if this type is a list type."""
        return True

# 🐍🏗️🐣
