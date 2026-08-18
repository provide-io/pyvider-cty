#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The three mark walks must agree about what counts as a container.

Each was written separately and each guessed a slightly different set of
container shapes. When a walk reports a mark it did not remove, callers that
trust the report -- equality trusts unmark_deep to have cleaned both sides, the
codec trusts the strip half of a strip/serialize/restore round trip -- act on a
value that still carries it.
"""

from pyvider.cty import CtyDynamic, CtyList, CtyObject, CtyString, CtyValue
from pyvider.cty.mark_paths import mark_with_paths, unmark_deep_with_paths
from pyvider.cty.marks import CtyMark, collect_marks_deep, unmark_deep
from pyvider.cty.values.equality import equals


def _list_with_raw_payload() -> CtyValue:
    """A CtyValue whose payload is a raw list, which validate is handed routinely."""
    return CtyValue(
        vtype=CtyList(element_type=CtyString()),
        value=[CtyValue(CtyString(), "s").with_marks({CtyMark("sensitive")})],
    )


def _dynamic_wrapping_a_marked_attribute() -> CtyValue:
    obj = CtyObject(attribute_types={"a": CtyString()}).validate(
        {"a": CtyValue(CtyString(), "x").with_marks({"sensitive"})}
    )
    return CtyDynamic().validate(obj)


def test_unmark_deep_actually_strips_a_raw_list_payload() -> None:
    """It reported the mark as removed while leaving it in place."""
    bare, reported = unmark_deep(_list_with_raw_payload())

    assert reported == frozenset({CtyMark("sensitive")})
    assert collect_marks_deep(bare) == frozenset()


def test_equality_does_not_trip_over_a_raw_list_payload() -> None:
    """It raised a bare ValueError out of value_range, outside the taxonomy."""
    other = CtyList(element_type=CtyString()).validate(["x"])

    assert equals(_list_with_raw_payload(), other).value is False


def test_paths_are_recorded_through_a_dynamic_wrapper() -> None:
    stripped, paths = unmark_deep_with_paths(_dynamic_wrapping_a_marked_attribute())

    assert paths, "the wrapper hid the marked attribute entirely"
    assert collect_marks_deep(stripped) == frozenset()


def test_marks_survive_the_strip_and_restore_round_trip() -> None:
    """The reason the module exists: strip, serialize, put them back."""
    original = _dynamic_wrapping_a_marked_attribute()

    stripped, paths = unmark_deep_with_paths(original)
    restored = mark_with_paths(stripped, paths)

    assert collect_marks_deep(restored) == frozenset({"sensitive"})
