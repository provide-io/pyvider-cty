#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`hash(CtyValue)` answers for containers too, as of 2026-08-17.

`CtyValue.__hash__` used to raise a bare `TypeError` for `list`, `set`, `map`
and `object`. Bare, so it fell outside `CtyError`/`CtyFunctionError` and a
caller's `except CtyFunctionError` missed it -- which means it reached Terraform
as a provider crash rather than a diagnostic.

Ten public entry points reached it, and every one of them had the same trigger:
**a set whose element type is a container**, because that is the only shape that
makes something hash a container. `set(object({...}))` is Terraform's
nested-block-set type, so this was the common case rather than a corner. One
test per entry point below, so that a regression names the entry point a caller
would have used rather than the internal call site it happened to die at.

The msgpack round-trip is here for the same reason: the shape survives
serialization, so this was reachable from decoded wire data and not only from
values a test constructed.

go-cty hashes containers without hesitation -- `makeSetHashBytes`
(`cty/set_internals.go:144-278`) serializes a whole value and crc32s it. The fix
is the same idea: hash `_canonical_sort_key()`, which `CtySet.validate` already
de-duplicated with. Having two notions of element identity and only one of them
working is what produced a library that could *build* a set of lists and then
refuse to compare one.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import (
    CtyCapsule,
    CtyCapsuleWithOps,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyValue,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.exceptions import CtyError
from pyvider.cty.functions import (
    contains,
    distinct,
    equal,
    lookup,
    not_equal,
    setunion,
)
from pyvider.cty.marks import CtyMark
from pyvider.cty.walk import deep_values

S = CtyString()
LIST_OF_STRING = CtyList(element_type=S)
SET_OF_LIST = CtySet(element_type=LIST_OF_STRING)
MAP_OF_LIST = CtyMap(element_type=LIST_OF_STRING)
NESTED_BLOCK = CtySet(element_type=CtyObject(attribute_types={"name": S}))

SENSITIVE = CtyMark("sensitive")


def set_of_lists() -> CtyValue[Any]:
    """`set(list(string))` -- the smallest shape that triggered every path."""
    return SET_OF_LIST.validate([["x"], ["y"]])


def verdict(result: CtyValue[Any]) -> object:
    return "unknown" if result.is_unknown else result.value


class TestHashItself:
    """The root: `hash()` on each of the four types that used to refuse."""

    @pytest.mark.parametrize(
        ("label", "value"),
        [
            ("list", LIST_OF_STRING.validate(["a"])),
            ("set", CtySet(element_type=S).validate(["a"])),
            ("map", CtyMap(element_type=S).validate({"k": "v"})),
            ("object", CtyObject(attribute_types={"a": S}).validate({"a": "x"})),
            ("empty list", LIST_OF_STRING.validate([])),
            ("set of lists", set_of_lists()),
            ("nested-block set", NESTED_BLOCK.validate([{"name": "a"}])),
            ("null list", CtyValue.null(LIST_OF_STRING)),
            ("unknown list", CtyValue.unknown(LIST_OF_STRING)),
            ("dynamic wrapping a list", CtyDynamic().validate(["a"])),
        ],
    )
    def test_every_container_shape_hashes(self, label: str, value: CtyValue[Any]) -> None:
        assert isinstance(hash(value), int), label

    def test_equal_containers_hash_alike(self) -> None:
        """The hash/eq contract, on the shape that could not previously be asked.

        Element order differs between the two arguments on purpose: a set has no
        order of its own, so two spellings of the same set must be one member of
        a Python set.
        """
        one, two = SET_OF_LIST.validate([["x"], ["y"]]), SET_OF_LIST.validate([["y"], ["x"]])

        assert one == two
        assert hash(one) == hash(two)
        assert len({one, two}) == 1

    def test_marks_are_hashed_because_eq_compares_them(self) -> None:
        """`__eq__` compares `marks`, so `__hash__` must not ignore them.

        Not the other way round: a hash that ignored marks would still be
        *correct* (equal values would still hash alike), just coarser. Including
        them keeps a marked and an unmarked container in separate buckets, which
        is what the scalar path has always done.
        """
        plain = LIST_OF_STRING.validate(["a"])
        marked = plain.mark(SENSITIVE)

        assert plain != marked
        assert hash(plain) != hash(marked)


class TestEntryPoints:
    """One per public entry point that reached the raise."""

    def test_value_equals_on_a_set_of_containers(self) -> None:
        """`CtyValue.equals` -> `_equals_set`, which built a `frozenset`."""
        assert verdict(set_of_lists().equals(set_of_lists())) is True
        assert verdict(set_of_lists().equals(SET_OF_LIST.validate([["x"]]))) is False

    def test_stdlib_equal(self) -> None:
        """`equal` is `Value.Equals` reached through the stdlib."""
        assert verdict(equal(set_of_lists(), set_of_lists())) is True

    def test_stdlib_not_equal(self) -> None:
        assert verdict(not_equal(set_of_lists(), set_of_lists())) is False

    def test_stdlib_setunion(self) -> None:
        """`setunion` built a `frozenset` of the elements, one and many args."""
        assert len(setunion(set_of_lists()).value) == 2
        assert len(setunion(set_of_lists(), set_of_lists()).value) == 2

    def test_stdlib_contains(self) -> None:
        """A list *of sets of lists* -- the container has to be the needle."""
        haystack = CtyList(element_type=SET_OF_LIST).validate([[["x"]]])

        assert contains(haystack, SET_OF_LIST.validate([["x"]])).value is True
        assert contains(haystack, SET_OF_LIST.validate([["z"]])).value is False

    def test_stdlib_distinct(self) -> None:
        """`distinct` de-duplicates with a Python `set`, so it hashed elements."""
        duplicated = CtyList(element_type=LIST_OF_STRING).validate([["a"], ["a"], ["b"]])

        assert len(distinct(duplicated).value) == 2

    def test_stdlib_lookup_with_a_container_key(self) -> None:
        """A dynamic key holding a list: `lookup` hashed it to probe the map.

        The assertion is about the *kind* of answer rather than the answer.
        go-cty's `LookupFunc` declares its key as `cty.String`, so refusing a
        list key is legitimate; refusing it with a bare `TypeError` out of `hash`
        was not, because that is outside `CtyError` and a caller's
        `except CtyFunctionError` missed it.
        """
        with pytest.raises(CtyError):
            lookup(
                CtyMap(element_type=S).validate({"k": "v"}),
                CtyDynamic().validate(["a"]),
                S.validate("fallback"),
            )

    def test_object_holding_a_set_of_containers_equals_itself(self) -> None:
        """The trigger can be nested arbitrarily deep inside a value."""
        wrapper = CtyObject(attribute_types={"s": SET_OF_LIST})
        value = wrapper.validate({"s": [["x"]]})

        assert verdict(value.equals(value)) is True

    def test_membership_on_a_map(self) -> None:
        """`CtyValue.__contains__` delegates to the payload dict, which hashes."""
        target = MAP_OF_LIST.validate({"m": ["x"]})

        assert set_of_lists() not in target

    def test_without_key_on_a_map(self) -> None:
        """`without_key` probes `key not in self.value` before copying."""
        target = MAP_OF_LIST.validate({"m": ["x"]})

        assert target.without_key(set_of_lists()) is target

    def test_deep_values_paths_go_into_a_set(self) -> None:
        """A set element is its own key, so a `KeyStep` holds a whole CtyValue.

        `.provide/GO-CTY-PARITY.md` closes go-cty's `PathSet` on the grounds
        that `set[CtyPath]` is the same thing once `CtyPath` is frozen. That was
        false for any set of containers until this fix, and `deep_values` hands
        out exactly those paths.
        """
        paths = {path for path, _ in deep_values(set_of_lists())}

        # root, two set elements, and the one string inside each of them.
        assert len(paths) == 5
        assert paths == {path for path, _ in deep_values(SET_OF_LIST.validate([["y"], ["x"]]))}


class TestReachableFromTheWire:
    def test_a_msgpack_round_trip_produces_the_same_shape(self) -> None:
        """Why this mattered: the trigger is decodable, not just constructable.

        `set(object({name=string}))` is what Terraform sends for a
        nested block set, so a provider comparing prior state against planned
        state hit this without ever building a value by hand.
        """
        decoded = cty_from_msgpack(
            cty_to_msgpack(NESTED_BLOCK.validate([{"name": "a"}]), NESTED_BLOCK), NESTED_BLOCK
        )

        assert verdict(equal(decoded, NESTED_BLOCK.validate([{"name": "b"}]))) is False
        assert verdict(equal(decoded, NESTED_BLOCK.validate([{"name": "a"}]))) is True


class TestSetMembershipIsBucketedButNotDecidedByHash:
    """`_equals_set` groups candidates by hash, then verifies with `Equals`.

    That is go-cty's own arrangement (`cty/set_internals.go`), and it is only
    possible here because containers hash at all now: the pairwise scan it
    replaces cost 1.3 s for two equal 1000-element sets, on the comparison a
    provider makes for every nested block set on every plan.

    The hash is a hint, never the verdict. `Equals` calls some values equal that
    hash apart, so a bucket miss must re-check the whole set rather than
    conclude. Dated 2026-08-17.
    """

    def test_two_equal_sets_of_containers_agree(self) -> None:
        many = [[str(i)] for i in range(200)]

        assert verdict(SET_OF_LIST.validate(many).equals(SET_OF_LIST.validate(list(reversed(many))))) is True

    def test_a_bucket_miss_falls_back_rather_than_concluding(self) -> None:
        """Nulls of two types are equal in cty but do not hash alike.

        `set(dynamic)` is the one element type that can hold both, and only by
        hand -- `validate` de-duplicates them to one, since both have canonical
        key `(2,)`. Deciding from the hash alone would answer `false` here, which
        is the answer cty explicitly rejects: "Nulls are always equal, regardless
        of type".
        """
        set_of_dynamic = CtySet(element_type=CtyDynamic())
        null_string = CtyValue(vtype=set_of_dynamic, value=(CtyValue.null(S),))
        null_number = CtyValue(vtype=set_of_dynamic, value=(CtyValue.null(CtyNumber()),))

        assert verdict(null_string.equals(null_number)) is True

    def test_a_member_whose_own_hash_fn_raises_is_still_compared(self) -> None:
        """A capsule's `hash_fn` is user code, and it is the last thing that can refuse.

        Everything else hashes now, so this is the only remaining way for `hash`
        to raise from inside a set comparison. It must degrade to a scan: the
        caller asked whether two sets are equal, not whether their members are
        hashable, and letting the user's `TypeError` out of `equals` would be the
        same escape from the taxonomy this whole change removes.
        """

        def broken_hash(_payload: Any) -> int:
            raise TypeError("this hash_fn is broken")

        capsule = CtyCapsuleWithOps(
            "Payload", Payload, hash_fn=broken_hash, equal_fn=lambda a, b: bool(a.n == b.n)
        )
        sets = CtySet(element_type=capsule)

        assert verdict(sets.validate([Payload(1)]).equals(sets.validate([Payload(1)]))) is True
        assert verdict(sets.validate([Payload(1)]).equals(sets.validate([Payload(2)]))) is False


class TestUnknownSetIdentity:
    """ "Two unknown values are not equivalent for the sake of set membership."

    go-cty says so in `cty/set_internals.go:52-68`, and it is the reason
    `CtySet.validate` holds unknowns in a list that is never de-duplicated. A
    hash that made two unknowns interchangeable would silently claim a
    cardinality the value does not have: `toset([a.id, b.id])` at plan time is
    two elements, not one, and that count reaches Terraform.
    """

    def test_two_unknowns_stay_two_elements(self) -> None:
        both = CtySet(element_type=S).validate([CtyValue.unknown(S), CtyValue.unknown(S)])

        assert len(both.value) == 2
        assert isinstance(hash(both), int)

    def test_a_set_holding_an_unknown_element_is_undecided(self) -> None:
        """Measured against go-cty on 2026-08-17: `{known}` is the guard.

        go-cty declines only for an element that is unknown at *its own* top
        level (`cty/value_ops.go:332-357`). Anything shallower it decides.
        """
        with_unknown = CtySet(element_type=S).validate(["a", CtyValue.unknown(S)])

        assert verdict(with_unknown.equals(CtySet(element_type=S).validate(["a", "b"]))) == "unknown"

    def test_an_element_that_merely_contains_an_unknown_is_decided_false(self) -> None:
        """go-cty answers a definite `false` here, and used to disagree with us.

        `Equivalent` is `Equals(...) == true`, so an element containing an
        unknown is equivalent to nothing -- which makes the sets unequal rather
        than undecided. Verified against the soup-go harness on 2026-08-17 for
        `set(list(string))` and `set(object({name=string}))`, both directions.
        """
        nested = SET_OF_LIST.validate([[CtyValue.unknown(S)]])

        assert verdict(nested.equals(nested)) is False

        blocks = NESTED_BLOCK.validate([{"name": CtyValue.unknown(S)}])
        assert verdict(blocks.equals(blocks)) is False


class Payload:
    """A capsule payload with an ordinary identity-based equality."""

    def __init__(self, n: int) -> None:
        self.n = n


class Unhashable:
    """A capsule payload that refuses to be hashed, as a `dict` does."""

    __hash__ = None  # type: ignore[assignment]


class TestCapsules:
    """A capsule with no `hash_fn` hashes as go-cty's capsule does.

    go-cty (`cty/set_internals.go:257-274`): "If there isn't an explicit hash
    implementation then we'll just generate the same hash value for every value
    of this type, which is logically fine but less efficient for larger sets
    because we'll have to bucket all values together and scan over them with
    Equals to determine set membership."

    One hash per type is the only choice that is correct for *any* equality the
    capsule defines, which matters because a `CtyCapsuleWithOps` with an
    `equal_fn` makes `__eq__` user-defined and nothing generic could derive an
    agreeing hash. It also replaces a `TypeError` that leaked the payload
    class's own name ("unhashable type: 'Unhashable'") out of pyvider.
    """

    def test_a_plain_capsule_hashes_and_still_separates_its_values(self) -> None:
        capsule = CtyCapsule("Payload", Payload)
        one, two = capsule.validate(Payload(1)), capsule.validate(Payload(2))

        assert hash(one) == hash(two)
        assert one != two
        assert len({one, two}) == 2

    def test_an_unhashable_payload_no_longer_escapes_as_a_typeerror(self) -> None:
        capsule = CtyCapsule("Unhashable", Unhashable)

        assert isinstance(hash(capsule.validate(Unhashable())), int)

    def test_a_capsule_with_equal_fn_but_no_hash_fn_stays_consistent(self) -> None:
        """`equal_fn` owns `__eq__`, so the hash must not contradict it."""
        capsule = CtyCapsuleWithOps("Payload", Payload, equal_fn=lambda a, b: bool(a.n == b.n))
        one, other_one = capsule.validate(Payload(1)), capsule.validate(Payload(1))

        assert one == other_one
        assert hash(one) == hash(other_one)
        assert len({one, other_one}) == 1

    def test_hash_fn_still_wins_when_supplied(self) -> None:
        capsule = CtyCapsuleWithOps("Payload", Payload, hash_fn=lambda v: int(v.n))

        assert hash(capsule.validate(Payload(7))) == 7


class TestMalformedPayloadsDoNotEscapeTheTaxonomy:
    """A hand-built payload holding raw Python objects hashes rather than raising.

    `validate` normalises every member to a CtyValue, so only hand construction
    produces these -- but `_canonical_sort_key` used to raise `AttributeError`
    on them, which is the same escape from the taxonomy that the bare
    `TypeError` was. A raw member is keyed by its repr instead.
    """

    @pytest.mark.parametrize(
        ("label", "value"),
        [
            ("list of raw", CtyValue(vtype=LIST_OF_STRING, value=("raw",))),
            ("map of raw", CtyValue(vtype=CtyMap(element_type=S), value={"k": "raw"})),
            (
                "map with keys of mixed type",
                CtyValue(vtype=CtyMap(element_type=S), value={1: S.validate("a"), "b": S.validate("b")}),
            ),
            ("set of raw", CtyValue(vtype=CtySet(element_type=S), value=("raw",))),
        ],
    )
    def test_hashing_a_malformed_payload_answers(self, label: str, value: CtyValue[Any]) -> None:
        assert isinstance(hash(value), int), label

    def test_a_string_keyed_mapping_keeps_its_previous_key(self) -> None:
        """Ordering by `str(name)` must be the identical order for real payloads.

        A mapping's keys are attribute or element names and so are strings; the
        looser sort exists only so a malformed payload cannot raise.
        """
        obj = CtyObject(attribute_types={"b": S, "a": S}).validate({"a": "1", "b": "2"})

        assert [name for name, _ in obj._canonical_sort_key()[2:]] == ["a", "b"]


def test_a_number_hashes_as_before() -> None:
    """The scalar path is untouched; it was never the problem."""
    assert hash(CtyNumber().validate(1)) == hash(CtyNumber().validate(1))
    assert hash(CtyNumber().validate("1.0")) == hash(CtyNumber().validate(1))


# 🌊🪢🔚
