from typing import Any, ClassVar, Generic, TypeVar, final
from typing import Set as PySet
from attrs import define, evolve, field
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.logger import logger

T = TypeVar('T')

@final
@define(frozen=True, slots=True)
class CtySet(CtyType[PySet[T]], Generic[T]):
    """
    CtySet represents a set type in the Cty type system.

    Sets are collections of unique values of a specific element type.
    Unlike lists, sets are unordered and cannot contain duplicate values.
    """
    ctype: ClassVar[str] = "set"
    element_type: CtyType[T] = field(kw_only=True)  # Mandatory as keyword-only
    value: PySet[T] = field(factory=set, kw_only=True)  # Allow passing value via kw_only

    def __attrs_post_init__(self) -> None:
        """Validate element_type after initialization."""
        if not isinstance(self.element_type, CtyType):
            raise CtyValidationError(
                f"Expected CtyType for element_type, got {type(self.element_type)}"
            )

    #### validate
    def validate(self, value: Any) -> "CtyValue":
        """
        Validate that the given value conforms to this set type.

        Args:
            value: The value to validate

        Returns:
            A CtyValue with the validated set

        Raises:
            CtyValidationError: If validation fails
        """
        logger.debug(f"🔌📝🔄 Validating value as CtySet: {type(value).__name__}")

        # Import locally to avoid circular imports
        from pyvider.cty.values import CtyValue

        if value is None:
            logger.debug("🔌❗❌ Expected iterable, got NoneType")
            raise CtyValidationError(f"Expected iterable, got NoneType")

        if not hasattr(value, '__iter__') or isinstance(value, (str, bytes)):
            logger.debug(f"🔌❗❌ Expected iterable, got {type(value).__name__}")
            raise CtyValidationError(f"Expected iterable, got {type(value).__name__}")

        if not value:
            logger.debug("🔌📝✅ Returning empty set for empty iterable")
            return CtyValue(type_=self, value=set())

        validated = set()
        validation_errors = []

        for i, item in enumerate(value):
            try:
                if isinstance(item, (set, frozenset)):
                    logger.debug("🔌❗❌ Nested sets are not allowed in CtySet")
                    raise CtyValidationError("Nested sets are not allowed in CtySet.")
                    
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
            raise CtyValidationError(error_msg)

        logger.debug(f"🔌📝✅ Successfully validated set with {len(validated)} items")
        return CtyValue(type_=self, value=validated)

    #### add
    def add(self, element) -> "CtySet":
        """
        Add an element to the set.

        Args:
            element: The element to add

        Returns:
            A new CtySet with the element added

        Raises:
            CtyValidationError: If the element cannot be validated
        """
        try:
            # Validate the element
            validated_item = self.element_type.validate(element)

            # Create a new set with the additional element
            new_set = set(self.value)
            new_set.add(validated_item)

            return evolve(self, value=new_set)
        except Exception as e:
            raise CtyValidationError(f"Failed to add element: {e}")

    def remove(self, item: T) -> "CtySet":
        """
        Remove an item from the set.

        Args:
            item: The item to remove

        Returns:
            A new CtySet with the item removed

        Raises:
            CtyValidationError: If the item cannot be removed
        """
        try:
            validated_item = self.element_type.validate(item)
            new_set = {x for x in self.value if x != validated_item}
            logger.debug(f"🔌📝✅ Removed item from set: {validated_item}")
            return evolve(self, value=new_set)
        except Exception as e:
            logger.debug(f"🔌❗❌ Failed to remove item: {e}")
            raise CtyValidationError(f"Failed to remove item: {e}")

    def usable_as(self, other: "CtyType") -> bool:
        """
        Check if this type can be used as the other type.

        Args:
            other: The other type to check against

        Returns:
            True if this type can be used as the other type
        """
        result = isinstance(other, CtySet) and self.element_type.usable_as(other.element_type)
        logger.debug(f"🔌📝✅ CtySet.usable_as: {result}")
        return result

    def equal(self, other: "CtyType") -> bool:
        """
        Check if this type is equal to the other type.

        Args:
            other: The other type to check against

        Returns:
            True if the types are equal
        """
        if not isinstance(other, CtySet):
            logger.debug(f"🔌📝❌ CtySet.equal: False (other is {type(other).__name__})")
            return False
        result = self.element_type.equal(other.element_type)
        logger.debug(f"🔌📝✅ CtySet.equal: {result}")
        return result

    def __eq__(self, other):
        """
        Check if this set is equal to another set.

        Args:
            other: The other set to check against

        Returns:
            True if the sets are equal
        """
        if not isinstance(other, CtySet):
            return False
        return (
            self.element_type == other.element_type
            and self.value == other.value
        )

    def __iter__(self):
        """
        Iterate over the set values.

        Returns:
            An iterator over the set values
        """
        return iter(self.value)

    def __str__(self) -> str:
        """
        Get a string representation of this set type.

        Returns:
            A string representation
        """
        return f"set({self.element_type})"


# 🐍🏗️🐣
