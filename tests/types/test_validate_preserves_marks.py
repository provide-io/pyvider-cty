#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`validate()` must not discard the marks carried by its input.

Marks are how Terraform tracks sensitivity. A validate that unwraps an incoming
CtyValue and rebuilds a fresh one drops the flag, so a sensitive value silently
becomes non-sensitive simply by being validated -- or by being placed inside a
collection, since collections validate each element through its element type.

The break these tests catch: any `validate` implementation that reads
`value.value` off a marked CtyValue and returns a newly constructed result
without restoring `value.marks`.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.marks import CtyMark, collect_marks_deep
from pyvider.cty.validation import clear_recursion_context, get_recursion_context

SENSITIVE = CtyMark("sensitive")


def marked_string() -> CtyValue[Any]:
    return CtyString().validate("hunter2").mark(SENSITIVE)


PRIMITIVES: list[tuple[str, CtyType[Any], object]] = [
    ("string", CtyString(), "hunter2"),
    ("number", CtyNumber(), 42),
    ("bool", CtyBool(), True),
]


@pytest.mark.parametrize(("name", "cty_type", "raw"), PRIMITIVES, ids=[p[0] for p in PRIMITIVES])
def test_primitive_validate_preserves_marks(name: str, cty_type: CtyType[Any], raw: object) -> None:
    marked = cty_type.validate(raw).mark(SENSITIVE)

    assert cty_type.validate(marked).marks == frozenset({SENSITIVE})


def test_list_preserves_marks_on_its_elements() -> None:
    result = CtyList(element_type=CtyString()).validate([marked_string()])

    assert result.value[0].marks == frozenset({SENSITIVE})


def test_set_hoists_marks_from_its_elements_onto_itself() -> None:
    """A set carries its elements' marks; the elements themselves carry none.

    go-cty's `SetVal` deep-unmarks every element and applies the union to the
    set (cty/value_init.go), and its set internals panic outright on hashing a
    marked element (cty/set_internals.go). The reason is mechanical: de-dup keys
    on the element's value, which is mark-blind, so a sensitive element that
    collides with an equal unmarked one is silently overwritten -- see
    `test_set_dedup_keeps_the_mark_of_the_element_it_drops`.
    """
    result = CtySet(element_type=CtyString()).validate([marked_string()])

    assert result.marks == frozenset({SENSITIVE})
    assert [e.marks for e in result.value] == [frozenset()]


def test_set_dedup_keeps_the_mark_of_the_element_it_drops() -> None:
    """The case that makes storing marks on set elements untenable.

    Two elements equal but for their marks de-dup to one, and whichever loses
    takes its mark with it. Hoisting means the survivor's identity no longer
    decides whether the set is sensitive.
    """
    result = CtySet(element_type=CtyString()).validate(
        [CtyString().validate("a").mark(SENSITIVE), CtyString().validate("a")]
    )

    assert len(result.value) == 1
    assert result.marks == frozenset({SENSITIVE})


def test_set_hoists_marks_from_deep_inside_an_element() -> None:
    """`SetVal` uses UnmarkDeep, not a shallow unmark.

    The element type is dynamic only so that the mark sits one level down from
    the set. The docstring used to claim a set of lists was "unsupported"
    because set elements "have to be hashable"; that was never true of
    `CtySet.validate`, which de-duplicates by canonical sort key, and since
    2026-08-17 it is not true of `hash` either.
    """
    result = CtySet(element_type=CtyDynamic()).validate([CtyDynamic().validate(marked_string())])

    assert result.marks == frozenset({SENSITIVE})
    assert [e.marks for e in result.value] == [frozenset()]


def test_map_preserves_marks_on_its_values() -> None:
    result = CtyMap(element_type=CtyString()).validate({"k": marked_string()})

    assert result.value["k"].marks == frozenset({SENSITIVE})


def test_tuple_preserves_marks_on_its_elements() -> None:
    result = CtyTuple(element_types=(CtyString(),)).validate([marked_string()])

    assert result.value[0].marks == frozenset({SENSITIVE})


def test_object_preserves_marks_on_its_attributes() -> None:
    """CtyObject already did this; the test pins the behaviour against regression."""
    result = CtyObject(attribute_types={"a": CtyString()}).validate({"a": marked_string()})

    assert result.value["a"].marks == frozenset({SENSITIVE})


def test_dynamic_preserves_marks_on_the_wrapped_value() -> None:
    """CtyDynamic wraps rather than replaces, so the mark lands at both levels.

    The wrapper is sensitive because what it wraps is, and the wrapped value
    keeps its own mark. Collecting marks deeply unions them back to one.
    """
    result = CtyDynamic().validate(marked_string())

    assert result.marks == frozenset({SENSITIVE})
    assert result.value.marks == frozenset({SENSITIVE})


def test_nested_collection_preserves_marks_at_depth() -> None:
    inner = CtyList(element_type=CtyString())
    result = CtyList(element_type=inner).validate([inner.validate([marked_string()])])

    assert result.value[0].value[0].marks == frozenset({SENSITIVE})


def test_validate_does_not_invent_marks() -> None:
    """An unmarked input must stay unmarked."""
    assert CtyString().validate("plain").marks == frozenset()
    assert CtyList(element_type=CtyString()).validate(["plain"]).value[0].marks == frozenset()


def test_marks_survive_a_collection_round_trip() -> None:
    """The mark reaches the element, and re-validating the collection keeps it."""
    lst = CtyList(element_type=CtyString())
    once = lst.validate([marked_string()])
    twice = lst.validate(once)

    assert twice.value[0].marks == frozenset({SENSITIVE})


class TestDeepMarkMemo:
    """The memo, and the contract it depends on.

    `collect_marks_deep` is asked about every argument of every stdlib call, so
    it memoizes on the value. Without that memo the cost is linear *per call*:
    a 20k-entry map took 2.7 ms on every `length()`, a 96,000% regression.

    So the memo is only taken when the walk proves the whole subtree immutable.
    Freezing an attrs class freezes the reference to `value`, not what it points
    at, and maps and objects hold a plain dict.

    That gate was removed once, for speed, on the stated grounds that nothing in
    the workspace mutates a payload in place. It was asserted without checking
    and was false: `pyvider` does it in three places, and the consequence was a
    value that had become sensitive going on answering "not sensitive" -- and
    only when something had asked about its marks earlier, so identical code
    gave different answers depending on what had run before it.

    The cost is real and falls on maps and objects, which re-walk per call. The
    way to recover it is to make those payloads genuinely immutable -- a `dict`
    subclass that refuses mutation keeps every `isinstance(x, dict)` check
    working -- not to memoize something that can change.
    """

    def test_the_memo_is_taken(self) -> None:
        """What keeps stdlib calls off an O(n) walk per argument."""
        value = CtyList(element_type=CtyString()).validate(["a", "b"])

        assert value._deep_marks is None
        assert collect_marks_deep(value) == frozenset()
        assert value._deep_marks == frozenset()

    def test_a_mapping_payload_is_memoized_because_it_is_frozen(self) -> None:
        """Map and object payloads are `FrozenDict`, so the memo is safe.

        They were briefly excluded, since a plain dict can change behind a memo.
        That was correct but cost a full re-walk on every stdlib call -- 12 ms
        for a 20k-entry map, and every Terraform resource is an object. The
        invariant is now enforced rather than assumed.
        """
        m = CtyMap(element_type=CtyString()).validate({"k": "v"})

        collect_marks_deep(m)

        assert m._deep_marks == frozenset()

    def test_marks_present_at_the_first_ask_are_memoized(self) -> None:
        inner = CtyList(element_type=CtyString())
        value = inner.validate([marked_string()])

        assert collect_marks_deep(value) == frozenset({SENSITIVE})
        assert value._deep_marks == frozenset({SENSITIVE})

    def test_evolving_a_value_does_not_carry_the_memo_across(self) -> None:
        """`mark`, `with_marks` and `unmark` all evolve a new instance.

        This is what makes the memo safe for every supported operation: the
        answer is recomputed for the new value rather than inherited from the
        old one.
        """
        value = CtyString().validate("x")
        collect_marks_deep(value)
        assert value._deep_marks == frozenset()

        marked = value.mark(SENSITIVE)

        assert marked._deep_marks is None
        assert collect_marks_deep(marked) == frozenset({SENSITIVE})

    def test_a_payload_cannot_be_mutated_behind_the_memo(self) -> None:
        """The stale memo is prevented by making the mutation impossible.

        With a memo over a mutable payload, a value that had become sensitive
        went on answering "not sensitive" -- and only when something had asked
        about its marks earlier, so identical code gave different answers
        depending on what had run before it. Refusing the mutation turns a
        silent declassification into a loud error at the point of the mistake.
        """
        m = CtyMap(element_type=CtyString()).validate({"k": "public"})
        assert collect_marks_deep(m) == frozenset()

        with pytest.raises(TypeError, match="immutable"):
            m.value["k"] = marked_string()

        assert collect_marks_deep(m) == frozenset()

    def test_a_raw_payload_is_still_not_memoized(self) -> None:
        """A hand-built value can hold a plain dict, which really can change."""
        value = CtyValue(vtype=CtyMap(element_type=CtyString()), value={"k": marked_string()})

        assert collect_marks_deep(value) == frozenset({SENSITIVE})
        assert value._deep_marks is None


class TestMarksSurviveTheRecursionGuard:
    """The recursion guard's early exits must preserve marks too.

    `with_recursion_detection` returns an unknown value when it stops
    validation, and those returns bypassed the mark re-application on the
    normal path. A sensitive value that trips the guard came back as a plain
    unmarked unknown, which is the same silent declassification the rest of
    this module exists to prevent -- just on the failure path.

    The break these tests catch: an early `return CtyValue.unknown(self)` in
    the guard that does not carry the input's marks.
    """

    def setup_method(self) -> None:
        clear_recursion_context()
        # RecursionContext.reset() deliberately keeps the configured limit, so
        # lowering it here would leak into every later test in the process.
        self._original_max_depth = get_recursion_context().max_depth_allowed

    def teardown_method(self) -> None:
        get_recursion_context().max_depth_allowed = self._original_max_depth
        clear_recursion_context()

    def _stop_validation_at(self, depth: int) -> None:
        clear_recursion_context()
        get_recursion_context().max_depth_allowed = depth

    def test_guard_stopping_at_the_top_level_keeps_marks(self) -> None:
        list_type = CtyList(element_type=CtyString())
        marked = list_type.validate(["a"]).mark(SENSITIVE)

        self._stop_validation_at(0)
        result = list_type.validate(marked)

        assert result.is_unknown
        assert result.marks == frozenset({SENSITIVE})

    def test_guard_stopping_in_a_nested_call_keeps_marks(self) -> None:
        """Exercises the post-validation stop check, not the pre-check.

        The payload is a list rather than a tuple so `CtyList.validate` cannot
        take its already-validated fast path: the outer call has to descend,
        and the guard trips on the inner one.
        """
        inner = CtyList(element_type=CtyString())
        outer = CtyList(element_type=inner)
        marked = CtyValue(vtype=outer, value=[["a"]], marks=frozenset({SENSITIVE}))

        self._stop_validation_at(1)
        result = outer.validate(marked)

        assert result.is_unknown
        assert result.marks == frozenset({SENSITIVE})

    def test_guard_keeps_a_mark_carried_only_by_a_set_element(self) -> None:
        """A set's payload is a frozenset, not a tuple.

        Collecting nested marks by matching on `tuple` and `dict` alone walks
        straight past every set, so the one container whose payload type is
        unusual is also the one that silently declassifies. The payload is built
        directly here because `CtySet.validate` now hoists element marks onto
        the set -- which would hide exactly the case this pins.
        """
        set_type = CtySet(element_type=CtyString())
        seed = CtyValue(vtype=set_type, value=frozenset({marked_string()}))

        self._stop_validation_at(0)
        result = set_type.validate(seed)

        assert result.is_unknown
        assert result.marks == frozenset({SENSITIVE})

    def test_marks_are_collected_once_and_memoized(self) -> None:
        """The unwind must not re-walk the subtree at every ancestor frame.

        Every frame above the one that trips the guard also returns an unknown
        carrying the input's marks. If each re-walked its own subtree the abort
        path would be O(depth x size) -- on the very input whose size or depth
        is why validation was abandoned.
        """
        from pyvider.cty.marks import collect_marks_deep

        inner = CtyList(element_type=CtyString())
        seed = inner.validate([marked_string()])
        assert seed._deep_marks is None

        assert collect_marks_deep(seed) == frozenset({SENSITIVE})
        assert seed._deep_marks == frozenset({SENSITIVE})

        outer = CtyList(element_type=inner)
        self._stop_validation_at(1)
        assert outer.validate([seed]).marks == frozenset({SENSITIVE})

    def test_a_recursion_error_from_shallow_code_is_not_swallowed(self) -> None:
        """The guard owns depth failures, not every RecursionError beneath it.

        A capsule's converter blowing its own stack two levels in is a broken
        input, and turning it into an unknown makes it indistinguishable from a
        legitimately undecided one.
        """
        from pyvider.cty import CtyCapsule

        class Boom:
            pass

        def explode(_: object) -> Boom:
            return explode(_)

        capsule = CtyCapsule("Boom", Boom)
        object.__setattr__(capsule, "validate", explode)

        clear_recursion_context()
        with pytest.raises(RecursionError):
            CtyList(element_type=capsule).validate([object()])

    def test_guard_keeps_marks_carried_by_a_raw_list_input(self) -> None:
        """The input is a plain list holding an already-marked value.

        On a stop path there is no validated result to read marks off, so they
        have to come from the input -- and `validate` is routinely handed raw
        Python containers rather than a CtyValue.
        """
        inner = CtyList(element_type=CtyString())
        outer = CtyList(element_type=inner)

        self._stop_validation_at(1)
        result = outer.validate([inner.validate([marked_string()])])

        assert result.is_unknown
        assert result.marks == frozenset({SENSITIVE})

    def test_guard_keeps_marks_carried_by_a_raw_dict_input(self) -> None:
        """Same as the list case, for the mapping side of the walk."""
        obj = CtyObject(attribute_types={"a": CtyString()})

        self._stop_validation_at(0)
        result = obj.validate({"a": marked_string()})

        assert result.is_unknown
        assert result.marks == frozenset({SENSITIVE})

    def test_collecting_marks_terminates_on_a_cyclic_raw_input(self) -> None:
        """The collector runs on the path a cycle reaches, so it must survive one."""
        from pyvider.cty.marks import collect_marks_deep

        cyclic: list[Any] = [marked_string()]
        cyclic.append(cyclic)

        assert collect_marks_deep(cyclic) == frozenset({SENSITIVE})

    def test_collecting_marks_does_not_recurse_on_deep_input(self) -> None:
        """A recursive collector would raise while salvaging marks from the
        very value whose depth triggered the stop."""
        from pyvider.cty.marks import collect_marks_deep

        nested: Any = marked_string()
        for _ in range(5_000):
            nested = [nested]

        assert collect_marks_deep(nested) == frozenset({SENSITIVE})


class TestFixesThatHadNoTest:
    """Each of these failed when its fix was reverted, and not before.

    A review found four round-four fixes that could be reverted with the whole
    suite still green -- including the one that let a marked value reach the
    wire. A fix without a test is a fix that will be undone by someone tidying
    up, so each of them is pinned here.
    """

    def test_a_marked_unknown_inside_a_container_is_not_serialized(self) -> None:
        """A marked unknown element must not slip past the mark check.

        The original bug: the container was flagged unknown *by* its element,
        and an unknown encodes to a marker without the encoder descending, so
        the per-level mark check never saw the mark and it reached the wire.

        Since 2026-08-17 the container stays known, so the encoder descends and
        the per-level check meets the mark directly. Two different routes to the
        same refusal, and the refusal is the point -- which is why the assertion
        on the container's own flag is inverted here while the `raises` below is
        untouched.
        """
        from pyvider.cty.codec import cty_to_msgpack
        from pyvider.cty.exceptions import CtyMarksSerializationError

        for cty_type, raw in (
            (CtyList(element_type=CtyString()), [CtyValue.unknown(CtyString()).mark(SENSITIVE)]),
            (CtyMap(element_type=CtyString()), {"a": CtyValue.unknown(CtyString()).mark(SENSITIVE)}),
            (CtyTuple(element_types=(CtyString(),)), [CtyValue.unknown(CtyString()).mark(SENSITIVE)]),
        ):
            value = cty_type.validate(raw)
            assert not value.is_unknown, "a container holding an unknown element is itself known"
            with pytest.raises(CtyMarksSerializationError):
                cty_to_msgpack(value, cty_type)

    def test_a_hand_built_set_does_not_keep_marked_elements(self) -> None:
        """The pass-through returned such a set untouched, so de-duplication
        could later drop the mark with the element that lost."""
        set_type = CtySet(element_type=CtyString())
        hand_built = CtyValue(vtype=set_type, value=frozenset({marked_string()}))

        result = set_type.validate(hand_built)

        assert result.marks == frozenset({SENSITIVE})
        assert [e.marks for e in result.value] == [frozenset()]

    def test_equality_against_an_unknown_of_dynamic_type_is_undecided(self) -> None:
        """What `cty_from_msgpack` produces for every not-yet-known dynamic
        attribute Terraform sends. go-cty answers unknown; this answered False."""
        assert CtyString().validate("x").equals(CtyValue.unknown(CtyDynamic())).is_unknown
        assert CtyValue.unknown(CtyDynamic()).equals(CtyString().validate("x")).is_unknown

    def test_contains_matches_a_null_of_a_different_type(self) -> None:
        """`==` requires matching types; `equals` treats nulls of any type as
        equal, as go-cty does. The `==` shortcut disagreed for exactly these."""
        from pyvider.cty.functions import contains

        collection = CtyList(element_type=CtyDynamic()).validate([CtyValue.null(CtyString())])

        result = contains(collection, CtyValue.null(CtyNumber()))

        assert not result.is_unknown
        assert result.value is True

    def test_a_marked_element_does_not_change_what_contains_answers(self) -> None:
        """The answer must depend on the data, not on its sensitivity.

        `_strip` could not descend into a container flagged unknown by one of
        its elements, so the marked element survived into the comparison and
        `CtyValue.__eq__` -- which counts marks -- reported a miss.
        """
        from pyvider.cty.functions import contains

        list_type = CtyList(element_type=CtyString())
        needle = CtyString().validate("a")
        plain = list_type.validate(["a", CtyValue.unknown(CtyString())])
        marked = list_type.validate([marked_string_named("a"), CtyValue.unknown(CtyString())])

        assert contains(plain, needle).value is True
        assert contains(marked, needle).value is True
        assert SENSITIVE in contains(marked, needle).marks

    def test_a_frozen_payload_refuses_the_in_place_merge_operator(self) -> None:
        """`|=` dispatches to dict.__ior__ in C and skipped every override.

        The payload is bound to a local first, deliberately. Writing
        `value.value |= {...}` re-assigns the attribute and so is refused by
        attrs' frozen class regardless -- the test would pass with the hole
        wide open. Mutating the payload object itself is the real attack, and
        the one that silently poisoned the deep-mark memo.
        """
        value = CtyObject(attribute_types={"a": CtyString()}).validate({"a": "public"})
        assert collect_marks_deep(value) == frozenset()

        payload = value.value

        with pytest.raises(TypeError, match="immutable"):
            payload |= {"a": marked_string()}

        assert collect_marks_deep(value) == frozenset(), "memo must still be right"

    def test_a_stripped_payload_is_frozen_too(self) -> None:
        """`_strip` memoizes and hands every caller the same object, so a plain
        dict payload there reintroduced the mutable shared state FrozenDict
        exists to prevent."""
        from pyvider.cty.marks import _strip
        from pyvider.cty.values.frozen import FrozenDict

        value = CtyObject(attribute_types={"a": CtyString()}).validate({"a": marked_string()})

        stripped = _strip(value)

        assert isinstance(stripped.value, FrozenDict)
        with pytest.raises(TypeError, match="immutable"):
            stripped.value["b"] = "tampered"


def marked_string_named(text: str) -> CtyValue[Any]:
    return CtyString().validate(text).mark(SENSITIVE)
