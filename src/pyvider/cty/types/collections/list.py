#
# pyvider/cty/types/collections/list.py
#

from typing import Any, ClassVar, Generic, List as PyList, TypeVar, final, Sequence, Optional, Union, cast
from attrs import define, evolve, field
from pyvider.cty.exceptions import ValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.logger import logger

# Type variable representing the type of values in the list
T = TypeVar('T')

@final
@define(frozen=True, slots=True)
class CtyList(CtyType[PyList[T]], Generic[T]):
    """
    CtyList represents a list type in the Cty type system.

    Lists are ordered collections of values of a specific element type.
    Unlike sets, lists can contain duplicate values and maintain order.

    Attributes:
        element_type: The Cty type of elements in the list
        value: The actual list of values (all of which are of type T)
    """
    ctype: ClassVar[str] = "list"
    element_type: CtyType[T] = field(kw_only=True)  # Mandatory as keyword-only
    value: PyList[T] = field(factory=list, kw_only=True)  # Allow passing value via kw_only

    def __attrs_post_init__(self) -> None:
        """
        Validate element_type after initialization.

        Raises:
            ValidationError: If element_type is not a CtyType
        """
        if not isinstance(self.element_type, CtyType):
            message = f"Expected CtyType for element_type, got {type(self.element_type).__name__}"
            logger.error(f"🔌❗❌ {message}")
            raise ValidationError(message)

    def validate(self, value: Any) -> "CtyList[T]":
        """
        Validate that the given value conforms to this list type.

        Args:
            value: The value to validate

        Returns:
            A new CtyList with the validated value

        Raises:
            ValidationError: If validation fails
        """
        logger.debug(f"🔌📝🔄 Validating value as CtyList: {type(value).__name__}")

        # For go-cty compatibility, we need to raise ValidationError for None values
        if value is None:
            logger.debug("🔌❗❌ Cannot validate None as a list")
            raise ValidationError("Expected list or tuple, got NoneType")

        if not isinstance(value, (list, tuple)):
            logger.debug(f"🔌❗❌ Expected list or tuple, got {type(value).__name__}")
            raise ValidationError(f"Expected list or tuple, got {type(value).__name__}")

        if not value:
            logger.debug("🔌📝✅ Returning empty list for empty list/tuple")
            return evolve(self, value=[])

        validated = []
        validation_errors = []

        for i, item in enumerate(value):
            try:
                # Check if item is already a CtyType instance of the expected type
                if isinstance(item, CtyType) and item.__class__ == self.element_type.__class__:
                    validated_item = item
                    logger.debug(f"🔌📝✅ Item {i} is already a {self.element_type.__class__.__name__}, no validation needed")
                else:
                    validated_item = self.element_type.validate(item)

                validated.append(validated_item)
                logger.debug(f"🔌📝✅ Validated item {i}: {validated_item}")
            except Exception as e:
                error_msg = f"Item {i}: {item} -> {e!s}"
                logger.debug(f"🔌❗❌ {error_msg}")
                validation_errors.append(error_msg)

        if validation_errors:
            error_msg = "CtyList validation failed:\n" + "\n".join(validation_errors)
            logger.debug(f"🔌❗❌ {error_msg}")
            raise ValidationError(error_msg)

        logger.debug(f"🔌📝✅ Successfully validated list with {len(validated)} items")
        return evolve(self, value=validated)

    def element_at(self, container: Any, index: int) -> T:
        """
        Get an element at a specific index in the list.

        Args:
            container: The list or CtyList to get the element from
            index: The index to get the element at

        Returns:
            The element at the specified index

        Raises:
            ValidationError: If the container is not a list, tuple, or CtyList
            IndexError: If the index is out of bounds
        """
        logger.debug(f"🔌🔍🔄 Getting element at index {index}")

        # Handle CtyList container
        if isinstance(container, CtyList):
            container_value = container.value
        # Handle raw list or tuple container
        elif isinstance(container, (list, tuple)):
            container_value = container
        # Handle invalid container type
        else:
            message = f"Expected list, tuple, or CtyList, got {type(container).__name__}"
            logger.error(f"🔌❗❌ {message}")
            raise ValidationError(message)

        # Get the element at the specified index
        try:
            result = container_value[index]
            logger.debug(f"🔌🔍✅ Got element at index {index}: {result}")
            return result
        except IndexError as e:
            message = f"Index out of bounds: {index} (valid range: 0-{len(container_value)-1})"
            logger.error(f"🔌❗❌ {message}")
            raise IndexError(message) from e

    def append(self, item: Any) -> "CtyList[T]":
        """
        Append an item to the list.

        Args:
            item: The item to append

        Returns:
            A new CtyList with the item appended

        Raises:
            ValidationError: If the item cannot be validated
        """
        logger.debug(f"🔌📝🔄 Appending item: {item}")

        try:
            # Validate the item against element_type
            if isinstance(item, CtyType) and item.__class__ == self.element_type.__class__:
                validated_item = item
                logger.debug(f"🔌📝✅ Item is already a {self.element_type.__class__.__name__}, no validation needed")
            else:
                validated_item = self.element_type.validate(item)

            # Create a new list with the additional item
            new_list = list(self.value)
            new_list.append(validated_item)

            logger.debug(f"🔌📝✅ Appended item: {validated_item}")
            return evolve(self, value=new_list)
        except Exception as e:
            message = f"Failed to append item: {e}"
            logger.error(f"🔌❗❌ {message}")
            raise ValidationError(message)

    def slice(self, start: int, end: Optional[int] = None) -> "CtyList[T]":
        """
        Get a slice of this list.

        Args:
            start: The start index (inclusive)
            end: The end index (exclusive), or None for end of list

        Returns:
            A new CtyList with the sliced values

        Raises:
            IndexError: If the indices are out of bounds
        """
        logger.debug(f"🔌🔍🔄 Slicing list from {start} to {end}")

        if end is None:
            end = len(self.value)

        # Convert negative indices to positive
        if start < 0:
            start = len(self.value) + start
        if end < 0:
            end = len(self.value) + end

        # Validate indices are within bounds
        if start < 0 or start > len(self.value):
            message = f"Start index {start} out of bounds (0-{len(self.value)})"
            logger.error(f"🔌❗❌ {message}")
            raise IndexError(message)

        if end < start or end > len(self.value):
            message = f"End index {end} out of bounds ({start}-{len(self.value)})"
            logger.error(f"🔌❗❌ {message}")
            raise IndexError(message)

        # Create a new list with the sliced values
        sliced_value = self.value[start:end]
        logger.debug(f"🔌🔍✅ Sliced list from {start} to {end}, result size: {len(sliced_value)}")
        return evolve(self, value=sliced_value)

    def concat(self, other: "CtyList[T]") -> "CtyList[T]":
        """
        Concatenate this list with another list.

        Args:
            other: The other list to concatenate with

        Returns:
            A new CtyList with the concatenated values

        Raises:
            ValidationError: If the other list has a different element type
        """
        logger.debug(f"🔌📝🔄 Concatenating with another list")

        # Ensure other is a CtyList
        if not isinstance(other, CtyList):
            message = f"Expected CtyList, got {type(other).__name__}"
            logger.error(f"🔌❗❌ {message}")
            raise ValidationError(message)

        # Ensure element types are compatible
        if not self.element_type.equal(other.element_type):
            message = f"Cannot concatenate lists with different element types: {self.element_type} and {other.element_type}"
            logger.error(f"🔌❗❌ {message}")
            raise ValidationError(message)

        # Create a new list with the concatenated values
        concat_value = list(self.value) + list(other.value)
        logger.debug(f"🔌📝✅ Concatenated lists, result size: {len(concat_value)}")
        return evolve(self, value=concat_value)

    def contains(self, item: Any) -> bool:
        """
        Check if this list contains an item.

        Args:
            item: The item to check for

        Returns:
            True if the item is in the list, False otherwise
        """
        logger.debug(f"🔌🔍🔄 Checking if list contains item: {item}")

        try:
            # Validate the item against element_type
            if isinstance(item, CtyType) and item.__class__ == self.element_type.__class__:
                validated_item = item
                logger.debug(f"🔌🔍✅ Item is already a {self.element_type.__class__.__name__}, no validation needed")
            else:
                validated_item = self.element_type.validate(item)

            # Check if any element in the list equals the validated item
            for list_item in self.value:
                if list_item == validated_item:
                    logger.debug(f"🔌🔍✅ List contains item: {validated_item}")
                    return True

            logger.debug(f"🔌🔍❌ List does not contain item: {validated_item}")
            return False
        except Exception as e:
            # If validation fails, the item can't be in the list
            logger.debug(f"🔌🔍❌ Item is not valid for this list: {e}")
            return False

    def usable_as(self, other: "CtyType") -> bool:
        """
        Check if this type can be used as the other type.

        Args:
            other: The other type to check against

        Returns:
            True if this type can be used as the other type
        """
        if not isinstance(other, CtyList):
            logger.debug(f"🔌📝❌ CtyList.usable_as: False (other is {type(other).__name__})")
            return False

        result = self.element_type.usable_as(other.element_type)
        logger.debug(f"🔌📝✅ CtyList.usable_as: {result}")
        return result

    def equal(self, other: "CtyType") -> bool:
        """
        Check if this type is equal to the other type.

        Args:
            other: The other type to check against

        Returns:
            True if the types are equal
        """
        if not isinstance(other, CtyList):
            logger.debug(f"🔌📝❌ CtyList.equal: False (other is {type(other).__name__})")
            return False

        result = self.element_type.equal(other.element_type)
        logger.debug(f"🔌📝✅ CtyList.equal: {result}")
        return result

    def __eq__(self, other):
        """
        Check if this list is equal to another list.

        Args:
            other: The other list to check against

        Returns:
            True if the lists are equal
        """
        if not isinstance(other, CtyList):
            return False

        # Check element type equality
        if not self.element_type == other.element_type:
            return False

        # Check if lists have the same length
        if len(self.value) != len(other.value):
            return False

        # Check each element for equality
        for a, b in zip(self.value, other.value):
            if a != b:
                return False

        return True

    def __len__(self):
        """
        Get the length of this list.

        Returns:
            The number of elements in the list
        """
        return len(self.value)

    def __iter__(self):
        """
        Iterate over the list values.

        Returns:
            An iterator over the list values
        """
        return iter(self.value)

    def __getitem__(self, index: Union[int, slice]):
        """
        Get an item from the list by index or slice.

        Args:
            index: The index or slice to get

        Returns:
            The item at the specified index, or a new CtyList with the sliced values
        """
        if isinstance(index, slice):
            sliced_value = self.value[index]
            return evolve(self, value=sliced_value)
        return self.value[index]

    def __str__(self) -> str:
        """
        Get a string representation of this list type.

        Returns:
            A string representation
        """
        # Handle nested lists properly
        element_class = self.element_type.__class__.__name__
        if element_class == "CtyList":
            # For nested lists, include the inner element type
            return f"list({str(self.element_type)})"
        return f"list({element_class})"

    def __repr__(self) -> str:
        """
        Get a detailed string representation of this list.

        Returns:
            A detailed string representation
        """
        return f"CtyList(element_type={self.element_type!r})"

# 🐍🏗️
