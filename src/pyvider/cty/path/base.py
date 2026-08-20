#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, TypeVar, cast

from attrs import define, field

from pyvider.cty.exceptions import (
    AttributePathError,
    CtyValidationError,
)
from pyvider.cty.types import CtyType
from pyvider.cty.values import CtyValue

T = TypeVar("T")


class PathStep(ABC):
    @abstractmethod
    def apply(self, value: CtyValue[Any]) -> CtyValue[Any]:
        pass

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

    def apply(self, value: CtyValue[Any]) -> CtyValue[Any]:
        if value.is_null:
            raise AttributePathError(f"Cannot get attribute '{self.name}' from null value")
        from pyvider.cty.types.structural import CtyObject

        if isinstance(value.type, CtyObject):
            return value.type.get_attribute(value, self.name)
        raise AttributePathError(
            f"Cannot get attribute from non-object value of type {value.type.__class__.__name__}"
        )

    def apply_type(self, vtype: CtyType[Any]) -> CtyType[Any]:
        from pyvider.cty.types.structural import CtyObject

        if not isinstance(vtype, CtyObject):
            raise AttributePathError(f"Cannot get attribute from non-object type {vtype.__class__.__name__}")
        if not vtype.has_attribute(self.name):
            raise AttributePathError(f"Object type has no attribute {self.name}")
        return vtype.attribute_types[self.name]

    def __str__(self) -> str:
        return f".{self.name}"


@define(frozen=True)
class IndexStep(PathStep):
    index: int = field()

    def apply(self, value: CtyValue[Any]) -> CtyValue[Any]:
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
            result = self.apply(value.value)
            return CtyValue(result.type, result.value)
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
        from pyvider.cty.types.collections import CtySet

        element_type = cast(CtySet[Any], value.type).element_type
        elements = cast("tuple[CtyValue[Any], ...]", value.value)
        if self.key in elements:
            # The set's marks come along: cty cannot hold marks on set elements,
            # so an element's sensitivity is recorded on the set as a whole.
            return cast(CtyValue[Any], self.key).with_marks(value.marks)
        if isinstance(self.key, CtyValue) and self.key.is_unknown:
            return CtyValue.unknown(element_type).with_marks(value.marks)
        if any(element.is_unknown for element in elements):
            # One of the unknowns could still turn out to be the element asked
            # for, so "absent" would be asserting more than the data supports.
            return CtyValue.unknown(element_type).with_marks(value.marks)
        raise AttributePathError("Set does not contain the requested element")

    def apply(self, value: CtyValue[Any]) -> CtyValue[Any]:
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
            result = self.apply(value.value)
            return CtyValue(result.type, result.value)
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
