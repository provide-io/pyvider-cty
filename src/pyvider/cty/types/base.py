#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from attrs import define

# Forward reference to CtyValue to avoid importing it directly at runtime
if TYPE_CHECKING:
    from pyvider.cty.values.base import CtyValue

T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T")


@runtime_checkable
class CtyTypeProtocol(Protocol[T_co]):
    """Protocol defining the essential interface of a CtyType."""

    def validate(self, value: object) -> CtyValue[T_co]: ...
    def equal(self, other: Any) -> bool: ...
    def usable_as(self, other: Any) -> bool: ...
    def is_primitive_type(self) -> bool: ...


# The concrete ABC now implements the protocol
@define(slots=True)
class CtyType(CtyTypeProtocol[T], Generic[T], ABC):
    """
    Generic abstract base class for all Cty types.
    """

    ctype: ClassVar[str | None] = None
    _type_order: ClassVar[int] = 99

    @abstractmethod
    def validate(self, value: object) -> CtyValue[T]:
        pass

    @abstractmethod
    def equal(self, other: Any) -> bool:
        pass

    @abstractmethod
    def usable_as(self, other: Any) -> bool:
        pass

    @abstractmethod
    def _to_wire_json(self) -> Any:
        """Abstract method for JSON wire format encoding."""

    def unknown_like(self, value: object) -> CtyValue[T]:
        """This type's unknown value, keeping the refinement `value` carries.

        A refinement is what is already known about a value that is not yet known
        — not null, a string's leading characters, a number's bounds, a
        collection's length — and Terraform plans on it. Every `validate` used to
        answer an unknown input with `CtyValue.unknown(self)`, whose payload is
        the `UNREFINED_UNKNOWN` singleton, so the refinement was discarded and the
        ext-12 wire payload go-cty writes came back out as the three bytes of a
        bare unknown. That was invisible only while a container holding an unknown
        element flagged itself wholly unknown; once the collapse went away, every
        refined element in a collection started reaching the encoder through here.

        The refinement is dropped when the type changes, which is go-cty's
        measured behaviour rather than a simplification: refinements are
        type-specific, so a string prefix means nothing on a number and a
        collection's length bounds mean nothing on a string. Converting
        `list(string)` to `list(string)` keeps the element's prefix; converting it
        to `list(number)` yields a bare unknown element.

        Also accepts the unwrapped marker, because that is the shape the msgpack
        decoder produces for a *nested* unknown: only the top-level value is
        rebuilt against the schema, and every element below it arrives at its
        element type as a bare `RefinedUnknownValue`. A marker carries no type of
        its own to disagree with, and the schema being validated against is the
        one the bytes were written for.
        """
        # Imported here, not at module scope: base.py keeps CtyValue as a
        # TYPE_CHECKING-only forward reference to avoid an import cycle, so the name
        # does not exist at runtime.
        from pyvider.cty.values.base import CtyValue
        from pyvider.cty.values.markers import UnknownValue

        if isinstance(value, UnknownValue):
            return CtyValue.unknown(self, value=value)
        if isinstance(value, CtyValue):
            payload = value.value
            # Only a genuine marker is carried across. A hand-built unknown can
            # hold anything at all in `value` — CtyDynamic parks the wrapped
            # CtyValue there — and forwarding that would be inventing a payload
            # rather than preserving one.
            if isinstance(payload, UnknownValue) and self.equal(value.type):
                return CtyValue.unknown(self, value=payload)
        return CtyValue.unknown(self)

    def unknown_marker(self, value: object) -> CtyValue[T] | None:
        """This type's unknown value when `value` is an unwrapped unknown marker.

        Terraform sends unknown for every attribute that depends on for_each, a data
        source or another resource, and an outer type unwrapping its CtyValue leaves
        the marker bare. Collections that only recognised the wrapped form rejected
        those configurations outright, so the check belongs where all of them can
        share it — and stating it once keeps each `validate` under its complexity
        budget rather than paying for the same six lines three times.
        """
        from pyvider.cty.values.markers import UnknownValue

        if isinstance(value, UnknownValue):
            return self.unknown_like(value)
        return None

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


# 🌊🪢🔚
