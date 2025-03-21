
# pyvider/cty/types/collections/list.py

from typing import Any, ClassVar, Generic, TypeVar, final, Sequence, Optional, Union
from attrs import define, evolve, field
from pyvider.cty.exceptions import ValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.logger import logger

T = TypeVar('T', bound=CtyType)

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
        """
        # [validation logic]
        
        # Instead of storing CtyType objects in the list
        # Store the actual validated values
        validated = []
        for item in value:
            # Get the validated value, not the CtyType object
            validated_value = self.element_type.validate(item)
            validated.append(validated_value)

        return evolve(self, value=validated)


    def Xvalidate(self, value: Any) -> "CtyList[T]":
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

        if value is None:
            logger.debug("🔌📝✅ Returning empty list for None value")
            return evolve(self, value=[])

        if not hasattr(value, '__iter__') or isinstance(value, (str, bytes, dict)):
            logger.debug(f"🔌❗❌ Expected iterable, got {type(value).__name__}")
            raise ValidationError(f"Expected iterable, got {type(value).__name__}")

        if not value:
            logger.debug("🔌📝✅ Returning empty list for empty iterable")
            return evolve(self, value=[])

        validated = []
        validation_errors = []

        for i, item in enumerate(value):
            try:
                # If element_type is a CtyType, use its validate method
                if isinstance(self.element_type, CtyType):
                    validated_item = self.element_type.validate(item)
                    validated.append(validated_item)
                    logger.debug(f"🔌📝✅ Validated item {i}: {validated_item}")
                else:
                    # This should never happen due to __attrs_post_init__, but just in case
                    raise ValidationError(f"Element type is not a CtyType: {self.element_type}")
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

    def element_at(self, container: Sequence[T], index: int) -> T:
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
        # If container is a CtyList, get its value
        actual_container = getattr(container, 'value', container) if isinstance(container, CtyList) else container

        if not isinstance(actual_container, (list, tuple)):
            logger.debug(f"🔌❗❌ Expected list or CtyList, got {type(container).__name__}")
            raise ValidationError(f"Expected list or CtyList, got {type(container).__name__}")

        try:
            result = actual_container[index]
            logger.debug(f"🔌📝✅ Got element at index {index}: {result}")
            return result
        except IndexError as e:
            logger.debug(f"🔌❗❌ Index out of bounds: {index}")
            raise IndexError(f"Index out of bounds: {index}") from e

    def append(self, item: T) -> "CtyList[T]":
        """
        Append an item to the list.

        Args:
            item: The item to append

        Returns:
            A new CtyList with the item appended

        Raises:
            ValidationError: If the item cannot be validated
        """
        try:
            validated_item = self.element_type.validate(item)
            new_list = list(self.value)
            new_list.append(validated_item)
            logger.debug(f"🔌📝✅ Appended item to list: {validated_item}")
            return evolve(self, value=new_list)
        except Exception as e:
            logger.debug(f"🔌❗❌ Failed to append item: {e}")
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
        if end is None:
            end = len(self.value)

        # Validate indices
        if start < 0:
            start = len(self.value) + start
        if end < 0:
            end = len(self.value) + end

        if start < 0 or start > len(self.value):
            raise IndexError(f"Start index {start} out of bounds (0-{len(self.value)})")
        if end < start or end > len(self.value):
            raise IndexError(f"End index {end} out of bounds ({start}-{len(self.value)})")

        # Create new list with sliced values
        sliced_value = self.value[start:end]
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
        if not isinstance(other, CtyList):
            raise ValidationError(f"Expected CtyList, got {type(other).__name__}")

        if not self.element_type.equal(other.element_type):
            raise ValidationError(
                f"Cannot concatenate lists with different element types: {self.element_type} and {other.element_type}"
            )

        # Create new list with concatenated values
        concat_value = list(self.value) + list(other.value)
        return evolve(self, value=concat_value)

    def contains(self, item: Any) -> bool:
        """
        Check if this list contains an item.

        Args:
            item: The item to check for

        Returns:
            True if the item is in the list, False otherwise
        """
        # Try to validate the item first
        try:
            validated_item = self.element_type.validate(item)
        except Exception:
            # If validation fails, the item can't be in the list
            return False

        # Check if the validated item is in the list
        return validated_item in self.value

    def usable_as(self, other: "CtyType") -> bool:
        """
        Check if this type can be used as the other type.

        Args:
            other: The other type to check against

        Returns:
            True if this type can be used as the other type
        """
        result = isinstance(other, CtyList) and self.element_type.usable_as(other.element_type)
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
        return (
            self.element_type == other.element_type
            and self.value == other.value
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

    def __getitem__(self, index):
        """Get an item from the list by index."""
        if isinstance(index, slice):
            sliced_value = self.value[index]
            return evolve(self, value=sliced_value)
        return self.value[index]  # Return the actual value, not a wrapped type

    def X__getitem__(self, index: Union[int, slice]):
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
