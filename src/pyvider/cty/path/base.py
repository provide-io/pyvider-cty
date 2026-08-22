#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, TypeVar, cast
import warnings

from attrs import define, field

from pyvider.cty.exceptions import (
    AttributePathError,
    CtyValidationError,
)
from pyvider.cty.types import CtyType
from pyvider.cty.values import CtyValue

T = TypeVar("T")


class PathStep(ABC):
    def apply(self, value: CtyValue[Any]) -> CtyValue[Any]:
        """Take this step, carrying the receiver's marks onto what it selects.

        go-cty's `Value.Index` (`cty/value_ops.go:866`) and `Value.GetAttr`
        (`:819`) each open the same way -- unmark the receiver, take the step,
        put the marks back -- so a mark on a container is a mark on every value
        read out of it. That is what makes sensitivity travel: `cty_to_msgpack`
        refuses a marked value, and a step that dropped the mark handed back one
        the codec would write to the wire.

        Here rather than in each step, so that a step cannot forget it and a new
        one gets it for nothing. `_apply` is what a step implements, and it is
        never handed a marked receiver.

        Marks accumulate rather than replace: `with_marks` unions, so an
        element's own marks survive alongside the container's.
        """
        if value.marks:
            unmarked, marks = value.unmark()
            return self._apply(unmarked).with_marks(marks)
        return self._apply(value)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Accept a subclass written against the older, public `apply`.

        `apply` used to be the abstract method, so a step outside this package
        implements it and would now be abstract in `_apply` and refuse to
        instantiate -- `PathStep` is exported from `pyvider.cty.path`, so that is
        a break in a public contract. Such a subclass is rewired here instead:
        its `apply` becomes its `_apply`, and the template method above comes
        back from the base class. It keeps working *and* gains the mark handling
        it was written too early to have.

        A subclass that defines both is left alone -- it has said what it means.
        """
        super().__init_subclass__(**kwargs)
        if "apply" in cls.__dict__ and "_apply" not in cls.__dict__:
            warnings.warn(
                f"{cls.__module__}.{cls.__qualname__} overrides PathStep.apply, which is now a"
                " template method that carries the receiver's marks onto the value a step"
                " selects. Implement `_apply` instead; it is handed an already-unmarked value."
                " The old method has been bridged to `_apply` for now.",
                DeprecationWarning,
                stacklevel=2,
            )
            cls._apply = cls.__dict__["apply"]  # type: ignore[method-assign]
            delattr(cls, "apply")

    @abstractmethod
    def _apply(self, value: CtyValue[Any]) -> CtyValue[Any]:
        """Take this step on an unmarked value."""

    @abstractmethod
    def apply_type(self, vtype: CtyType[Any]) -> CtyType[Any]:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


@define(frozen=True)
class GetAttrStep(PathStep):
    """A step into an object attribute by name.

    Any name at all, including the empty one. go-cty puts no constraint on an
    attribute name -- `cty.Object(map[string]cty.Type{"": cty.String})` is an
    ordinary object type, and `merge` produces one from a map with an empty key,
    which HCL can write as `merge({"" = "x"}, {})`.

    This used to refuse an empty name, and the refusal was not confined to
    paths: `CtyObject.validate` builds a `GetAttrStep` for every attribute it
    checks, so *no* value of such an object type could be validated. It escaped
    as a `ValueError` from inside a function implementation, which the framework
    reports as `CtyFunctionPanicError` -- a panic where go-cty answers. Found
    2026-08-19 by the stdlib fuzz, through `merge`.
    """

    name: str = field()

    def _apply(self, value: CtyValue[Any]) -> CtyValue[Any]:
        if value.is_null:
            raise AttributePathError(f"Cannot get attribute '{self.name}' from null value")
        from pyvider.cty.types.structural import CtyDynamic, CtyObject

        # Checked before the unknown case below, and deliberately: an unknown
        # object already answers correctly, with an unknown of the *attribute's*
        # type. Short-circuiting every unknown receiver up front would replace
        # that with `dynamic` and lose what the object type already says.
        if isinstance(value.type, CtyObject):
            return value.type.get_attribute(value, self.name)
        if isinstance(value.type, CtyDynamic):
            # A `dynamic` wrapper is stepped through, as `IndexStep` and `KeyStep`
            # already did. Only this step lacked the branch, so an attribute of an
            # object inside a wrapper was unreachable by path while an element of a
            # list inside one was reachable. Recursed through `apply` rather than
            # `_apply` so the payload's own marks are picked up as well.
            if isinstance(value.value, CtyValue):
                return self.apply(value.value)
            # A wholly unknown `dynamic` has no inner value to step into. Its own
            # `apply_type` answers `dynamic` here, and `IndexStep` and `KeyStep`
            # both hand back an unknown; this raised, so a type could be walked
            # where the value it described could not.
            if value.is_unknown:
                return CtyValue.unknown(CtyDynamic())
        raise AttributePathError(
            f"Cannot get attribute from non-object value of type {value.type.__class__.__name__}"
        )

    def apply_type(self, vtype: CtyType[Any]) -> CtyType[Any]:
        from pyvider.cty.types.structural import CtyDynamic, CtyObject

        if isinstance(vtype, CtyDynamic):
            return CtyDynamic()
        if not isinstance(vtype, CtyObject):
            raise AttributePathError(f"Cannot get attribute from non-object type {vtype.__class__.__name__}")
        if not vtype.has_attribute(self.name):
            raise AttributePathError(f"Object type has no attribute {self.name}")
        return vtype.attribute_types[self.name]

    def __str__(self) -> str:
        return f".{self.name}"


@define(frozen=True)
class IndexStep(PathStep):
    """A step into a list or tuple by position.

    Stepping through a `dynamic` wrapper returns what the inner step selected,
    whole. It used to rebuild the answer as `CtyValue(result.type, result.value)`
    -- two of the five fields a `CtyValue` carries -- which turned a null into
    `is_null=False, value=None`, an unknown into `is_unknown=False,
    value=UNREFINED_UNKNOWN`, and a refined unknown into a known value whose
    payload was the refinement object. None of the three is a value this library
    can represent, so a consumer reading `is_null` believed a null was a present
    value holding `None`. `KeyStep` had the same line and the same defect.

    The check is internal consistency rather than go-cty parity: go-cty has no
    known-dynamic value to compare against, because `Index` and `GetAttr` on a
    `DynamicPseudoType` receiver return `DynamicVal`.
    """

    index: int = field()

    def _apply(self, value: CtyValue[Any]) -> CtyValue[Any]:
        if value.is_null:
            raise AttributePathError("Cannot index into null value")
        if value.is_unknown:
            return CtyValue.unknown(self.apply_type(value.type))
        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyDynamic, CtyTuple

        if isinstance(value.type, CtyList | CtyTuple):
            list_or_tuple_type = cast(CtyList[Any] | CtyTuple, value.type)  # type: ignore[redundant-cast]
            return list_or_tuple_type.element_at(value, self.index)
        if isinstance(value.type, CtyDynamic) and isinstance(value.value, CtyValue):
            return self.apply(value.value)
        raise AttributePathError(f"Cannot index into value of type {type(value.type).__name__}")

    def apply_type(self, vtype: CtyType[Any]) -> CtyType[Any]:
        from pyvider.cty.types.collections import CtyList
        from pyvider.cty.types.structural import CtyDynamic, CtyTuple

        if isinstance(vtype, CtyList):
            return vtype.element_type
        if isinstance(vtype, CtyTuple):
            try:
                return vtype.element_types[self.index]
            except IndexError as e:
                raise AttributePathError(f"Tuple index {self.index} out of bounds") from e
        if isinstance(vtype, CtyDynamic):
            return CtyDynamic()
        raise AttributePathError(f"Cannot index into non-collection type {vtype.__class__.__name__}")

    def __str__(self) -> str:
        return f"[{self.index}]"


@define(frozen=True)
class KeyStep(PathStep):
    """A step into a map by its key, or into a set by the element itself.

    The set case exists because a traversal has to be able to say where it is.
    go-cty puts it on `IndexStep` and explains the reasoning there: a path
    "is often used to describe the current location in a nested data structure
    when working with functions like Walk or Transform, and in that case
    traversal into a set is represented as an IndexStep whose key is the set
    element value itself, with the idea that a set element effectively acts as
    its own key in the set". pyvider splits go-cty's single `IndexStep` into an
    int-keyed `IndexStep` and this key-keyed one, so the set case lands here.
    """

    key: object = field()

    def _apply_to_set(self, value: CtyValue[Any]) -> CtyValue[Any]:
        """Find the element that keys itself, by cty identity rather than `==`.

        `set_order.identity_key` is `makeSetHashBytes` paired with the canonical
        key -- what `CtySet.validate` de-duplicates on -- so the lookup agrees
        with what the set actually holds. Python equality did not: a
        `Decimal("-0")` equals a `Decimal("0")`, so a path of `[0]` into
        `toset([-0])` matched the negative zero and handed back the positive one.
        go-cty keeps the two apart, and gives them separate paths:
        `soup-go cty walk --type '["set","number"]' '[-0,0]'` visits both.

        The element found is returned rather than the key, which now matters:
        with identity deciding, they can differ only in ways the set itself
        distinguishes, and the set's member is the one that is really there.

        The key is unmarked before the lookup and its marks go onto the answer.
        A marked key asks after the same element an unmarked one does --
        `identity_key` strips marks, as go-cty's hashing does, so a marked key
        used to find nothing at all -- but asking with a sensitive value is a
        sensitive question, so the mark travels the way `PathStep.apply` carries
        the receiver's. The set's own marks are already `apply`'s doing; it
        unmarked `value` before calling here.

        A key that is not a `CtyValue` matches nothing, as before: `CtyValue.__eq__`
        returns `NotImplemented` against a raw operand, so it never matched either.
        """
        from pyvider.cty.types.collections import CtySet
        from pyvider.cty.values.set_order import identity_key

        element_type = cast(CtySet[Any], value.type).element_type
        elements = cast("tuple[CtyValue[Any], ...]", value.value)

        key = self.key
        key_marks: frozenset[Any] = frozenset()
        if isinstance(key, CtyValue) and key.marks:
            key, key_marks = key.unmark()

        def answered(selected: CtyValue[Any]) -> CtyValue[Any]:
            return selected.with_marks(key_marks) if key_marks else selected

        if isinstance(key, CtyValue):
            wanted = identity_key(key)
            for element in elements:
                if identity_key(element) == wanted:
                    return answered(element)
            if key.is_unknown:
                return answered(CtyValue.unknown(element_type))
        if any(element.is_unknown for element in elements):
            # One of the unknowns could still turn out to be the element asked
            # for, so "absent" would be asserting more than the data supports.
            return answered(CtyValue.unknown(element_type))
        raise AttributePathError("Set does not contain the requested element")

    def _apply(self, value: CtyValue[Any]) -> CtyValue[Any]:
        if value.is_null:
            raise AttributePathError("Cannot get key from null value")
        if value.is_unknown:
            return CtyValue.unknown(self.apply_type(value.type))
        from pyvider.cty.types.collections import CtyMap, CtySet
        from pyvider.cty.types.structural import CtyDynamic

        if isinstance(value.type, CtyMap):
            return value.type.get(value, self.key)
        if isinstance(value.type, CtySet):
            return self._apply_to_set(value)
        if isinstance(value.type, CtyDynamic) and isinstance(value.value, CtyValue):
            return self.apply(value.value)
        raise AttributePathError(
            f"Cannot get key from non-map/non-dynamic value of type {type(value.type).__name__}"
        )

    def apply_type(self, vtype: CtyType[Any]) -> CtyType[Any]:
        from pyvider.cty.types import CtyString
        from pyvider.cty.types.collections import CtyMap, CtySet
        from pyvider.cty.types.structural import CtyDynamic

        if isinstance(vtype, CtyDynamic):
            return CtyDynamic()
        if isinstance(vtype, CtySet):
            return vtype.element_type
        if not isinstance(vtype, CtyMap):
            raise AttributePathError(f"Cannot get key from non-map type {vtype.__class__.__name__}")
        try:
            CtyString().validate(self.key)
        except CtyValidationError as e:
            raise AttributePathError(f"Invalid key for map: {self.key!r} is not a valid string") from e
        return vtype.element_type

    def __str__(self) -> str:
        # A set element keys itself, so the raw key is a whole CtyValue whose
        # repr would swamp the path. Show what it holds instead.
        if isinstance(self.key, CtyValue):
            return f"[{self.key.value!r}]"
        return f"[{self.key!r}]"


def _as_steps(steps: Iterable[PathStep]) -> tuple[PathStep, ...]:
    """Store the steps as a tuple, while still accepting the list callers pass."""
    return tuple(steps)


@define(frozen=True)
class CtyPath:
    """A location within a nested value, as the steps taken to reach it.

    Frozen, and so hashable, which is what lets a plain `set[CtyPath]` stand in
    for go-cty's `PathSet`. go-cty needs a dedicated type there only because Go
    cannot hash a slice -- it ships crc64 hashing rules to fake it. `steps` is
    stored as a tuple for the same reason; the converter still accepts a list,
    so existing construction keeps working.
    """

    steps: tuple[PathStep, ...] = field(factory=tuple, converter=_as_steps)

    @classmethod
    def empty(cls) -> CtyPath:
        return cls(())

    @classmethod
    def get_attr(cls, name: str) -> CtyPath:
        return cls((GetAttrStep(name),))

    @classmethod
    def index(cls, index: int) -> CtyPath:
        return cls((IndexStep(index),))

    @classmethod
    def key(cls, key: object) -> CtyPath:
        return cls((KeyStep(key),))

    def with_step(self, step: PathStep) -> CtyPath:
        """This path with one more step on the end."""
        return CtyPath((*self.steps, step))

    def child(self, name: str) -> CtyPath:
        return self.with_step(GetAttrStep(name))

    def index_step(self, index: int) -> CtyPath:
        return self.with_step(IndexStep(index))

    def key_step(self, key: object) -> CtyPath:
        return self.with_step(KeyStep(key))

    def apply_path(self, value: object) -> CtyValue[Any]:
        if not self.steps:
            if isinstance(value, CtyValue):
                return value
            raise AttributePathError("Cannot return non-CtyValue from apply_path")
        if not isinstance(value, CtyValue):
            raise AttributePathError(f"Cannot apply path to non-CtyValue: {type(value).__name__}")
        current = value
        for i, step in enumerate(self.steps):
            try:
                current = step.apply(current)
            except AttributePathError as e:
                raise AttributePathError(f"Error at step {i + 1} ({step}): {e}") from e
        return current

    def apply_path_type(self, vtype: CtyType[Any]) -> CtyType[Any]:
        if not self.steps:
            return vtype
        current = vtype
        for i, step in enumerate(self.steps):
            try:
                current = step.apply_type(current)
            except AttributePathError as e:
                raise AttributePathError(f"Error at type step {i + 1} ({step}): {e}") from e
        return current

    def string(self) -> str:
        if not self.steps:
            return "(root)"

        path_str = ""
        for i, step in enumerate(self.steps):
            current_step_str = str(step)
            if i == 0 and isinstance(step, GetAttrStep):
                path_str += current_step_str[1:]  # Strip leading dot
            else:
                path_str += current_step_str

        return path_str

    def __str__(self) -> str:
        return self.string()


# 🌊🪢🔚
