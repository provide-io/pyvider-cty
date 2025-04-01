#
# pyvider/cty/types/collections/list.py
#

from typing import Any, ClassVar, Generic, TypeVar, final, Sequence, Optional, Union, cast
from attrs import define, evolve, field
from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.logger import logger

# Type variable representing the type of values in the list
T = TypeVar('T')

@final
@define(frozen=True, slots=True)
class CtyList(CtyType[list[T]], Generic[T]):
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
    value: list[T] = field(factory=list, kw_only=True)  # Allow passing value via kw_only

    def __attrs_post_init__(self) -> None:
        """
        Validate element_type after initialization.

        Raises:
            CtyListValidationError: If element_type is not a CtyType
        """
        if not isinstance(self.element_type, CtyType):
            message = f"Expected CtyType for element_type, got {type(self.element_type).__name__}"
            logger.error(f"🔌❗❌ {message}")
            raise CtyListValidationError(message)

    #### validate
    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value conforms to this list type.

        Args:
            value: The value to validate

        Returns:
            A CtyValue with the validated list
        """
        logger.debug(f"🔌📝🔄 Validating value as CtyList: {type(value).__name__}")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        # Handle None
        if value is None:
            logger.debug("🔌📝✅ None value - creating empty list")
            return CtyValue(type_=self, value=[])

        # Ensure input is iterable
        if not isinstance(value, (list, tuple)):
            logger.debug(f"🔌❗❌ Expected list or tuple, got {type(value).__name__}")
            raise CtyListValidationError(f"Expected list or tuple, got {type(value).__name__}")

        # Handle empty list
        if not value:
            logger.debug("🔌📝✅ Empty list - creating empty CtyList")
            return CtyValue(type_=self, value=[])

        # Validate each element
        validated_list = []
        validation_errors = []

        for i, item in enumerate(value):
            try:
                # Already a CtyValue of correct type?
                if isinstance(item, CtyValue) and isinstance(item.type, self.element_type.__class__):
                    validated_item = item
                    logger.debug(f"🔌📝✅ Item {i} is already a CtyValue: {item}")
                else:
                    # Validate and wrap
                    validated = self.element_type.validate(item)
                    if isinstance(validated, CtyValue):
                        validated_item = validated
                    else:
                        validated_item = CtyValue(type_=self.element_type, value=validated)
                    logger.debug(f"🔌📝✅ Validated item {i}: {item} -> {validated_item}")

                validated_list.append(validated_item)
            except Exception as e:
                error_msg = f"Item {i}: {item} -> {e!s}"
                logger.debug(f"🔌❗❌ {error_msg}")
                validation_errors.append(error_msg)

        if validation_errors:
            error_msg = "CtyList validation failed:\n" + "\n".join(validation_errors)
            logger.debug(f"🔌❗❌ {error_msg}")
            raise CtyListValidationError(error_msg)

        logger.debug(f"🔌📝✅ Successfully validated list with {len(validated_list)} items")
        return CtyValue(type_=self, value=validated_list)

    #### element_at
    def element_at(self, container: Any, index: int) -> "CtyValue":
        """
        Get an element at a specific index in the list.

        Args:
            container: The list, tuple, or CtyValue containing a list
            index: The index to get the element at

        Returns:
            The element at the specified index
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
        elif isinstance(container, (list, tuple)):
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

    #### append
    def append(self, item: Any) -> "CtyList[T]":
        """
        Append an item to the list.

        Args:
            item: The item to append

        Returns:
            A new CtyList with the item appended

        Raises:
            CtyListValidationError: If the item cannot be validated
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
            raise CtyListValidationError(message)

    #### slice
    def slice(self, start: int, end: Optional[int] = None) -> "CtyList[T]":
        """
        Get a slice of this list.

        Args:
            start: The start index (inclusive)
            end: The end index (exclusive), or None for end of list

        Returns:
            A new CtyList with the sliced values
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

        # Clamp indices to valid ranges - this fixes the extreme indices issue
        start = max(0, min(start, list_length))
        end = max(start, min(end, list_length))

        # Create a new list with the sliced values
        sliced_value = self.value[start:end]
        logger.debug(f"🔌🔍✅ Sliced list from {start} to {end}, result size: {len(sliced_value)}")
        return evolve(self, value=sliced_value)

    #### concat
    def concat(self, other: "CtyList[T]") -> "CtyList[T]":
        """
        Concatenate this list with another list.

        Args:
            other: The other list to concatenate with

        Returns:
            A new CtyList with the concatenated values

        Raises:
            CtyListValidationError: If the other list has a different element type
        """
        logger.debug(f"🔌📝🔄 Concatenating with another list")

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

    #### contains
    def contains(self, item: Any) -> bool:
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

    #### usable_as
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

    #### equal
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
        if not isinstance(other, CtyList):
            return False

        # Check element type equality
        if not self.element_type.equal(other.element_type):
            return False

        # Check list length
        if len(self.value) != len(other.value):
            return False

        # Compare values, not just references
        for a, b in zip(self.value, other.value):
            if hasattr(a, 'value') and hasattr(b, 'value'):
                if a.value != b.value:
                    return False
            elif a != b:
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

# 🐍🏗️🐣
