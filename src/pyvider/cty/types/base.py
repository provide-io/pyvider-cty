from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Generic,
    TypeVar,
)

from attrs import define

from pyvider.cty.exceptions import CtyValidationError
from .types_base import CtyTypeProtocol # Import the protocol

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue
    from pyvider.wire.types import TfType # For the internal helper

T = TypeVar("T")

# The concrete ABC now implements the protocol
@define(slots=True)
class CtyType(CtyTypeProtocol[T], ABC, Generic[T]):
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

    def is_primitive_type(self) -> bool:
        return False

    def is_dynamic_type(self) -> bool:
        """Returns True if this type is CtyDynamic."""
        return False
    
    def _to_tf_type(self) -> "TfType":
        """Internal helper for interop tests. Not for public use."""
        from pyvider.conversion.type_encoder import encode_cty_type_to_wire_json
        from pyvider.wire.types import parse_tf_type
        return parse_tf_type(encode_cty_type_to_wire_json(self))
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, CtyType):
            return self.equal(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(repr(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
