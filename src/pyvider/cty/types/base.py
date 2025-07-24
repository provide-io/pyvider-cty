from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    TypeVar,
)

from attrs import define

from .types_base import CtyTypeProtocol  # Import the protocol

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue

T = TypeVar("T")


# The concrete ABC now implements the protocol
@define(slots=True)
class CtyType[T](CtyTypeProtocol[T], ABC):
    """
    Generic abstract base class for all Cty types.
    """

    ctype: ClassVar[str | None] = None

    @abstractmethod
    def validate(self, value: object) -> "CtyValue[T]":
        pass

    @abstractmethod
    def equal(self, other: "CtyType[T]") -> bool:
        pass

    @abstractmethod
    def usable_as(self, other: "CtyType[T]") -> bool:
        pass

    @abstractmethod
    def _to_wire_json(self) -> Any:
        """Abstract method for JSON wire format encoding."""
        pass

    def is_primitive_type(self) -> bool:
        return False

    def is_dynamic_type(self) -> bool:
        """Returns True if this type is CtyDynamic."""
        return False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CtyType):
            return self.equal(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(repr(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
