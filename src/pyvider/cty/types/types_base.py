# pyvider-cty/src/pyvider/cty/types/types_base.py
"""Base protocols to prevent circular imports in the CTY type system."""

from __future__ import annotations

from typing import Any, Protocol, TypeVar, runtime_checkable

# Forward reference to CtyValue to avoid importing it directly
if "CtyValue" not in globals():
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from pyvider.cty.values.base import CtyValue

T = TypeVar("T")


@runtime_checkable
class CtyTypeProtocol(Protocol[T]):
    """Protocol defining the essential interface of a CtyType."""

    def validate(self, value: object) -> CtyValue[T]: ...
    def equal(self, other: Any) -> bool: ...
    def usable_as(self, other: Any) -> bool: ...
    def is_primitive_type(self) -> bool: ...
