
from typing import (
    Any,
    TypeVar,
)

from attr import define, field

from .base import CtyType

# Define generic type variable
T = TypeVar("T")

@define
class DynamicPseudoType(CtyType[Any]):
    """Represents a dynamic type that can match any other type."""
    metadata: tuple = field(factory=tuple)
    validators: tuple = field(factory=tuple)  # Ensure validators is always initialized


    def validate(self, value: Any) -> Any:
        """Always validates successfully."""
        self._run_validators(value)
        return value

    def equal(self, other: "CtyType[Any]") -> bool:
        """Check if other type is also DynamicPseudoType."""
        return isinstance(other, DynamicPseudoType)

    def usable_as(self, other: "CtyType[Any]") -> bool:
        """Always returns True - compatible with all types."""
        return True

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
