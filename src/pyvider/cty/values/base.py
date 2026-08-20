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
    cast,
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

# The type classes, bound once on first use rather than imported per call.
#
# `values` is imported before `types` in the package `__init__`, so a
# module-level import here is a cycle. The per-call `from ... import` that
# worked around it is not free: measured, a six-name one costs 684 ns against
# 4.4 ns for an already-bound global, and `__attrs_post_init__` runs on every
# single CtyValue construction. Binding once keeps the cycle broken, because
# nothing below runs at import time.
# The rank a member key carries in its first position: 0 known, 1 unknown, 2
# null, -1 a raw member `validate` never normalised. `_EXHAUSTED` outranks all
# four, so a key that has run out of members sorts after one that has not --
# go-cty's order for a sequence that is a prefix of another. `_PRESENT` is the
# matching low rank for a mapping's entries, which need a shape a sentinel can
# be compared against.
_PRESENT = 0
_EXHAUSTED: tuple[int, ...] = (3,)

_TYPES_BOUND: bool = False
_CtyDynamic: Any = None
_CtyList: Any = None
_CtyMap: Any = None
_CtyObject: Any = None
_CtySet: Any = None
_CtyTuple: Any = None
_CtyNumber: Any = None
_CtyString: Any = None
_CtyBool: Any = None
_CtyCapsule: Any = None
_CtyCapsuleWithOps: Any = None


def _bind_types() -> None:
    """Resolve the type classes into module globals, once."""
    global _TYPES_BOUND, _CtyDynamic, _CtyList, _CtyMap, _CtyObject, _CtySet, _CtyTuple
    global _CtyNumber, _CtyString, _CtyBool, _CtyCapsule, _CtyCapsuleWithOps
    from pyvider.cty.types import (
        CtyBool,
        CtyCapsule,
        CtyCapsuleWithOps,
        CtyDynamic,
        CtyList,
        CtyMap,
        CtyNumber,
        CtyObject,
        CtySet,
        CtyString,
        CtyTuple,
    )

    _CtyDynamic, _CtyList, _CtyMap, _CtyObject = CtyDynamic, CtyList, CtyMap, CtyObject
    _CtySet, _CtyTuple, _CtyNumber = CtySet, CtyTuple, CtyNumber
    _CtyString, _CtyBool, _CtyCapsule = CtyString, CtyBool, CtyCapsule
    _CtyCapsuleWithOps = CtyCapsuleWithOps
    _TYPES_BOUND = True


def _payload_pairs(left: Any, right: Any) -> tuple[tuple[Any, Any], ...] | None:
    """Two payloads compared without descending into any `CtyValue` they hold.

    A container's payload is a tuple (list, set, tuple) or a mapping (map,
    object) of `CtyValue`s, and comparing those with `==` is what put a Python
    frame on the stack for every level of nesting. Anything else is a leaf
    payload -- a string, a `Decimal`, an unknown marker -- and decides here.
    """
    if isinstance(left, tuple) and isinstance(right, tuple):
        if len(left) != len(right):
            return None
        return tuple(zip(left, right, strict=True))
    left_items = getattr(left, "items", None)
    right_items = getattr(right, "items", None)
    if left_items is not None and right_items is not None and not isinstance(left, str | bytes):
        if left.keys() != right.keys():
            return None
        return tuple((value, right[key]) for key, value in left_items())
    return () if left == right else None


@define(frozen=True, slots=True)
class CtyValue(Generic[T]):
    vtype: CtyType[T] = field()
    value: object | None = field(default=None)
    is_unknown: bool = field(default=False)
    is_null: bool = field(default=False)
    marks: frozenset[Any] = field(default=frozenset())

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
        if not _TYPES_BOUND:
            _bind_types()

        if isinstance(self.vtype, _CtyDynamic) and isinstance(self.value, CtyValue):
            object.__setattr__(self, "is_unknown", self.value.is_unknown)
            object.__setattr__(self, "is_null", self.value.is_null)

        if self.is_unknown and self.is_null:
            object.__setattr__(self, "is_null", False)
        elif self.is_null and self.value is not None and not self._dynamic_wrapper():
            # A null holds no payload -- except at `dynamic`, where the payload
            # *is* the type. Clearing it there discarded the one thing a dynamic
            # position exists to carry: `CtyDynamic().validate(null-of-string)`
            # became an untyped dynamic null, and the msgpack codec then wrote a
            # bare `c0` where go-cty writes `[type, value]`. Reading that back,
            # go-cty answers `type=dynamic` against its own `type=string`.
            object.__setattr__(self, "value", None)

    def _dynamic_wrapper(self) -> bool:
        """Whether this value is a `dynamic` standing in front of a concrete one."""
        return isinstance(self.vtype, _CtyDynamic) and isinstance(self.value, CtyValue)

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
        """This library's notion of value identity. `__hash__` and `__eq__` rest on it.

        **Not the wire order any more.** It was, until 2026-08-19, and it was an
        approximation: go-cty orders a set of composite elements by the *bytes*
        of `makeSetHashBytes`, which is a different comparison from a structural
        one -- see `pyvider.cty.values.set_order`, which does it exactly and is
        what every encoder now sorts by. What is left here is identity, which
        the hash cannot serve because it renders a number at ten significant
        digits and would merge two elements go-cty keeps apart.

        **Running out of elements ranks last, not first**, which is the
        structural echo of that byte comparison and is still the right shape for
        a key: `_EXHAUSTED` below outranks any real member, so a comparison
        reaches it only when one side has run out. Elements of a mapping key
        carry `_PRESENT` for a related reason -- a terminator has to be
        comparable with them, and a bare sentinel against a `(name, ...)` pair
        compares an int with a str and raises.

        Ranks known 0, unknown 1, null 2, which is `setRules.Less`'s order
        (`cty/set_internals.go:99-110`): it checks nullness *before* knownness,
        so an unknown sorts ahead of a null. These three were previously the
        exact inverse, and a set holding a null re-encoded with the null first
        where go-cty writes it last.

        `CtySet.validate` no longer de-duplicates with this alone. It uses
        `set_order.identity_key`, which carries the hash bucket too, because
        go-cty finds a set element by bucket before it compares anything -- so
        `0` and `-0` are two elements there and were one here. `__hash__` stays
        with this key, and must, since `__eq__` calls those two values equal.

        Total, and never raising: a member that is not a `CtyValue` is keyed by
        its repr and a mapping is ordered by `str(key)`. Only a hand-built value
        can hold either -- `validate` normalises members -- and both used to
        reach `AttributeError`/`TypeError` from here, which is the same escape
        from the error taxonomy that the bare `TypeError` in `__hash__` was.
        """
        if not _TYPES_BOUND:
            _bind_types()
        CtyBool, CtyCapsule, CtyList = _CtyBool, _CtyCapsule, _CtyList
        CtyMap, CtyNumber, CtyObject = _CtyMap, _CtyNumber, _CtyObject
        CtySet, CtyString, CtyTuple = _CtySet, _CtyString, _CtyTuple

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
            return (*key_prefix, *(_member_key(v) for v in self.value), _EXHAUSTED)

        if isinstance(self.type, CtySet) and self.value is not None and hasattr(self.value, "__iter__"):
            sorted_elements = sorted(self.value, key=_member_key)
            return (*key_prefix, *(_member_key(v) for v in sorted_elements), _EXHAUSTED)

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
                *((_PRESENT, str(k), _member_key(v)) for k, v in sorted_items),
                _EXHAUSTED,
            )

        if isinstance(self.type, CtyCapsule):
            return (*key_prefix, repr(self.value))

        # Fallback for any other type
        return (*key_prefix, repr(self.value))

    def __eq__(self, other: object) -> bool:
        """Walked, not recursed -- a value nests as deeply as its type.

        This used to compare the payloads with `==`, which for a container is a
        tuple or `FrozenDict` of `CtyValue`s and so came straight back here, one
        level down. `CtyType.equal` had the same shape and raised
        `RecursionError` on Python 3.11 for a value 400 deep; this is the same
        defect one layer up, and value equality is the hotter of the two.

        `_eq_shallow` decides everything about one node that is not a child
        comparison and hands back the children still to compare.
        """
        if not isinstance(other, CtyValue):
            return NotImplemented
        children = self._eq_shallow(other)
        if children is None:
            return False
        stack = list(children)
        while stack:
            this, that = stack.pop()
            pairs = this._eq_shallow(that)
            if pairs is None:
                return False
            stack.extend(pairs)
        return True

    def _eq_shallow(self, other: CtyValue[Any]) -> tuple[tuple[Any, Any], ...] | None:
        """This value's equality minus its children. `None` means unequal."""
        from ..types import CtyCapsuleWithOps

        # A capsule's equal_fn is written against its payload type, and a null or
        # unknown has no payload -- self.value is None or an unknown marker. It
        # was being handed those anyway, so comparing two nulls of a capsule type
        # raised AttributeError out of user code, where cty requires them to be
        # equal. Nullness, unknown-ness and marks are decided by cty; only two
        # known payloads are the capsule's business.
        both_present = not (self.is_null or self.is_unknown or other.is_null or other.is_unknown)
        if (
            isinstance(self.type, CtyCapsuleWithOps)
            and self.type.equal(other.type)
            and self.type.equal_fn
            and both_present
        ):
            # Marks are still cty's concern: a sensitive value is not equal to
            # the same payload unmarked, and __hash__ already counts them, so
            # ignoring them here made equal values hash differently.
            return () if (self.marks == other.marks and self.type.equal_fn(self.value, other.value)) else None

        if not (
            self.type.equal(other.type)
            and self.is_unknown == other.is_unknown
            and self.is_null == other.is_null
            and self.marks == other.marks
        ):
            return None
        return _payload_pairs(self.value, other.value)

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

        **Folded rather than recursed, as of 2026-08-20.** A container's payload
        hash was built by calling `hash` on each element, which came straight
        back here one level down -- the same defect `__eq__` above had, and
        leaving it while fixing `__eq__` would have been the third half-fix of
        this shape in one codebase. The walk below is an explicit post-order:
        every node's hash is computed once, after its children's, and each node
        reads theirs out of `computed` rather than asking for them.
        """
        order: list[CtyValue[Any]] = []
        stack: list[CtyValue[Any]] = [self]
        while stack:
            node = stack.pop()
            order.append(node)
            stack.extend(node._hash_descendants())
        computed: dict[int, int] = {}
        for node in reversed(order):
            computed[id(node)] = node._hash_node(computed)
        return computed[id(self)]

    def _hash_descendants(self) -> tuple[CtyValue[Any], ...]:
        """The child values this one's hash is built from, and only those.

        Mirrors the branches in `_hash_node` exactly: a null, an unknown, a
        capsule and a leaf all decide without consulting a child, so descending
        into them would compute hashes nothing reads.
        """
        if not _TYPES_BOUND:
            _bind_types()
        if self.is_unknown or self.is_null:
            return ()
        if isinstance(self.type, _CtyCapsuleWithOps) and self.type.hash_fn:
            return ()
        if isinstance(self.vtype, _CtyCapsule):
            return ()
        if not isinstance(self.vtype, _CtyList | _CtyMap | _CtyObject | _CtySet | _CtyTuple):
            return ()
        payload = self.value
        items: tuple[Any, ...] = ()
        if isinstance(payload, dict):
            items = tuple(payload.values())
        elif isinstance(payload, tuple | list | frozenset):
            items = tuple(payload)
        return tuple(item for item in items if isinstance(item, CtyValue))

    def _hash_node(self, computed: dict[int, int]) -> int:
        """This value's hash, given its children's."""
        if not _TYPES_BOUND:
            _bind_types()
        CtyCapsule, CtyCapsuleWithOps = _CtyCapsule, _CtyCapsuleWithOps
        CtyList, CtyMap, CtyObject, CtySet = _CtyList, _CtyMap, _CtyObject, _CtySet

        # Ordered before the capsule dispatch for the same reason as __eq__: a
        # null or unknown has no payload to hand a user-supplied hash_fn, and
        # doing so raised AttributeError out of their code.
        if self.is_unknown or self.is_null:
            return hash((self.vtype, self.is_unknown, self.is_null, self.marks))

        if isinstance(self.type, CtyCapsuleWithOps) and self.type.hash_fn:
            # hash_fn wins outright, as documented. Marks are deliberately not
            # folded in: __eq__ does distinguish them, and unequal values are
            # allowed to share a hash -- only the reverse would break the
            # contract.
            # `cast` because the capsule class is resolved through the lazy
            # binder above, so the isinstance narrowing carries no static type.
            return cast("int", self.type.hash_fn(self.value))

        if isinstance(self.vtype, CtyCapsule):
            return hash((self.vtype, self.marks))

        # `CtyTuple` belongs here and was missing, which is a second bug in one
        # line: a tuple's payload is a tuple of `CtyValue`s, so it fell through
        # to the leaf branch and was hashed by Python's own tuple hash. That
        # asks each element for `hash()` -- recursing, which is why this test
        # found it -- and it also skips the element-hashing the comment below
        # exists for, so two tuples holding equal capsule payloads hashed apart
        # exactly as two lists used to.
        if isinstance(self.vtype, CtyList | CtySet | CtyMap | CtyObject | _CtyTuple):
            # Hash the elements' own hashes rather than the canonical sort key.
            # That key renders a capsule payload with repr(), which for a class
            # without a defined __repr__ is its memory address -- so two lists
            # holding equal capsule payloads compared equal and hashed
            # differently, and a set kept both. Element hashing routes each
            # capsule back through its hash_fn, which is the whole point of
            # supplying one.
            return hash((self.vtype, self.marks, self._payload_hash(computed)))

        return hash((self.vtype, self.is_unknown, self.is_null, self.marks, self.value))

    def _payload_hash(self, computed: dict[int, int]) -> int:
        """A container payload's hash, built from its elements' hashes.

        An element's hash comes out of `computed` when the fold in `__hash__`
        has already produced it, which is every `CtyValue` element. Anything
        else is a raw payload member and hashes itself.
        """

        def element(item: Any) -> int:
            found = computed.get(id(item))
            return hash(item) if found is None else found

        payload = self.value
        if isinstance(payload, dict):
            # A frozenset rather than a sort: map keys are not guaranteed to be
            # mutually orderable (a malformed payload can mix str and int), and
            # sorting them raised TypeError out of __hash__.
            return hash(frozenset((key, element(item)) for key, item in payload.items()))
        if isinstance(payload, frozenset):
            return hash(tuple(sorted(element(item) for item in payload)))
        if isinstance(payload, tuple | list):
            return hash(tuple(element(item) for item in payload))
        return hash(payload)

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
