#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from collections import OrderedDict
from typing import Any, ClassVar, Generic, TypeVar, cast, final

from attrs import define, field

from pyvider.cty.exceptions import CtySetValidationError, CtyValidationError
from pyvider.cty.marks import _strip, collect_marks_deep
from pyvider.cty.types.base import CtyType, equal_iteratively
from pyvider.cty.validation.recursion import with_recursion_detection
from pyvider.cty.values import CtyValue
from pyvider.cty.values.set_order import identity_key as set_identity_key, order_key as set_order_key

T = TypeVar("T")

# Payloads that can hide a mark below the top level; anything else is a leaf.
_NESTING_PAYLOADS = (CtyValue, dict, list, tuple, set, frozenset)


def _has_marked_elements(value: CtyValue[Any]) -> bool:
    """Whether any element carries a mark, answered without a walk when possible.

    Re-validating an already-validated set was constant time until this check
    was added, and scanning every element on every call made it O(n) -- 13 ms
    for a 50k set that used to cost microseconds. `collect_marks_deep` is
    memoized for an immutable payload, so the overwhelmingly common answer
    ("nothing anywhere is marked") now costs one lookup, and only a set that
    really does carry marks pays for finding out where they are.
    """
    if not collect_marks_deep(value):
        return False
    elements = cast("tuple[CtyValue[Any], ...]", value.value)
    return any(collect_marks_deep(element) for element in elements)


@final
@define(frozen=True, slots=True)
class CtySet(CtyType[tuple[T, ...]], Generic[T]):
    ctype: ClassVar[str] = "set"
    _type_order: ClassVar[int] = 4
    element_type: CtyType[T] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.element_type, CtyType):
            raise CtySetValidationError(f"Expected CtyType for element_type, got {type(self.element_type)}")

    def _short_circuit(self, value: object) -> tuple[CtyValue[tuple[T, ...]] | None, object]:
        """The answers that need no validation: null, unknown in either shape, and a
        value already of this exact type. Returns (answer, value-to-validate)."""
        if value is None:
            return CtyValue.null(self), value
        if isinstance(value, CtyValue):
            if value.is_unknown:
                return self.unknown_like(value), value
            if value.is_null:
                return CtyValue.null(self), value
            # The pass-through requires the value to already satisfy the
            # invariant this type enforces: no marked elements, marks on the set
            # itself. A hand-built set with marked elements would otherwise skip
            # the hoisting below and keep them, which de-duplication then drops.
            if (
                isinstance(value.type, CtySet)
                and value.type.equal(self)
                and isinstance(value.value, tuple)
                and not _has_marked_elements(value)
            ):
                return cast(CtyValue[tuple[T, ...]], value), value
            value = value.value
        return self.unknown_marker(value), value

    @with_recursion_detection
    def validate(self, value: object) -> CtyValue[tuple[T, ...]]:
        answer, value = self._short_circuit(value)
        if answer is not None:
            return answer

        if not isinstance(value, list | tuple | set | frozenset):
            raise CtySetValidationError(
                f"Expected a Python set, frozenset, list, or tuple, got {type(value).__name__}"
            )

        value_iterable = cast(list[Any] | tuple[Any, ...] | set[Any] | frozenset[Any], value)  # type: ignore[redundant-cast]
        unique_items: OrderedDict[tuple[Any, ...], CtyValue[Any]] = OrderedDict()
        # Marks are hoisted off the elements onto the set itself, as go-cty's
        # `SetVal` does (cty/value_init.go). A set cannot hold a marked element:
        # de-duplication keys on the element's value, which is mark-blind, so an
        # element marked sensitive that collides with an equal unmarked one was
        # simply overwritten and its mark lost. go-cty goes further and panics on
        # hashing a marked element (cty/set_internals.go) rather than trust the
        # invariant to callers.
        element_marks: set[Any] = set()
        # Unknown elements are held apart from the de-duplicated ones. go-cty is
        # explicit that "two unknown values are not equivalent for the sake of
        # set membership" (cty/set_internals.go): its `Equivalent` compares
        # `Equals(...) == true`, and unknown-against-unknown is undecided, so
        # both survive. De-duplicating them would claim a cardinality the value
        # does not have -- `toset([a.id, b.id])` at plan time is two elements,
        # not one, and the count reaches Terraform.
        undecided: list[CtyValue[Any]] = []
        for raw_item in value_iterable:
            try:
                validated_item = self.element_type.validate(raw_item)
                # Only look for marks where one could be hiding, and only
                # rebuild an element that actually carries one. A leaf answers
                # from its own `marks`; `_strip` walks and reconstructs the
                # whole element, which on an unmarked set is pure overhead paid
                # once per member.
                if validated_item.marks or isinstance(validated_item.value, _NESTING_PAYLOADS):
                    item_marks = collect_marks_deep(validated_item)
                    if item_marks:
                        element_marks.update(item_marks)
                        validated_item = _strip(validated_item)
                if validated_item.is_unknown:
                    undecided.append(validated_item)
                else:
                    unique_items[set_identity_key(validated_item)] = validated_item
            except CtyValidationError as e:
                raise CtySetValidationError(e.message, value=raw_item) from e
            except Exception as e:
                raise CtySetValidationError(f"Failed to process element for set: {e}", value=raw_item) from e

        # Canonical order, not a frozenset. Two unknowns of one type are `==` and
        # hash-equal here, so a frozenset payload could not hold both however the
        # de-duplication above was written -- the container itself was the
        # constraint. An ordered tuple is also what `CtySet` has always declared
        # (`CtyType[tuple[T, ...]]`), and it makes the wire order a property of
        # the value rather than something each encoder re-derives.
        #
        # The sort is stable and `_canonical_sort_key` ranks known 0, unknown 1,
        # null 2, so this reproduces go-cty's observed iteration order exactly:
        # known elements sorted by value, then the unknowns in the order they
        # were supplied, then nulls last.
        elements = sorted((*unique_items.values(), *undecided), key=set_order_key)
        result: CtyValue[tuple[T, ...]] = CtyValue(vtype=self, value=tuple(elements))
        return result.with_marks(element_marks) if element_marks else result

    def equal(self, other: CtyType[Any]) -> bool:
        return equal_iteratively(self, other)

    def _equal_shallow(self, other: Any) -> tuple[tuple[Any, Any], ...] | None:
        if not isinstance(other, CtySet):
            return None
        return ((self.element_type, other.element_type),)

    def usable_as(self, other: CtyType[Any]) -> bool:
        from pyvider.cty.types.structural import CtyDynamic

        if isinstance(other, CtyDynamic):
            return True
        if not isinstance(other, CtySet):
            return False
        return self.element_type.usable_as(other.element_type)

    def _to_wire_json(self) -> Any:
        return [self.ctype, self.element_type._to_wire_json()]

    def __str__(self) -> str:
        return f"set({self.element_type})"


# 🌊🪢🔚
