#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""One `unwrap_dynamic`, with the mark policy explicit at every call site.

Four private copies of the same loop lived in `walk`, `values/equality`,
`functions/_function` and `functions/collection_functions`; one of them moved
the wrapper's marks onto what it wrapped and three did not, and nothing said
which behaviour a new call site should copy.
"""

from pyvider.cty import CtyDynamic, CtyString
from pyvider.cty.marks import CtyMark
from pyvider.cty.types.structural.dynamic import unwrap_dynamic

SENSITIVE = CtyMark("sensitive")


def _wrapped(depth: int) -> object:
    value = CtyString().validate("x")
    for _ in range(depth):
        value = CtyDynamic().validate(value)
    return value


def test_a_concrete_value_is_returned_as_itself() -> None:
    value = CtyString().validate("x")
    assert unwrap_dynamic(value) is value


def test_nested_wrappers_are_all_removed() -> None:
    inner = unwrap_dynamic(_wrapped(3))
    assert isinstance(inner.type, CtyString)
    assert inner.value == "x"


def test_structural_unwrap_leaves_the_wrappers_marks_behind() -> None:
    wrapper = CtyDynamic().validate(CtyString().validate("x")).mark(SENSITIVE)
    inner = unwrap_dynamic(wrapper)
    assert inner.marks == frozenset()
    assert inner is wrapper.value


def test_carry_marks_moves_the_wrappers_marks_onto_what_it_wrapped() -> None:
    wrapper = CtyDynamic().validate(CtyString().validate("x")).mark(SENSITIVE)
    inner = unwrap_dynamic(wrapper, carry_marks=True)
    assert inner.marks == {SENSITIVE}
    assert isinstance(inner.type, CtyString)


def test_carry_marks_unions_marks_from_every_level() -> None:
    outer = CtyMark("outer")
    wrapper = (
        CtyDynamic().validate(CtyDynamic().validate(CtyString().validate("x")).mark(SENSITIVE)).mark(outer)
    )
    assert unwrap_dynamic(wrapper, carry_marks=True).marks == {SENSITIVE, outer}
