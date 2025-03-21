
# pyvider/cty/types/collections/list.py

from typing import Any, ClassVar, Generic, TypeVar, final, Sequence, Optional, Union, cast
from attrs import define, evolve, field
from pyvider.cty.exceptions import ValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.logger import logger

T = TypeVar('T')

@final
@define(frozen=True, slots=True)
class CtyList(CtyType[list[T]], Generic[T]):
    """
    CtyList represents a list type in the Cty type system.

    Lists are ordered collections of values of a specific element type.
    Unlike sets, lists can contain duplicate values and maintain order.
    """
    ctype: ClassVar[str] = "list"
    element_type: CtyType[T] = field(kw_only=True)  # Mandatory as keyword-only
    value: list[T] = field(factory=list, kw_only=True)  # Allow passing value via kw_only

    def __attrs_post_init__(self) -> None:
        """Validate element_type after initialization."""
        if not isinstance(self.element_type, CtyType):
            logger.error(f"🔌❗❌ Expected CtyType for element_type, got {type(self.element_type)}")
            raise ValidationError(
                f"Expected CtyType for element_type, got {type(self.element_type)}"
            )

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

        # Handle None value - no fallback, just raise an error
        if value is None:
            logger.error("🔌❗❌ Cannot validate None as a list")
            raise ValidationError("Cannot validate None as a list")

        # Validate the input is an iterable
        if not hasattr(value, '__iter__') or isinstance(value, (str, bytes, dict)):
            logger.error(f"🔌❗❌ Expected iterable, got {type(value).__name__}")
            raise ValidationError(f"Expected iterable, got {type(value).__name__}")

        # Handle empty iterable
        if not value:
            logger.debug("🔌📝✅ Returning empty list for empty iterable")
            return evolve(self, value=[])

        # Validate each element
        validated = []
        validation_errors = []

        for i, item in enumerate(value):
            try:
                # Validate each element against the element_type
                validated_item = self.element_type.validate(item)
                validated.append(validated_item)
                logger.debug(f"🔌📝✅ Validated item {i}: {validated_item}")
            except Exception as e:
                error_msg = f"Item {i}: {item} -> {e!s}"
                logger.error(f"🔌❗❌ {error_msg}")
                validation_errors.append(error_msg)

        # If any validation errors, raise them
        if validation_errors:
            error_msg = "CtyList validation failed:\n" + "\n".join(validation_errors)
            logger.error(f"🔌❗❌ {error_msg}")
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
            ValidationError: If the container is not a list or CtyList
            IndexError: If the index is out of bounds
        """
        logger.debug(f"🔌🔍🔄 Getting element at index {index}")

        # Handle CtyList container
        if isinstance(container, CtyList):
            container_value = container.value
        # Handle raw list container
        elif isinstance(container, (list, tuple)):
            container_value = container
        # Handle invalid container type
        else:
            logger.error(f"🔌❗❌ Expected list or CtyList, got {type(container).__name__}")
            raise ValidationError(f"Expected list or CtyList, got {type(container).__name__}")

        # Get the element at the specified index
        try:
            result = container_value[index]
            logger.debug(f"🔌🔍✅ Got element at index {index}")
            return result
        except IndexError as e:
            logger.error(f"🔌❗❌ Index out of bounds: {index}")
            raise IndexError(f"Index out of bounds: {index}") from e

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
            # Validate the item
            validated_item = self.element_type.validate(item)

            # Create a new list with the additional item
            new_list = list(self.value)
            new_list.append(validated_item)

            logger.debug(f"🔌📝✅ Appended item: {validated_item}")
            return evolve(self, value=new_list)
        except Exception as e:
            logger.error(f"🔌❗❌ Failed to append item: {e}")
            raise ValidationError(f"Failed to append item: {e}")

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

        # Validate indices
        if start < 0:
            start = len(self.value) + start
        if end < 0:
            end = len(self.value) + end

        if start < 0 or start > len(self.value):
            logger.error(f"🔌❗❌ Start index {start} out of bounds (0-{len(self.value)})")
            raise IndexError(f"Start index {start} out of bounds (0-{len(self.value)})")
        if end < start or end > len(self.value):
            logger.error(f"🔌❗❌ End index {end} out of bounds ({start}-{len(self.value)})")
            raise IndexError(f"End index {end} out of bounds ({start}-{len(self.value)})")

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
            logger.error(f"🔌❗❌ Expected CtyList, got {type(other).__name__}")
            raise ValidationError(f"Expected CtyList, got {type(other).__name__}")

        # Ensure element types are compatible
        if not self.element_type.equal(other.element_type):
            logger.error(f"🔌❗❌ Element types are not compatible: {self.element_type} and {other.element_type}")
            raise ValidationError(
                f"Cannot concatenate lists with different element types: {self.element_type} and {other.element_type}"
            )

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
            # Validate the item
            validated_item = self.element_type.validate(item)

            # Check if the validated item is in the list
            for list_item in self.value:
                if list_item == validated_item:
                    logger.debug(f"🔌🔍✅ List contains item: {validated_item}")
                    return True

            logger.debug(f"🔌🔍❌ List does not contain item: {validated_item}")
            return False
        except Exception as e:
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
        Check if this list is equal to another object.

        Args:
            other: The other object to check against

        Returns:
            True if the lists are equal
        """
        # Only equal to other CtyList instances
        if not isinstance(other, CtyList):
            return False

        # Check element type and values
        return (
            self.element_type == other.element_type
            and len(self.value) == len(other.value)
            and all(a == b for a, b in zip(self.value, other.value))
        )

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
        return f"list({self.element_type})"

    def __repr__(self) -> str:
        """
        Get a detailed string representation of this list.

        Returns:
            A detailed string representation
        """
        return f"CtyList(element_type={self.element_type})"