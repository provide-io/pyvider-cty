#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Stdlib functions must carry their arguments' marks through to the result.

go-cty enforces this structurally in the `cty/function` framework: a parameter
declared without `AllowMarked` has its marks stripped before `Impl` runs, and
the union of every argument's marks is re-applied to the result. Marks are how
Terraform tracks sensitivity, so a function that drops them silently converts a
sensitive value into a non-sensitive one.

The break these tests catch: any stdlib function that builds its result with a
fresh `CtyType().validate(...)` and returns it without restoring the marks its
arguments carried.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyValue,
)
import pyvider.cty.functions as F
from pyvider.cty.functions import STDLIB, upper
from pyvider.cty.functions._marks import preserve_marks
from pyvider.cty.marks import CtyMark
from pyvider.cty.types import BytesCapsule

SENSITIVE = CtyMark("sensitive")
OTHER = CtyMark("other")


def s(v: str) -> CtyValue[Any]:
    return CtyString().validate(v)


def n(v: object) -> CtyValue[Any]:
    return CtyNumber().validate(v)


def b(v: bool) -> CtyValue[Any]:  # noqa: FBT001
    return CtyBool().validate(v)


STRS = CtyList(element_type=CtyString())
STRMAP = CtyMap(element_type=CtyString())
STRSET = CtySet(element_type=CtyString())

# Hand-built argument fixtures: one valid call per exported function.
# The first argument is the one that gets marked.
CALLS: dict[str, tuple[CtyValue[Any], ...]] = {
    "abs_fn": (n(-5),),
    "add": (n(1), n(2)),
    "and_fn": (b(True), b(True)),
    "byteslen": (BytesCapsule.validate(b"abc"),),
    "bytesslice": (BytesCapsule.validate(b"abcde"), n(1), n(3)),
    "ceil_fn": (n("1.2"),),
    "chomp": (s("hi\n"),),
    "chunklist": (STRS.validate(["a", "b", "c"]), n(2)),
    "coalesce": (CtyValue.null(CtyString()), s("fallback")),
    "coalescelist": (STRS.validate([]), STRS.validate(["a"])),
    "compact": (STRS.validate(["a", "", "b"]),),
    "concat": (STRS.validate(["a"]), STRS.validate(["b"])),
    "contains": (STRS.validate(["a", "b"]), s("a")),
    "csvdecode": (s("a,b\n1,2"),),
    "distinct": (STRS.validate(["a", "a", "b"]),),
    "divide": (n(6), n(3)),
    "element": (STRS.validate(["a", "b"]), n(0)),
    "equal": (s("a"), s("a")),
    "flatten": (CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"], ["b"]]),),
    "floor_fn": (n("1.8"),),
    "formatdate": (s("YYYY"), s("2026-01-01T00:00:00Z")),
    "greater_than": (n(2), n(1)),
    "greater_than_or_equal_to": (n(2), n(1)),
    "hasindex": (STRS.validate(["a"]), n(0)),
    "indent": (n(2), s("a\nb")),
    "index": (STRS.validate(["a", "b"]), n(1)),
    "int_fn": (n("3.7"),),
    "join": (s(","), STRS.validate(["a", "b"])),
    "jsondecode": (s('{"a": 1}'),),
    "jsonencode": (s("x"),),
    "keys": (STRMAP.validate({"k": "v"}),),
    "length": (STRS.validate(["a", "b"]),),
    "less_than": (n(1), n(2)),
    "less_than_or_equal_to": (n(1), n(2)),
    "log_fn": (n(8), n(2)),
    "lookup": (STRMAP.validate({"k": "v"}), s("k"), s("fallback")),
    "lower": (s("AB"),),
    "max_fn": (n(1), n(2)),
    "merge": (
        CtyObject(attribute_types={"a": CtyString()}).validate({"a": "1"}),
        CtyObject(attribute_types={"b": CtyString()}).validate({"b": "2"}),
    ),
    "min_fn": (n(1), n(2)),
    "modulo": (n(5), n(2)),
    "multiply": (n(2), n(3)),
    "negate": (n(1),),
    "not_equal": (s("a"), s("b")),
    "not_fn": (b(True),),
    "or_fn": (b(True), b(False)),
    "parseint_fn": (s("ff"), n(16)),
    "pow_fn": (n(2), n(3)),
    "range_fn": (n(3),),
    # Pattern first, as go-cty takes them.
    "regex": (s("b"), s("abc")),
    "regexall": (s("b"), s("abc")),
    "regexreplace": (s("abc"), s("b"), s("X")),
    "replace": (s("abc"), s("b"), s("X")),
    "reverse": (STRS.validate(["a", "b"]),),
    "sethaselement": (STRSET.validate(["a"]), s("a")),
    "setintersection": (STRSET.validate(["a", "b"]), STRSET.validate(["b"])),
    "format_fn": (s("%s"), s("a")),
    "formatlist": (s("%s"), STRS.validate(["a"])),
    "setproduct": (STRSET.validate(["a"]), STRSET.validate(["b"])),
    "setsubtract": (STRSET.validate(["a", "b"]), STRSET.validate(["b"])),
    "setsymmetricdifference": (STRSET.validate(["a"]), STRSET.validate(["b"])),
    "setunion": (STRSET.validate(["a"]), STRSET.validate(["b"])),
    "signum_fn": (n(-3),),
    "slice": (STRS.validate(["a", "b", "c"]), n(0), n(2)),
    "sort": (STRS.validate(["b", "a"]),),
    "split": (s(","), s("a,b")),
    "assertnotnull": (s("ab"),),
    "strlen": (s("ab"),),
    "strrev": (s("ab"),),
    "substr": (s("hello"), n(1), n(2)),
    "subtract": (n(3), n(1)),
    "timeadd": (s("2026-01-01T00:00:00Z"), s("1h")),
    "title": (s("ab cd"),),
    "to_bool": (s("true"),),
    "to_number": (s("42"),),
    "to_string": (n(42),),
    "trim": (s("xxaxx"), s("x")),
    "trimprefix": (s("abc"), s("a")),
    "trimspace": (s("  a  "),),
    "trimsuffix": (s("abc"), s("c")),
    "upper": (s("ab"),),
    "values": (STRMAP.validate({"k": "v"}),),
    "zipmap": (STRS.validate(["k"]), STRS.validate(["v"])),
}


def test_every_stdlib_function_has_a_fixture() -> None:
    """A new stdlib function must not silently skip mark coverage.

    Driven off the registry rather than `__all__`, because the registry holds
    exactly the functions the mark policy applies to -- `__all__` also carries
    the registry itself and anything else the package chooses to export.
    """
    assert set(CALLS) == {fn.__name__ for fn in STDLIB.values()}


@pytest.mark.parametrize("name", sorted(CALLS))
def test_function_preserves_a_mark_on_its_first_argument(name: str) -> None:
    args = CALLS[name]
    marked = (args[0].mark(SENSITIVE), *args[1:])

    result = getattr(F, name)(*marked)

    assert SENSITIVE in result.marks, f"{name} dropped the mark on its first argument"


@pytest.mark.parametrize("name", sorted(k for k, v in CALLS.items() if len(v) > 1))
def test_function_unions_marks_from_every_argument(name: str) -> None:
    args = CALLS[name]
    marked = (args[0].mark(SENSITIVE), args[1].mark(OTHER), *args[2:])

    result = getattr(F, name)(*marked)

    assert {SENSITIVE, OTHER} <= result.marks, f"{name} lost a mark from one argument"


def test_unmarked_arguments_produce_an_unmarked_result() -> None:
    """The wrapper must not invent marks where none were supplied."""
    assert upper(s("ab")).marks == frozenset()


def test_result_value_is_unchanged_by_mark_propagation() -> None:
    """Stripping and re-applying marks must not disturb the computed value."""
    assert upper(s("hunter2").mark(SENSITIVE)).value == "HUNTER2"
    assert upper(s("hunter2")).value == "HUNTER2"


def test_mark_on_a_nested_element_propagates_to_the_result() -> None:
    """go-cty collects marks with `UnmarkDeep`, not a top-level unmark.

    A sensitive string inside a list makes the whole list sensitive, so a
    function reading that list must carry the mark out. Collecting only the
    container's own marks would let `join` leak the element's value unmarked.
    """
    collection = STRS.validate([s("safe"), s("hunter2").mark(SENSITIVE)])

    result = F.join(s(","), collection)

    assert result.value == "safe,hunter2"
    assert SENSITIVE in result.marks


def test_deeply_nested_mark_propagates_to_the_result() -> None:
    """The deep collection must recurse past the first level."""
    inner_type = CtyList(element_type=CtyString())
    outer = CtyList(element_type=inner_type).validate([inner_type.validate([s("x").mark(SENSITIVE)])])

    result = F.flatten(outer)

    assert SENSITIVE in result.marks


def test_mark_on_a_set_element_propagates_to_the_result() -> None:
    """A validated set stores a frozenset, not a tuple.

    Walking only tuples and dicts to find nested marks skips every set, so a
    sensitive element inside a set is dropped from the result of any function
    that reads it -- and the implementation is handed the marked element it was
    supposed to be shielded from.
    """
    collection = STRSET.validate([s("safe"), s("hunter2").mark(SENSITIVE)])

    result = F.length(collection)

    assert result.value == 2
    assert SENSITIVE in result.marks


def test_set_elements_are_unmarked_before_the_function_runs() -> None:
    seen: list[frozenset[Any]] = []

    @preserve_marks
    def record_element_marks(arg: CtyValue[Any]) -> CtyValue[Any]:
        seen.append(frozenset().union(*(e.marks for e in arg.value)))
        return s("done")

    result = record_element_marks(STRSET.validate([s("hunter2").mark(SENSITIVE)]))

    assert seen == [frozenset()], "the wrapped function saw a marked set element"
    assert result.marks == frozenset({SENSITIVE})


def test_wrapped_function_does_not_see_marks_on_its_arguments() -> None:
    """go-cty strips marks before `Impl` runs so implementations cannot mishandle them.

    `equal` compares its two arguments; a marked and an unmarked copy of the same
    string must still compare equal, which only holds if the wrapper stripped the
    mark before the comparison.
    """
    result = F.equal(s("a").mark(SENSITIVE), s("a"))

    assert result.value is True
    assert result.marks == frozenset({SENSITIVE})


def test_marks_are_stripped_from_capsule_elements_with_custom_equality() -> None:
    """Stripping must not depend on `__eq__` reporting a mark difference.

    `CtyValue.__eq__` delegates to a CtyCapsuleWithOps' `equal_fn`, which
    compares payloads and never looks at marks. A strip that decides "nothing
    changed" by comparing the rebuilt container against the original therefore
    concludes wrongly for capsule elements, and hands the wrapped function the
    marked value it was supposed to be shielded from.
    """
    from pyvider.cty import CtyCapsuleWithOps

    class Box:
        def __init__(self, v: int) -> None:
            self.v = v

    capsule = CtyCapsuleWithOps("Box", Box, equal_fn=lambda a, b: a.v == b.v)
    collection = CtyValue(
        vtype=CtyList(element_type=capsule),
        value=(capsule.validate(Box(1)).mark(SENSITIVE),),
    )

    seen: list[frozenset[Any]] = []

    @preserve_marks
    def record_element_marks(arg: CtyValue[Any]) -> CtyValue[Any]:
        seen.append(arg.value[0].marks)
        return s("done")

    result = record_element_marks(collection)

    assert seen == [frozenset()], "the wrapped function saw a marked argument"
    assert result.marks == frozenset({SENSITIVE})
