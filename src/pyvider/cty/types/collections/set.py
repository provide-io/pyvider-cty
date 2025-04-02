#
# pyvider/cty/types/collections/set.py
#

"""
Set type implementation for the Cty type system.

This module provides CtySet, representing unordered collections of unique values
in the Cty type system. Sets contain elements of a single specified type and
enforce uniqueness constraints during validation. The implementation follows
go-cty's set semantics, ensuring consistent behavior for collection operations
and maintaining type safety throughout the validation process.

Sets support standard operations like adding and removing elements, checking
for membership, and comparing with other sets, all while preserving type
information and maintaining immutability of the original values.
"""

from typing import Any, ClassVar, Generic, TypeVar, final
from typing import Set as PySet
from attrs import define, evolve, field
from pyvider.cty.exceptions import CtySetValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.logger import logger

T = TypeVar('T')

@final
@define(frozen=True, slots=True)
class CtySet(CtyType[PySet[T]], Generic[T]):
    """
    Represents a set type in the Cty type system.

    Sets are unordered collections of unique values of a specific element type.
    Unlike lists, sets cannot contain duplicate values and do not maintain any
    particular order. This implementation enforces type constraints during validation
    and provides immutable set operations.

    Attributes:
        ctype: Class variable identifying this as a set type, always "set"
        element_type: The Cty type of elements in the set
        value: The actual set of values, all of which are of type T
    """
    ctype: ClassVar[str] = "set"
    element_type: CtyType[T] = field(kw_only=True)  # Mandatory as keyword-only
    value: PySet[T] = field(factory=set, kw_only=True)  # Allow passing value via kw_only

    def __attrs_post_init__(self) -> None:
        """
        Validate element_type after initialization.

        Ensures that the element_type provided during instantiation is a valid
        CtyType instance. This validation occurs immediately after the object is
        created to catch configuration errors early.

        Raises:
            CtySetValidationError: If element_type is not a CtyType instance
        """
        if not isinstance(self.element_type, CtyType):
            raise CtySetValidationError(
                f"Expected CtyType for element_type, got {type(self.element_type)}"
            )

    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value conforms to this set type.

        Performs validation on the input to ensure it can be represented as a set
        with elements of the specified type. The validation process includes checking
        that the input is iterable, validating each element against the element_type,
        and constructing a new set with the validated elements.

        Args:
            value: The value to validate as a set. Can be any iterable except
                strings and bytes, which are treated as single values rather than
                collections of characters.

        Returns:
            CtyValue: A CtyValue instance containing the validated set

        Raises:
            CtySetValidationError: If value is None, not an iterable, contains nested sets,
                or contains elements that don't conform to the element_type
        """
        logger.debug(f"🔌📝🔄 Validating value as CtySet: {type(value).__name__}")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        if value is None:
            logger.debug("🔌❗❌ Expected iterable, got NoneType")
            raise CtySetValidationError(f"Expected iterable, got NoneType")

        if not hasattr(value, '__iter__') or isinstance(value, (str, bytes)):
            logger.debug(f"🔌❗❌ Expected iterable, got {type(value).__name__}")
            raise CtySetValidationError(f"Expected iterable, got {type(value).__name__}")

        if not value:
            logger.debug("🔌📝✅ Returning empty set for empty iterable")
            return CtyValue(type_=self, value=set())

        validated = set()
        validation_errors = []

        for i, item in enumerate(value):
            try:
                if isinstance(item, (set, frozenset)):
                    logger.debug("🔌❗❌ Nested sets are not allowed in CtySet")
                    raise CtySetValidationError("Nested sets are not allowed in CtySet.")

                # Validate the element
                validated_item = self.element_type.validate(item)

                # Add to the validated set
                validated.add(validated_item)
                logger.debug(f"🔌📝✅ Validated item {i}: {validated_item}")
            except Exception as e:
                error_msg = f"Item {i}: {item} -> {e!s}"
                logger.debug(f"🔌❗❌ {error_msg}")
                validation_errors.append(error_msg)

        if validation_errors:
            error_msg = "CtySet validation failed:\n" + "\n".join(validation_errors)
            logger.debug(f"🔌❗❌ {error_msg}")
            raise CtySetValidationError(error_msg)

        logger.debug(f"🔌📝✅ Successfully validated set with {len(validated)} items")
        return CtyValue(type_=self, value=validated)

    def add(self, element) -> "CtySet":
        """
        Add an element to the set.

        Creates a new set that includes all elements from the original set
        plus the new element. This operation is immutable - the original set
        remains unchanged.

        Args:
            element: The element to add to the set. Must conform to the set's
                element_type.

        Returns:
            CtySet: A new CtySet with the original elements plus the new element

        Raises:
            CtySetValidationError: If the element cannot be validated against the
                element_type
        """
        try:
            # Validate the element
            validated_item = self.element_type.validate(element)

            # Create a new set with the additional element
            new_set = set(self.value)
            new_set.add(validated_item)

            return evolve(self, value=new_set)
        except Exception as e:
            raise CtySetValidationError(f"Failed to add element: {e}")

    def remove(self, item: T) -> "CtySet":
        """
        Remove an item from the set.

        Creates a new set that includes all elements from the original set
        except the specified item. This operation is immutable - the original
        set remains unchanged.

        Args:
            item: The item to remove from the set. Must conform to the set's
                element_type.

        Returns:
            CtySet: A new CtySet with the item removed

        Raises:
            CtySetValidationError: If the item cannot be validated or removed
        """
        try:
            validated_item = self.element_type.validate(item)
            new_set = {x for x in self.value if x != validated_item}
            logger.debug(f"🔌📝✅ Removed item from set: {validated_item}")
            return evolve(self, value=new_set)
        except Exception as e:
            logger.debug(f"🔌❗❌ Failed to remove item: {e}")
            raise CtySetValidationError(f"Failed to remove item: {e}")

    def usable_as(self, other: "CtyType") -> bool:
        """
        Check if this type can be used as the other type.

        Determines if values of this set type can be safely used in contexts
        expecting the other type. For sets, this requires the other type to be
        a CtySet with a compatible element type.

        Args:
            other: The other type to check compatibility with

        Returns:
            bool: True if this set type can be used as the other type,
                False otherwise
        """
        result = isinstance(other, CtySet) and self.element_type.usable_as(other.element_type)
        logger.debug(f"🔌📝✅ CtySet.usable_as: {result}")
        return result

    def equal(self, other: "CtyType") -> bool:
        """
        Check if this type is equal to the other type.

        For sets, equality requires the other type to be a CtySet with an
        equal element type. This implements strict type identity checking.

        Args:
            other: The other type to compare with

        Returns:
            bool: True if the types are equal, False otherwise
        """
        if not isinstance(other, CtySet):
            logger.debug(f"🔌📝❌ CtySet.equal: False (other is {type(other).__name__})")
            return False
        result = self.element_type.equal(other.element_type)
        logger.debug(f"🔌📝✅ CtySet.equal: {result}")
        return result

    def __eq__(self, other):
        """
        Equality operator implementation for direct comparison.

        Compares this set type with another object for equality using Python's
        standard equality operator (==). For CtySet instances, this checks
        both type compatibility and set content equality.

        Args:
            other: Object to compare with

        Returns:
            bool: True if the objects are equal, False otherwise
        """
        if not isinstance(other, CtySet):
            return False
        return (
            self.element_type == other.element_type
            and self.value == other.value
        )

    def __iter__(self):
        """
        Create an iterator over the set elements.

        Allows iteration over the set using standard Python iteration syntax,
        such as 'for element in set_instance'. Each iteration yields a value
        from the underlying set.

        Returns:
            Iterator: An iterator over the set values
        """
        return iter(self.value)

    def __str__(self) -> str:
        """
        Get a string representation of this set type.

        Returns a human-readable string representation of the set type,
        indicating that it's a set and showing the element type.

        Returns:
            str: A string representation of the form "set(element_type)"
        """
        return f"set({self.element_type})"

# 🐍🏗️🐣
