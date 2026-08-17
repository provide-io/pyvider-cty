#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from collections.abc import Iterator, Set as AbstractSet
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Self,
    TypeVar,
)

from attrs import define, evolve, field

from pyvider.cty.config.defaults import (
    ERR_CANNOT_COMPARE_CTYVALUE_WITH,
    ERR_CANNOT_COMPARE_DIFFERENT_TYPES,
    ERR_CANNOT_COMPARE_NULL_UNKNOWN,
    ERR_CANNOT_GET_LENGTH_UNKNOWN_VALUE,
    ERR_CANNOT_GET_RAW_VALUE_UNKNOWN,
    ERR_CANNOT_INDEX_UNKNOWN_NULL_VALUE,
    ERR_CANNOT_ITERATE_UNKNOWN_VALUE,
    ERR_VALUE_TYPE_NO_LEN,
    ERR_VALUE_TYPE_NOT_COMPARABLE,
    ERR_VALUE_TYPE_NOT_ITERABLE,
    ERR_VALUE_TYPE_NOT_SUBSCRIPTABLE,
)
from pyvider.cty.values.markers import UNREFINED_UNKNOWN

T = TypeVar("T", covariant=True)

if TYPE_CHECKING:
    from pyvider.cty.types import CtyType


@define(frozen=True, slots=True)
class CtyValue(Generic[T]):
    vtype: CtyType[T] = field()
    value: object | None = field(default=None)
    is_unknown: bool = field(default=False)
    is_null: bool = field(default=False)
    marks: frozenset[Any] = field(factory=frozenset)

    # Memo for `collect_marks_deep`, filled on first ask. Excluded from init,
    # equality, hashing and repr: it is derived state, not part of the value.
    #
    # Only filled when that walk proves the whole subtree immutable. Freezing
    # this class freezes the reference to `value`, not what `value` points at:
    # maps and objects hold a plain dict, and `validate` accepts raw lists. A
    # memo taken over one of those could be left under-reporting marks by an
    # in-place mutation, which is the silent declassification the mark machinery
    # exists to prevent. See `pyvider.cty.marks._walk_marks`.
    _deep_marks: frozenset[Any] | None = field(default=None, init=False, eq=False, repr=False)

    # Memo for `_strip`, filled on first ask and under the same immutability
    # rule as `_deep_marks`. Stripping rebuilds the whole subtree, and the
    # function wrapper strips every marked argument on every call, so without
    # this a marked 50k-element list cost 40 ms per stdlib call against 0.005 ms
    # for the same list unmarked.
    _stripped: Any = field(default=None, init=False, eq=False, repr=False)

    def __attrs_post_init__(self) -> None:
        from pyvider.cty.types import CtyDynamic

        if isinstance(self.vtype, CtyDynamic) and isinstance(self.value, CtyValue):
            object.__setattr__(self, "is_unknown", self.value.is_unknown)
            object.__setattr__(self, "is_null", self.value.is_null)

        if self.is_unknown and self.is_null:
            object.__setattr__(self, "is_null", False)
        elif self.is_null and self.value is not None:
            object.__setattr__(self, "value", None)

    @property
    def type(self) -> CtyType[T]:
        return self.vtype

    @property
    def raw_value(self) -> object | None:
        if self.is_unknown:
            error_message = ERR_CANNOT_GET_RAW_VALUE_UNKNOWN
            raise ValueError(error_message)
        if self.is_null:
            return None
        from ..conversion.adapter import cty_to_native

        return cty_to_native(self)  # type: ignore

    def _canonical_sort_key(self) -> tuple[Any, ...]:
        """The order go-cty puts a set's elements in, which reaches the wire.

        go-cty's `setRules.Less` (`cty/set_internals.go:99-110`) ranks known
        values first, then unknown, then null -- in that order, and it checks
        nullness *before* knownness, so an unknown sorts ahead of a null. These
        three ranks were previously the exact inverse, which is not a
        preference: a set holding a null re-encoded with the null first where
        go-cty writes it last. Both decode to the same value, so only a byte
        comparison catches it -- and Terraform compares serialized state, so it
        was a diff that reappeared on every plan.

        Doubles as this library's *only* notion of value identity, as of
        2026-08-17. `CtySet.validate` de-duplicates with it and `__hash__` now
        hashes it, which is what makes a set of containers work at all -- the
        two used to disagree, and only one of them worked. It is the analogue of
        go-cty's `makeSetHashBytes` (`cty/set_internals.go:144-278`), which
        likewise serializes a whole value and is likewise mark-blind.

        Total, and never raising: a member that is not a `CtyValue` is keyed by
        its repr and a mapping is ordered by `str(key)`. Only a hand-built value
        can hold either -- `validate` normalises members -- and both used to
        reach `AttributeError`/`TypeError` from here, which is the same escape
        from the error taxonomy that the bare `TypeError` in `__hash__` was.
        """
        from ..types import (
            CtyBool,
            CtyCapsule,
            CtyList,
            CtyMap,
            CtyNumber,
            CtyObject,
            CtySet,
            CtyString,
            CtyTuple,
        )

        if self.is_null:
            return (2,)
        if self.is_unknown:
            return (1,)

        type_rank = self.type._type_order
        key_prefix = (0, type_rank)

        if isinstance(self.type, CtyBool | CtyNumber | CtyString):
            return (*key_prefix, self.value)

        if (
            isinstance(self.type, CtyList | CtyTuple)
            and self.value is not None
            and hasattr(self.value, "__iter__")
        ):
            return (*key_prefix, *(_member_key(v) for v in self.value))

        if isinstance(self.type, CtySet) and self.value is not None and hasattr(self.value, "__iter__"):
            sorted_elements = sorted(self.value, key=_member_key)
            return (*key_prefix, *(_member_key(v) for v in sorted_elements))

        if (
            isinstance(self.type, CtyMap | CtyObject)
            and self.value is not None
            and hasattr(self.value, "items")
        ):
            # Keyed on `str(name)` rather than the raw pair. A mapping payload's
            # keys are attribute or element names and so are strings, for which
            # this is the identical order; sorting the pairs themselves raised
            # for a hand-built payload whose keys were not all one type.
            sorted_items = sorted(self.value.items(), key=lambda item: str(item[0]))
            return (
                *key_prefix,
                *((k, _member_key(v)) for k, v in sorted_items),
            )

        if isinstance(self.type, CtyCapsule):
            return (*key_prefix, repr(self.value))

        # Fallback for any other type
        return (*key_prefix, repr(self.value))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CtyValue):
            return NotImplemented
        from ..types import CtyCapsuleWithOps

        if isinstance(self.type, CtyCapsuleWithOps) and self.type.equal(other.type) and self.type.equal_fn:
            return self.type.equal_fn(self.value, other.value)

        return (
            self.type.equal(other.type)
            and self.is_unknown == other.is_unknown
            and self.is_null == other.is_null
            and self.marks == other.marks
            and self.value == other.value
        )

    def _check_comparable(self, other: object) -> CtyValue[Any]:
        from ..types import CtyNumber, CtyString

        if not isinstance(other, CtyValue):
            error_message = ERR_CANNOT_COMPARE_CTYVALUE_WITH.format(type_name=type(other).__name__)
            raise TypeError(error_message)
        if self.is_unknown or self.is_null or other.is_unknown or other.is_null:
            error_message = ERR_CANNOT_COMPARE_NULL_UNKNOWN
            raise TypeError(error_message)
        if not self.type.equal(other.type):
            error_message = ERR_CANNOT_COMPARE_DIFFERENT_TYPES.format(type1=self.type, type2=other.type)
            raise TypeError(error_message)
        if not isinstance(self.type, CtyNumber | CtyString):
            error_message = ERR_VALUE_TYPE_NOT_COMPARABLE.format(type=self.type)
            raise TypeError(error_message)
        return other

    def __lt__(self, other: object) -> bool:
        other_val = self._check_comparable(other)
        if hasattr(self.value, "__lt__"):
            return bool(self.value < other_val.value)
        error_message = ERR_VALUE_TYPE_NOT_COMPARABLE.format(type=self.type)
        raise TypeError(error_message)

    def __le__(self, other: object) -> bool:
        other_val = self._check_comparable(other)
        if hasattr(self.value, "__le__"):
            return bool(self.value <= other_val.value)
        error_message = ERR_VALUE_TYPE_NOT_COMPARABLE.format(type=self.type)
        raise TypeError(error_message)

    def __gt__(self, other: object) -> bool:
        other_val = self._check_comparable(other)
        if hasattr(self.value, "__gt__"):
            return bool(self.value > other_val.value)
        error_message = ERR_VALUE_TYPE_NOT_COMPARABLE.format(type=self.type)
        raise TypeError(error_message)

    def __ge__(self, other: object) -> bool:
        other_val = self._check_comparable(other)
        if hasattr(self.value, "__ge__"):
            return bool(self.value >= other_val.value)
        error_message = ERR_VALUE_TYPE_NOT_COMPARABLE.format(type=self.type)
        raise TypeError(error_message)

    def __contains__(self, item: Any) -> bool:
        if self.is_unknown or self.is_null:
            return False
        if hasattr(self.value, "__contains__"):
            return item in self.value
        return bool(self.value == item)

    def __bool__(self) -> bool:
        from pyvider.cty.types import CtyDynamic

        if self.is_unknown or self.is_null:
            return False
        if isinstance(self.vtype, CtyDynamic) and isinstance(self.value, CtyValue):
            return bool(self.value)
        return True

    def __len__(self) -> int:
        from pyvider.cty.types import CtyDynamic, CtyList, CtyMap, CtySet, CtyTuple

        if self.is_unknown:
            error_message = ERR_CANNOT_GET_LENGTH_UNKNOWN_VALUE
            raise TypeError(error_message)
        if isinstance(self.vtype, CtyDynamic) and isinstance(self.value, CtyValue):
            return len(self.value)
        if self.is_null:
            return 0
        if isinstance(self.vtype, CtyList | CtyMap | CtySet | CtyTuple) and hasattr(self.value, "__len__"):
            return len(self.value)
        error_message = ERR_VALUE_TYPE_NO_LEN.format(type_name=self.vtype.__class__.__name__)
        raise TypeError(error_message)

    def __iter__(self) -> Iterator[Any]:
        from pyvider.cty.types import CtyList, CtyMap, CtySet, CtyTuple

        if self.is_unknown:
            error_message = ERR_CANNOT_ITERATE_UNKNOWN_VALUE
            raise TypeError(error_message)
        if self.is_null:
            return iter([])
        if isinstance(self.vtype, CtyList | CtySet | CtyTuple) and hasattr(self.value, "__iter__"):
            return iter(self.value)
        if isinstance(self.vtype, CtyMap) and hasattr(self.value, "values"):
            return iter(self.value.values())

        error_message = ERR_VALUE_TYPE_NOT_ITERABLE.format(type_name=self.vtype.__class__.__name__)
        raise TypeError(error_message)

    def __getitem__(self, key: Any) -> CtyValue[Any]:
        from ..types import CtyList, CtyMap, CtyObject, CtyTuple

        if self.is_unknown or self.is_null:
            error_message = ERR_CANNOT_INDEX_UNKNOWN_NULL_VALUE
            raise TypeError(error_message)
        if isinstance(self.vtype, CtyObject):
            if not isinstance(key, str):
                raise TypeError(f"Object attribute name must be a string, got {type(key).__name__}")
            return self.vtype.get_attribute(self, key)
        if isinstance(self.vtype, CtyList):
            if not isinstance(self.value, list | tuple):
                raise TypeError(f"CtyList value is not a list/tuple, but {type(self.value).__name__}")
            if isinstance(key, slice):
                return CtyValue(vtype=self.vtype, value=tuple(self.value[key]))
            return self.vtype.element_at(self, key)
        if isinstance(self.vtype, CtyTuple):
            return self.vtype.element_at(self, key)
        if isinstance(self.vtype, CtyMap):
            return self.vtype.get(self, key)  # type: ignore[arg-type]
        error_message = ERR_VALUE_TYPE_NOT_SUBSCRIPTABLE.format(type_name=self.vtype.__class__.__name__)
        raise TypeError(error_message)

    def __hash__(self) -> int:
        """A hash for **every** value, containers included, as of 2026-08-17.

        This used to raise a bare `TypeError` for `list`, `set`, `map` and
        `object`, on the reasoning that Python cannot hash a mutable payload.
        The reasoning was wrong twice over. A validated container's payload is
        immutable (a tuple, or a `FrozenDict`), and go-cty hashes containers
        without hesitation -- `makeSetHashBytes` (`cty/set_internals.go:144`)
        serializes a whole value and crc32s it, which is why `set(object({}))`,
        Terraform's nested-block-set type, works there.

        The raise was reachable from ten public entry points -- `Value.Equals`
        on any set of containers, `setunion`, `contains`, `lookup`, `zipmap`,
        `distinct`, `in` and `without_key` on a map, and the paths `deep_values`
        hands out -- all with one trigger: a set whose element type is itself a
        container. It survived a msgpack round-trip, so decoded wire data
        reached it. And being a bare `TypeError` it fell outside `CtyError`, so
        a caller's `except CtyFunctionError` missed it and it surfaced to
        Terraform as a provider crash rather than a diagnostic.

        The hash is the canonical sort key, which is the same notion of identity
        `CtySet.validate` already de-duplicates with. Having two notions and
        only one of them working is what produced a library that could *build*
        a set of lists but not compare one.

        Consistency with `__eq__` (`a == b` implies equal hashes) holds because
        every field `__eq__` looks at is either in the key or hashed beside it:
        `vtype` (no two `equal` types hash differently -- checked), `marks` --
        which `__eq__` does compare, so they belong here -- and the payload,
        which the key derives from structurally. The key is coarser than `__eq__`
        in places, which only ever costs a bucket collision.

        A capsule with no `hash_fn` gives one hash to every value of its type.
        That is go-cty's own answer (`cty/set_internals.go:257-274`: "we'll just
        generate the same hash value for every value of this type, which is
        logically fine but less efficient for larger sets"), it is correct
        whatever equality the capsule defines -- including a `CtyCapsuleWithOps`
        whose `equal_fn` makes `__eq__` user-defined, where nothing generic
        *could* derive an agreeing hash -- and it replaces a `TypeError` that
        leaked the user's own class name for an unhashable payload. Supply
        `hash_fn` to get bucketing back; go-cty says the same of `HashKey`.
        """
        from pyvider.cty.types import (
            CtyCapsule,
            CtyCapsuleWithOps,
            CtyList,
            CtyMap,
            CtyObject,
            CtySet,
        )

        if isinstance(self.type, CtyCapsuleWithOps) and self.type.hash_fn:
            return self.type.hash_fn(self.value)

        if self.is_unknown or self.is_null:
            return hash((self.vtype, self.is_unknown, self.is_null, self.marks))

        if isinstance(self.vtype, CtyCapsule):
            return hash((self.vtype, self.marks))

        if isinstance(self.vtype, CtyList | CtySet | CtyMap | CtyObject):
            return hash((self.vtype, self.marks, self._canonical_sort_key()))

        return hash((self.vtype, self.is_unknown, self.is_null, self.marks, self.value))

    def equals(self, other: CtyValue[Any]) -> CtyValue[Any]:
        """Whether this equals `other`: true, false, or **unknown**.

        go-cty spells this `Value.Equals`. Unlike `==`, which must answer with a
        plain bool, this can decline to decide -- which is the only correct
        answer when the comparison depends on a value that is not yet known.
        """
        from pyvider.cty.values.equality import equals

        return equals(self, other)

    def is_wholly_known(self) -> bool:
        """False if this value, or anything nested inside it, is unknown.

        go-cty spells this `Value.IsWhollyKnown`. `is_unknown` answers only for
        the top level, so a known object with an unknown attribute reports as
        known -- which is the right answer to a different question than the one
        callers deciding "can I draw a conclusion from this value" are asking.
        """
        stack: list[Any] = [self]
        visited: set[int] = set()
        while stack:
            current = stack.pop()
            current_id = id(current)
            if current_id in visited:
                continue
            visited.add(current_id)
            if isinstance(current, CtyValue):
                if current.is_unknown:
                    return False
                if current.is_null:
                    continue
                stack.append(current.value)
            elif isinstance(current, dict):
                stack.extend(current.values())
            elif isinstance(current, (list, tuple, set, frozenset)):
                stack.extend(current)
        return True

    def has_mark(self, mark: object) -> bool:
        return mark in self.marks

    def mark(self, mark: object) -> Self:
        return evolve(self, marks=self.marks.union({mark}))

    def with_marks(self, marks_to_add: AbstractSet[Any]) -> Self:
        return evolve(self, marks=self.marks.union(marks_to_add))

    def unmark(self) -> tuple[Self, frozenset[Any]]:
        unmarked_value = evolve(self, marks=frozenset())
        return unmarked_value, self.marks

    def is_true(self) -> bool:
        from pyvider.cty.types import CtyDynamic

        if isinstance(self.vtype, CtyDynamic) and isinstance(self.value, CtyValue):
            return self.value.is_true()
        return self.value is True

    def is_false(self) -> bool:
        from pyvider.cty.types import CtyDynamic

        if isinstance(self.vtype, CtyDynamic) and isinstance(self.value, CtyValue):
            return self.value.is_false()
        return self.value is False

    def is_empty(self) -> bool:
        return not self.value if hasattr(self.value, "__len__") else False

    def with_key(self, key: str, value: Any) -> Self:
        from ..types import CtyMap

        if not isinstance(self.vtype, CtyMap):
            raise TypeError("'.with_key()' can only be used on CtyMap values.")
        if not isinstance(self.value, dict):
            raise TypeError("Internal value of CtyMap must be a dict.")
        new_dict = self.value.copy()
        new_dict[key] = value
        # validate() returns CtyValue[Any] due to .value: object limitation
        return self.vtype.validate(new_dict)  # type: ignore[no-any-return]

    def without_key(self, key: str) -> Self:
        from ..types import CtyMap

        if not isinstance(self.vtype, CtyMap):
            raise TypeError("'.without_key()' can only be used on CtyMap values.")
        if not isinstance(self.value, dict):
            raise TypeError("Internal value of CtyMap must be a dict.")
        if key not in self.value:
            return self
        new_dict = self.value.copy()
        del new_dict[key]
        # validate() returns CtyValue[Any] due to .value: object limitation
        return self.vtype.validate(new_dict)  # type: ignore[no-any-return]

    def append(self, value: Any) -> Self:
        from ..types import CtyList

        if not isinstance(self.vtype, CtyList):
            raise TypeError("'.append()' can only be used on CtyList values.")
        if not isinstance(self.value, list | tuple):
            raise TypeError("Internal value of CtyList must be a list or tuple.")
        new_list = list(self.value)
        new_list.append(value)
        # validate() returns CtyValue[Any] due to .value: object limitation
        return self.vtype.validate(new_list)  # type: ignore[no-any-return]

    def with_element_at(self, index: int, value: Any) -> Self:
        from ..types import CtyList

        if not isinstance(self.vtype, CtyList):
            raise TypeError("'.with_element_at()' can only be used on CtyList values.")
        if not isinstance(self.value, list | tuple):
            raise TypeError("Internal value of CtyList must be a list or tuple.")
        new_list = list(self.value)
        if not (-len(new_list) <= index < len(new_list)):
            raise IndexError("list index out of range")
        new_list[index] = value
        # validate() returns CtyValue[Any] due to .value: object limitation
        return self.vtype.validate(new_list)  # type: ignore[no-any-return]

    @classmethod
    def unknown(cls, vtype: CtyType[Any], value: Any = UNREFINED_UNKNOWN) -> CtyValue[Any]:
        return cls(vtype=vtype, is_unknown=True, value=value)

    @classmethod
    def null(cls, vtype: CtyType[Any]) -> CtyValue[Any]:
        return cls(vtype=vtype, is_null=True)


def _member_key(member: object) -> tuple[Any, ...]:
    """The canonical key of a container member, which need not be a CtyValue.

    `validate` normalises every member of a list, set, tuple, map or object to a
    CtyValue, but a hand-built value can hold raw Python objects, and asking one
    of those for `_canonical_sort_key` used to raise `AttributeError` -- from
    inside sorting, hashing and set de-duplication alike, and outside the error
    taxonomy. A raw member is keyed by its repr instead, which is orderable
    against every other member's key and hashable for anything at all.

    Repr is exact for anything whose repr round-trips and coarse otherwise, so a
    malformed payload can collide where `__eq__` would separate. That is the
    safe direction, and the supported way to build a value is `validate`.
    """
    if isinstance(member, CtyValue):
        return member._canonical_sort_key()
    # Ranked -1 so raw members sort ahead of every real type rank rather than
    # interleaving with them, which keeps the order deterministic.
    return (0, -1, repr(member))


# 🌊🪢🔚
