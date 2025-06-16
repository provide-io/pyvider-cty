
#
# pyvider/cty/types/base.py
#

"""
Core type system foundation for the Cty package.

This module defines the abstract base class for all Cty types, establishing
the interface and common behaviors that specific type implementations must follow.
The type system provides strong typing, validation, and compatibility checking
for values within the Cty ecosystem.
"""

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,  # Add TYPE_CHECKING
    Any,
    ClassVar,
    Generic,
    TypeVar,
)

from attrs import define

if TYPE_CHECKING:  # Add conditional import for CtyValue
    from pyvider.cty.values import CtyValue

from pyvider.cty.exceptions import CtyValidationError

T = TypeVar("T")


@define(slots=True)
class CtyType(ABC, Generic[T]):
    """
    Generic abstract base class for all Cty types.

    CtyType establishes the core interface that all type implementations must implement,
    providing a consistent API for type validation, equality checking, and compatibility
    testing. Types are parameterized with a generic type variable that represents the
    corresponding Python type for values of this Cty type.

    Each specific type implementation extends this class to provide type-specific
    validation logic and behavior.

    Attributes:
        ctype: Class variable identifying the type name in the Cty type system
    """

    ctype: ClassVar[str | None] = None  # Abstract class - no ctype by default

    @classmethod
    def from_raw(cls, value: Any) -> 'CtyType':
        """
        Convert raw Python types to CtyType instances.

        This class method provides a way to create a CtyType instance from a raw
        Python value. By default, it only accepts existing CtyType instances and
        raises an error for other values. Subclasses may override this to provide
        type-specific conversion logic.

        Args:
            value: The value to convert to a CtyType instance

        Returns:
            A CtyType instance

        Raises:
            CtyValidationError: If the value cannot be converted to this type
        """
        if isinstance(value, cls):
            return value
        raise CtyValidationError(
            f"Cannot convert {type(value).__name__} to {cls.__name__}."
        )

    @abstractmethod
    def validate(self, value: Any) -> 'CtyValue[T]':
        """
        Validate and coerce the value to this type.

        This is the core validation method that checks if a given value conforms
        to this type's constraints and converts it if possible. All type implementations
        must provide their own validation logic.

        Args:
            value: The value to validate and coerce

        Returns:
            A CtyValue containing the validated value

        Raises:
            CtyValidationError: If the value cannot be validated as this type
        """
        pass

    @abstractmethod
    def equal(self, other: 'CtyType[T]') -> bool:
        """
        Check equality between this type and another.

        Determines if two types are exactly equal, meaning they represent the
        same type with identical constraints and properties. This is stricter
        than compatibility checking via usable_as().

        Args:
            other: The other type to compare with

        Returns:
            True if the types are exactly equal, False otherwise
        """
        pass

    @abstractmethod
    def usable_as(self, other: 'CtyType[T]') -> bool:
        """
        Determine if this type can be used as another.

        Checks if values of this type can be safely used in contexts expecting
        the other type. This is a compatibility test that may be less strict
        than exact equality.

        Args:
            other: The other type to check compatibility with

        Returns:
            True if this type can be used as the other type, False otherwise
        """
        pass

    # Type checking methods
    def is_primitive_type(self) -> bool:
        """Check if this type is a primitive type (string, number, bool, dynamic)."""
        return False

    def is_collection_type(self) -> bool:
        """Check if this type is a collection type (list, map, set)."""
        return False

    def is_list_type(self) -> bool:
        """Check if this type is a list type."""
        return False

    def is_map_type(self) -> bool:
        """Check if this type is a map type."""
        return False

    def is_set_type(self) -> bool:
        """Check if this type is a set type."""
        return False

    def is_structured_type(self) -> bool:
        """Check if this type is a structured type (object, tuple)."""
        return False

    def is_object_type(self) -> bool:
        """Check if this type is an object type."""
        return False

    def is_tuple_type(self) -> bool:
        """Check if this type is a tuple type."""
        return False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CtyType):
            return self.equal(other)
        return NotImplemented

    def __repr__(self) -> str:
        """
        Get a detailed string representation for debugging.

        Returns a more detailed string representation that includes
        implementation details useful for debugging. Type implementations
        should override this to include type-specific details.

        Returns:
            A detailed string representation of the type
        """
        return f"{self.__class__.__name__}()"

    def __hash__(self) -> int:
        return hash(repr(self))

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the type.

        Returns a concise string representation suitable for display
        to users. Type implementations should override this to provide
        type-specific representations.

        Returns:
            A string representation of the type
        """
        return f"{self.__class__.__name__}"


# 🐍🏗️🐣
