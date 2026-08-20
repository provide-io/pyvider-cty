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


def _ported(marker: object, target: object) -> object:
    """A bare unknown marker's refinement, narrowed to what `target` can carry."""
    from pyvider.cty.values.markers import RefinedUnknownValue

    if isinstance(marker, RefinedUnknownValue):
        return marker.for_type(target)
    return marker


def equal_iteratively(left: Any, right: Any) -> bool:
    """Structural type equality without a Python frame per level of nesting.

    Type structure nests as deeply as the values it describes, and `equal` is
    among the most called methods in this package, so a recursive descent
    overflows the stack for a sufficiently nested type -- out of anything at all
    that compares two of them, `validate` included. A tuple nested 400 deep cost
    two frames a level and raised `RecursionError` on Python 3.11 while passing
    on 3.13, which is the whole margin: 800 frames against a limit of 1000.

    The collection types once solved their own half of this by flattening the
    linear chain of same-kind containers, and said in a comment that branching
    shapes were "bounded by the schema's own breadth". They are not -- a
    single-element tuple nested 400 deep is as linear as a list of lists, and
    overflowed in exactly the same way. This walks any shape with an explicit
    stack instead.

    Each node answers `_equal_shallow`, which decides everything that is not a
    child comparison and hands back the child pairs still to compare, so the
    per-type rules stay with their types.
    """
    children = left._equal_shallow(right)
    if children is None:
        return False
    if not children:
        return True
    stack = list(children)
    while stack:
        this, that = stack.pop()
        pairs = this._equal_shallow(that)
        if pairs is None:
            return False
        stack.extend(pairs)
    return True


@runtime_checkable
class CtyTypeProtocol(Protocol[T_co]):
    """Protocol defining the essential interface of a CtyType.

    A protocol is structural, so anything shaped like a Cty type satisfies this
    whether or not it inherits from `CtyType`. That is the whole point of it,
    and it is also why `CtyType` deliberately does *not* list it as a base.

    Inheriting from a `Protocol` makes `typing._ProtocolMeta` the metaclass of
    every subclass, and `_ProtocolMeta.__instancecheck__` is a Python-level
    function that runs on every `isinstance` against any of them. The concrete
    branch it takes is a two-line pass-through to `_abc_instancecheck`, so it
    buys nothing here -- but a Python frame is not free: 143 ns against 98 ns
    for the plain `ABCMeta` check, and this library asks `isinstance(x,
    SomeCtyType)` six times per stdlib function call. (Only for a *non-exact*
    class; `isinstance(v, type(v))` short-circuits in C before any metaclass is
    consulted, which is why a naive microbenchmark of this shows no difference
    at all.)

    Conformance is still checked, statically, by `_conforms` below.
    """

    def validate(self, value: object) -> CtyValue[T_co]: ...
    def equal(self, other: Any) -> bool: ...
    def usable_as(self, other: Any) -> bool: ...
    def is_primitive_type(self) -> bool: ...


@define(slots=True)
class CtyType(Generic[T], ABC):
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
            # A bare marker carries no type of its own, but the refinement inside
            # it does: it was written against whatever type produced the bytes.
            # Forwarding it unchecked put a string prefix on a number, and
            # re-encoding that emits a payload go-cty rejects outright rather
            # than a value it merely disagrees with.
            return CtyValue.unknown(self, value=_ported(value, self))
        if isinstance(value, CtyValue):
            payload = value.value
            # Only a genuine marker is carried across. A hand-built unknown can
            # hold anything at all in `value` — CtyDynamic parks the wrapped
            # CtyValue there — and forwarding that would be inventing a payload
            # rather than preserving one.
            if isinstance(payload, UnknownValue) and self.equal(value.type):
                return CtyValue.unknown(self, value=payload)
            if isinstance(payload, UnknownValue):
                return CtyValue.unknown(self, value=_ported(payload, self))
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

    def _equal_shallow(self, other: Any) -> tuple[tuple[Any, Any], ...] | None:
        """Everything this type's equality asks that is not a child comparison.

        `None` means unequal; otherwise the child pairs still to compare. The
        default is a leaf's answer -- `equal` decides it outright and has no
        children to descend into. A type whose `equal` would recurse has to
        override this instead, or it puts the frames back.
        """
        return () if self.equal(other) else None

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


if TYPE_CHECKING:

    def _conforms(cty_type: CtyType[T]) -> CtyTypeProtocol[T]:
        """Static-only: every `CtyType` must satisfy `CtyTypeProtocol`.

        The base-class relationship used to carry this check, and dropping it for
        the reason in `CtyTypeProtocol`'s docstring would have dropped the check
        with it. Returning the argument is the whole assertion: the type checker
        rejects this file if the two interfaces ever drift apart, and nothing
        runs at runtime.
        """
        return cty_type


# 🌊🪢🔚
