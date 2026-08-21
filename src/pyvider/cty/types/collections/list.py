#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, cast, final

from attrs import define, field

from pyvider.cty.exceptions import CtyListValidationError, CtyValidationError
from pyvider.cty.path import CtyPath, IndexStep
from pyvider.cty.types.base import (
    CtyType,
    equal_iteratively,
    hash_iteratively,
    render_iteratively,
    usable_as_iteratively,
)
from pyvider.cty.types.structural import CtyDynamic
from pyvider.cty.validation.recursion import with_recursion_detection
from pyvider.cty.values import CtyValue

if TYPE_CHECKING:
    pass

T = TypeVar("T")


@final
@define(frozen=True, slots=True)
class CtyList(CtyType[tuple[T, ...]], Generic[T]):
    ctype: ClassVar[str] = "list"
    _type_order: ClassVar[int] = 5
    element_type: CtyType[T] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.element_type, CtyType):
            raise CtyListValidationError(
                f"Expected CtyType for element_type, got {type(self.element_type).__name__}"
            )

    @with_recursion_detection
    def validate(self, value: object) -> CtyValue[tuple[T, ...]]:

        if isinstance(value, CtyValue):
            if self.equal(value.type) and isinstance(value.value, tuple):
                return cast(CtyValue[tuple[T, ...]], value)  # Fast path for already-validated values
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return self.unknown_like(value)
            value = value.value

        if value is None:
            return CtyValue.null(self)

        if (unknown := self.unknown_marker(value)) is not None:
            return unknown

        # Ordered input only. A `set` used to be accepted, and the list it
        # produced changed order with PYTHONHASHSEED -- the same configuration
        # serialized to different state bytes in different processes.
        if isinstance(value, list | tuple):
            raw_list_to_validate = cast(list[object] | tuple[object, ...], value)
        else:
            raise CtyListValidationError(f"Expected list, tuple, or CtyValue list, got {type(value).__name__}")

        validated_elements: list[CtyValue[T]] = []
        for i, item in enumerate(raw_list_to_validate):
            # A null element is not refused. A null is a value of any type in
            # cty -- nullability is not part of a type there -- so go-cty writes
            # one inside a list and Terraform sends it for `["a", null]`, which
            # is ordinary configuration. This used to raise, and it raised on
            # *read*, so decoding that state failed rather than the value merely
            # being unconstructable. `element_type.validate(None)` already
            # returns a null of the element type, which is what set, tuple and
            # map have always relied on here.
            try:
                validated_item = self.element_type.validate(item)
                validated_elements.append(validated_item)
            except CtyValidationError as e:
                new_path = CtyPath(steps=(IndexStep(i), *(e.path.steps if e.path else ())))
                raise CtyListValidationError(e.message, value=item, path=new_path, original_exception=e) from e

        # A list holding an unknown element is a *known* list. go-cty draws this
        # line at `IsKnown` vs `IsWhollyKnown`, and the distinction is the whole
        # value: the length is known, every known element is known, and only the
        # one element is undecided. Hoisting the element's unknownness onto the
        # container threw all of that away -- `["a", unknown]` encoded to the
        # wire as a bare unknown, losing "a" and the length with it.
        return CtyValue(vtype=self, value=tuple(validated_elements))

    def element_at(self, container: object, index: int) -> CtyValue[T]:

        if isinstance(container, CtyValue):
            if not isinstance(container.type, CtyList):
                raise CtyListValidationError(
                    f"Expected CtyValue with CtyList type, got CtyValue with {type(container.type).__name__}"
                )
            if container.is_null:
                raise IndexError(f"Cannot access element at index {index} in a null list.")
            if container.is_unknown:
                return CtyValue.unknown(self.element_type)
            if not isinstance(container.value, list | tuple):
                raise CtyListValidationError(
                    f"Internal error: CtyValue of CtyList type does not wrap a list/tuple, got {type(container.value).__name__}"
                )
            container_value_seq = cast(list[Any] | tuple[Any, ...], container.value)  # type: ignore[redundant-cast]
            # Inside the taxonomy, and only around the subscript, as of
            # 2026-08-17. This used to catch `TypeError` around the validate call
            # too and re-raise a *new bare* `TypeError` with a message about
            # indices -- so a `TypeError` from anywhere inside element validation
            # was relabelled as an index-type problem, the original was thrown
            # away, and neither answer was a `CtyError` a caller could catch
            # alongside every other validation failure.
            try:
                element = container_value_seq[index]
            except TypeError as e:
                raise CtyListValidationError(
                    f"List index must be an integer or slice, not {type(index).__name__}",
                    value=index,
                ) from e
            return self.element_type.validate(element)

        raise CtyListValidationError(f"Expected CtyValue[CtyList], got {type(container).__name__}")

    def equal(self, other: CtyType[Any]) -> bool:
        return equal_iteratively(self, other)

    def _structure(self) -> tuple[Any, tuple[Any, ...]] | None:
        return ((self.ctype,), (self.element_type,))

    def __eq__(self, other: object) -> bool:
        # Written out rather than left to attrs, which generates a field-by-field
        # comparison that recurses once per level of nesting. `equal` walks.
        # attrs' `auto_detect` leaves both of these alone because they are here.
        return self.equal(other) if isinstance(other, CtyType) else NotImplemented

    def __hash__(self) -> int:
        return hash_iteratively(self)

    def usable_as(self, other: CtyType[Any]) -> bool:
        return usable_as_iteratively(self, other)

    def _usable_shallow(self, other: Any) -> tuple[tuple[Any, Any], ...] | None:

        if isinstance(other, CtyDynamic):
            return ()
        if not isinstance(other, CtyList):
            return None
        return ((self.element_type, other.element_type),)

    def _to_wire_json(self) -> Any:
        return [self.ctype, self.element_type._to_wire_json()]

    def _render(self, children: list[str]) -> str:
        return f"list({children[0]})"

    def __str__(self) -> str:
        return render_iteratively(self)

    def __repr__(self) -> str:
        return f"CtyList(element_type={self.element_type!r})"


# 🌊🪢🔚
