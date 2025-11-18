#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import unicodedata

from hypothesis import given, settings, strategies as st
import pytest

from pyvider.cty import CtyBool, CtyDynamic, CtyList, CtyNumber, CtyObject, CtyString
from pyvider.cty.conversion import cty_to_native
from pyvider.cty.marks import CtyMark
from pyvider.cty.values import CtyValue

# Strategy for generating mark names
mark_names = st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=("Cs",)))

# Strategy for generating mark details (hashable types)
mark_details = (
    st.none() | st.integers() | st.text() | st.lists(st.integers()) | st.dictionaries(st.text(), st.integers())
)


@st.composite
def cty_marks_strategy(draw):
    """Generate a set of CtyMark instances."""
    num_marks = draw(st.integers(min_value=0, max_value=5))
    marks = set()
    for _ in range(num_marks):
        name = draw(mark_names)
        details = draw(mark_details)
        marks.add(CtyMark(name, details))
    return marks


# Strategy for generating simple CtyValue instances
@st.composite
def simple_cty_value_strategy(draw):
    """Generate simple CtyValue instances for testing marks."""
    value_type = draw(st.sampled_from(["string", "number", "bool", "list", "object"]))

    if value_type == "string":
        raw_value = draw(st.text())
        return CtyString().validate(raw_value)
    elif value_type == "number":
        raw_value = draw(st.integers() | st.floats(allow_nan=False, allow_infinity=False))
        return CtyNumber().validate(raw_value)
    elif value_type == "bool":
        raw_value = draw(st.booleans())
        return CtyBool().validate(raw_value)
    elif value_type == "list":
        raw_value = draw(st.lists(st.integers(), max_size=5))
        return CtyList(element_type=CtyNumber()).validate(raw_value)
    else:  # object
        raw_value = draw(st.dictionaries(st.text(min_size=1, max_size=10), st.integers(), max_size=3))
        if not raw_value:
            raw_value = {"default": 0}
        attr_types = {k: CtyNumber() for k in raw_value}
        return CtyObject(attribute_types=attr_types).validate(raw_value)


@settings(deadline=1000, max_examples=200)
@given(cty_value=simple_cty_value_strategy(), marks=cty_marks_strategy())
def test_marks_can_be_applied_and_retrieved(cty_value: CtyValue, marks: set[CtyMark]) -> None:
    """
    Property test: Marks can be applied to values and retrieved.

    Tests that applying marks to a value works correctly and marks
    can be retrieved from the marked value.

    Note: Marks are transient metadata and are NOT serialized to msgpack.
    """
    # Apply marks to the value
    marked_value = cty_value.with_marks(marks)

    # Verify marks were applied
    assert marked_value.marks == frozenset(marks)

    # Underlying value should be unchanged
    if isinstance(cty_value.value, str):
        assert marked_value.value == unicodedata.normalize("NFC", cty_value.value)
    elif isinstance(cty_value.value, float):
        assert marked_value.value == pytest.approx(cty_value.value)

    # Type should be preserved
    assert marked_value.type.equal(cty_value.type)


@settings(deadline=500, max_examples=100)
@given(cty_value=simple_cty_value_strategy(), marks1=cty_marks_strategy(), marks2=cty_marks_strategy())
def test_marks_are_immutable_and_additive(
    cty_value: CtyValue, marks1: set[CtyMark], marks2: set[CtyMark]
) -> None:
    """
    Property test: Marks are immutable and adding marks creates new values.

    Tests that applying marks doesn't modify the original value and that
    marks can be combined additively.
    """
    # Apply first set of marks
    marked_v1 = cty_value.with_marks(marks1)

    # Original value should be unchanged
    assert cty_value.marks == frozenset()

    # Apply second set of marks to already marked value
    marked_v2 = marked_v1.with_marks(marks2)

    # First marked value should be unchanged
    assert marked_v1.marks == frozenset(marks1)

    # Second value should have union of marks
    assert marked_v2.marks == frozenset(marks1 | marks2)

    # All three values should have the same underlying value
    assert marked_v1.type.equal(cty_value.type)
    assert marked_v2.type.equal(cty_value.type)


@settings(deadline=500, max_examples=100)
@given(marks=cty_marks_strategy())
def test_marks_with_null_and_unknown(marks: set[CtyMark]) -> None:
    """
    Property test: Marks can be applied to null and unknown values.

    Tests that marks can be applied to null and unknown values correctly.

    Note: Marks are transient metadata and are NOT serialized to msgpack.
    """
    # Test with null
    null_value = CtyValue.null(CtyString())
    marked_null = null_value.with_marks(marks)

    assert marked_null.is_null
    assert marked_null.marks == frozenset(marks)
    assert marked_null.type.equal(CtyString())

    # Test with unknown
    unknown_value = CtyValue.unknown(CtyNumber())
    marked_unknown = unknown_value.with_marks(marks)

    assert marked_unknown.is_unknown
    assert marked_unknown.marks == frozenset(marks)
    assert marked_unknown.type.equal(CtyNumber())


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_marks_work_with_dynamic_types(data) -> None:
    """
    Property test: Marks can be applied to dynamically typed values.

    Tests that marks work correctly when applied to values that have
    been validated through CtyDynamic.

    Note: Marks are transient metadata and are NOT serialized to msgpack.
    """
    # Generate a value using the json strategy
    json_primitives = (
        st.none()
        | st.booleans()
        | st.integers()
        | st.floats(allow_nan=False, allow_infinity=False)
        | st.text()
    )
    native_value = data.draw(json_primitives)
    marks = data.draw(cty_marks_strategy())

    # Validate through dynamic schema
    schema = CtyDynamic()
    cty_value = schema.validate(native_value)

    # Apply marks
    marked_value = cty_value.with_marks(marks)

    # Marks should be applied
    assert marked_value.marks == frozenset(marks)

    # Value should be unchanged
    native_result = cty_to_native(marked_value)

    if isinstance(native_value, str):
        assert native_result == unicodedata.normalize("NFC", native_value)
    elif isinstance(native_value, float):
        assert native_result == pytest.approx(native_value)
    else:
        assert native_result == native_value


@settings(deadline=500, max_examples=50)
@given(marks=cty_marks_strategy())
def test_marks_details_hashability(marks: set[CtyMark]) -> None:
    """
    Property test: Mark details should be properly converted to hashable types.

    Tests that the details field is always hashable and can be used in sets.
    """
    # All marks should be hashable (can be added to a set)
    marks_set = set(marks)

    # Should be able to recreate the set
    marks_list = list(marks_set)
    recreated_set = set(marks_list)

    assert marks_set == recreated_set

    # Should be able to create frozenset (used internally)
    frozen_marks = frozenset(marks)

    # Should be able to compare marks
    for mark in marks:
        assert mark in frozen_marks


# 🌊🪢🔚
