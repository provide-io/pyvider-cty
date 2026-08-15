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
from pyvider.cty.marks import CtyMark
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

    The element type is dynamic rather than a collection because set elements
    have to be hashable, and a set of lists is unsupported for that reason --
    which is separate from marks.
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
