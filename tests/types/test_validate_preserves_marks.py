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


def test_set_preserves_marks_on_its_elements() -> None:
    result = CtySet(element_type=CtyString()).validate([marked_string()])

    assert [e.marks for e in result.value] == [frozenset({SENSITIVE})]


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
