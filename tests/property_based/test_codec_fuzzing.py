#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import unicodedata

from hypothesis import assume, given, settings, strategies as st
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
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.conversion import cty_to_native
from pyvider.cty.marks import CtyMark
from pyvider.cty.values import CtyValue
from pyvider.cty.values.markers import UnknownValue


# Aggressive fuzzing strategy for deeply nested structures
@st.composite
def deeply_nested_json_strategy(draw, max_depth=10):
    """
    Generate deeply nested JSON-like structures for fuzzing.

    This goes beyond the standard roundtrip tests by creating
    more pathological nesting scenarios.
    """
    depth = draw(st.integers(min_value=0, max_value=max_depth))

    if depth == 0:
        # Base case: primitives
        return draw(
            st.none()
            | st.booleans()
            | st.integers(min_value=-(2**53), max_value=2**53)
            | st.floats(allow_nan=False, allow_infinity=False, min_value=-1e100, max_value=1e100)
            | st.text(max_size=100)
        )

    # Recursive case: collections
    child_strategy = deeply_nested_json_strategy(max_depth=depth - 1)

    return draw(
        st.lists(child_strategy, max_size=10)
        | st.dictionaries(
            st.text(min_size=1, max_size=20).filter(lambda s: s.strip()), child_strategy, max_size=10
        )
    )


# Strategy for generating complex marked values
@st.composite
def marked_nested_value_strategy(draw):
    """Generate nested values with marks at different levels."""
    # Generate base structure
    data = draw(deeply_nested_json_strategy(max_depth=5))

    # Validate through dynamic type
    schema = CtyDynamic()
    cty_value = schema.validate(data)

    # Randomly add marks
    num_marks = draw(st.integers(min_value=0, max_value=3))
    if num_marks > 0:
        marks = set()
        for _ in range(num_marks):
            mark_name = draw(st.text(min_size=1, max_size=20))
            mark_details = draw(st.none() | st.integers() | st.text(max_size=50))
            marks.add(CtyMark(mark_name, mark_details))
        cty_value = cty_value.with_marks(marks)

    return cty_value


@settings(deadline=2000, max_examples=100)
@given(nested_data=deeply_nested_json_strategy(max_depth=8))
def test_codec_handles_deep_nesting(nested_data) -> None:
    """
    Fuzzing test: Codec should handle deeply nested structures.

    This test fuzzes the codec with pathologically nested data to ensure
    it doesn't fail on complex structures.
    """
    schema = CtyDynamic()

    try:
        # Validate and encode
        cty_value = schema.validate(nested_data)
        msgpack_bytes = cty_to_msgpack(cty_value, schema)

        # Decode
        decoded = cty_from_msgpack(msgpack_bytes, schema)

        # Convert back to native
        result = cty_to_native(decoded)

        # Should be equivalent (with normalization)
        def normalize_for_comparison(obj):
            if isinstance(obj, dict):
                return {unicodedata.normalize("NFC", k): normalize_for_comparison(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [normalize_for_comparison(item) for item in obj]
            if isinstance(obj, str):
                return unicodedata.normalize("NFC", obj)
            if isinstance(obj, float):
                return pytest.approx(obj, rel=1e-9, abs=1e-9)
            return obj

        assert normalize_for_comparison(result) == normalize_for_comparison(nested_data)

    except Exception as e:
        pytest.fail(f"Codec failed on nested data: {type(e).__name__}: {e}")


@settings(deadline=2000, max_examples=100)
@given(marked_value=marked_nested_value_strategy())
def test_codec_handles_marked_nested_structures(marked_value: CtyValue) -> None:
    """
    Fuzzing test: Codec should handle marked nested structures gracefully.

    Tests that the codec can serialize values with marks attached,
    even though marks are not preserved during serialization (by design).

    Note: Marks are transient metadata and are NOT serialized to msgpack.
    """
    # Serialize (marks will be dropped)
    msgpack_bytes = cty_to_msgpack(marked_value, marked_value.type)

    # Deserialize
    decoded = cty_from_msgpack(msgpack_bytes, marked_value.type)

    # Value structure should be preserved (but marks are lost)
    assert decoded.type.equal(marked_value.type)
    assert decoded.marks == frozenset()  # Marks are not serialized


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_codec_handles_heterogeneous_lists(data) -> None:
    """
    Fuzzing test: Codec should handle lists with heterogeneous element types.

    Tests the codec with lists containing different types, which should be
    handled through dynamic typing.
    """
    # Generate a heterogeneous list
    list_items = data.draw(
        st.lists(
            st.none()
            | st.booleans()
            | st.integers()
            | st.floats(allow_nan=False, allow_infinity=False)
            | st.text(),
            min_size=1,
            max_size=20,
        )
    )

    # Ensure we have at least some heterogeneity
    types_present = {type(item).__name__ for item in list_items if item is not None}
    assume(len(types_present) >= 2)

    schema = CtyDynamic()
    cty_value = schema.validate(list_items)

    # Encode and decode
    msgpack_bytes = cty_to_msgpack(cty_value, schema)
    decoded = cty_from_msgpack(msgpack_bytes, schema)

    # Convert back
    result = cty_to_native(decoded)

    # Normalize for comparison
    def normalize(item):
        if isinstance(item, str):
            return unicodedata.normalize("NFC", item)
        if isinstance(item, float):
            return pytest.approx(item)
        return item

    assert [normalize(r) for r in result] == [normalize(i) for i in list_items]


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_codec_handles_objects_with_unknown_values(data) -> None:
    """
    Fuzzing test: Codec should correctly handle objects with unknown values.

    Tests that unknown values in object attributes are correctly
    serialized and deserialized.

    Note: Null values in object attributes are only allowed for optional
    attributes, so this test focuses on unknown values instead.
    """
    # Generate attribute names (ASCII only for reliability)
    attr_names = data.draw(
        st.lists(
            st.text(min_size=1, max_size=10, alphabet="abcdefghijklmnopqrstuvwxyz"),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )

    if not attr_names:
        attr_names = ["default"]

    # Create object type
    attr_types = {name: CtyString() for name in attr_names}
    obj_type = CtyObject(attribute_types=attr_types)

    # Create object value with mix of normal and unknown values
    obj_value = {}
    for name in attr_names:
        value_type = data.draw(st.sampled_from(["normal", "unknown"]))
        if value_type == "normal":
            obj_value[name] = CtyString().validate(data.draw(st.text(max_size=20)))
        else:  # unknown
            obj_value[name] = CtyValue.unknown(CtyString())

    cty_obj = obj_type.validate(obj_value)

    # Encode and decode
    msgpack_bytes = cty_to_msgpack(cty_obj, obj_type)
    decoded = cty_from_msgpack(msgpack_bytes, obj_type)

    # If the whole object is unknown, we can't access individual attributes
    if decoded.is_unknown:
        assert isinstance(decoded.value, UnknownValue)
        return

    # Verify each attribute
    for name in attr_names:
        original_attr = obj_value[name]
        decoded_attr = decoded.value[name]

        assert original_attr.is_unknown == decoded_attr.is_unknown

        if not original_attr.is_unknown:
            assert unicodedata.normalize("NFC", decoded_attr.value) == unicodedata.normalize(
                "NFC", original_attr.value
            )


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_codec_handles_sets_and_maps(data) -> None:
    """
    Fuzzing test: Codec should handle CtySet and CtyMap types.

    Tests serialization/deserialization of set and map types with
    various element/value types.
    """
    collection_type = data.draw(st.sampled_from(["set", "map"]))

    if collection_type == "set":
        # Generate a set of strings (non-empty to ensure proper set handling)
        items = data.draw(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10, unique=True))
        set_type = CtySet(element_type=CtyString())
        cty_value = set_type.validate(items)

        # Encode and decode
        msgpack_bytes = cty_to_msgpack(cty_value, set_type)
        decoded = cty_from_msgpack(msgpack_bytes, set_type)

        # Verify type is preserved
        assert isinstance(decoded.type, CtySet)

        # Convert back to native - sets are converted to lists by cty_to_native
        result = cty_to_native(decoded)
        expected_items = {unicodedata.normalize("NFC", item) for item in items}

        # Result should be a list containing all the expected items
        assert isinstance(result, list)
        assert set(result) == expected_items

    else:  # map
        # Generate a map of string -> number
        items = data.draw(
            st.dictionaries(
                st.text(min_size=1, max_size=20),
                st.integers() | st.floats(allow_nan=False, allow_infinity=False),
                max_size=10,
            )
        )

        map_type = CtyMap(element_type=CtyNumber())
        cty_value = map_type.validate(items)

        # Encode and decode
        msgpack_bytes = cty_to_msgpack(cty_value, map_type)
        decoded = cty_from_msgpack(msgpack_bytes, map_type)

        # Convert back to native
        result = cty_to_native(decoded)

        # Normalize for comparison
        expected = {unicodedata.normalize("NFC", k): pytest.approx(float(v)) for k, v in items.items()}
        result_normalized = {k: pytest.approx(float(v)) for k, v in result.items()}

        assert result_normalized == expected


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_codec_handles_tuples_with_varied_types(data) -> None:
    """
    Fuzzing test: Codec should handle CtyTuple with heterogeneous element types.

    Tests that tuples with different element types at each position are
    correctly serialized and deserialized.
    """
    # Generate 2-5 element types
    num_elements = data.draw(st.integers(min_value=2, max_value=5))
    element_types = []
    element_values = []

    for _ in range(num_elements):
        elem_type = data.draw(st.sampled_from([CtyString(), CtyNumber(), CtyBool()]))
        element_types.append(elem_type)

        # Generate a value for this type
        if isinstance(elem_type, CtyString):
            element_values.append(data.draw(st.text(max_size=20)))
        elif isinstance(elem_type, CtyNumber):
            element_values.append(data.draw(st.integers() | st.floats(allow_nan=False, allow_infinity=False)))
        else:  # CtyBool
            element_values.append(data.draw(st.booleans()))

    # Create tuple type and value
    tuple_type = CtyTuple(element_types=tuple(element_types))
    cty_value = tuple_type.validate(element_values)

    # Encode and decode
    msgpack_bytes = cty_to_msgpack(cty_value, tuple_type)
    decoded = cty_from_msgpack(msgpack_bytes, tuple_type)

    # Verify each element
    for _i, (original, decoded_val) in enumerate(zip(element_values, decoded.value, strict=False)):
        if isinstance(original, str):
            assert decoded_val.value == unicodedata.normalize("NFC", original)
        elif isinstance(original, float):
            assert decoded_val.value == pytest.approx(original)
        else:
            assert decoded_val.value == original


@settings(deadline=2000, max_examples=50)
@given(data=st.data())
def test_codec_handles_refined_unknowns(data) -> None:
    """
    Fuzzing test: Codec should handle refined unknown values.

    Tests that unknown values with refined types are correctly
    serialized and deserialized.

    Note: Marks are NOT serialized to msgpack - they are transient metadata.
    """
    # Create a refined unknown - an unknown value with a more specific type
    base_type = data.draw(
        st.sampled_from(
            [
                CtyString(),
                CtyNumber(),
                CtyBool(),
                CtyList(element_type=CtyString()),
                CtyObject(attribute_types={"name": CtyString()}),
            ]
        )
    )

    unknown_value = CtyValue.unknown(base_type)

    # Encode and decode
    msgpack_bytes = cty_to_msgpack(unknown_value, base_type)
    decoded = cty_from_msgpack(msgpack_bytes, base_type)

    # Should still be unknown
    assert decoded.is_unknown

    # Type should match
    assert decoded.type.equal(base_type)

    # Marks are not serialized, so decoded will have no marks
    assert decoded.marks == frozenset()


@settings(deadline=2000, max_examples=50)
@given(data=st.data())
def test_codec_stress_test_large_collections(data) -> None:
    """
    Stress test: Codec should handle large collections efficiently.

    Tests the codec with larger-than-normal data structures to ensure
    it can handle realistic workloads.
    """
    collection_type = data.draw(st.sampled_from(["list", "map", "object"]))

    if collection_type == "list":
        # Large list of numbers
        items = data.draw(
            st.lists(
                st.integers() | st.floats(allow_nan=False, allow_infinity=False), min_size=50, max_size=200
            )
        )
        list_type = CtyList(element_type=CtyNumber())
        cty_value = list_type.validate(items)

        msgpack_bytes = cty_to_msgpack(cty_value, list_type)
        decoded = cty_from_msgpack(msgpack_bytes, list_type)

        result = cty_to_native(decoded)
        assert len(result) == len(items)

    elif collection_type == "map":
        # Large map
        items = data.draw(
            st.dictionaries(st.text(min_size=1, max_size=10), st.text(max_size=50), min_size=20, max_size=100)
        )
        map_type = CtyMap(element_type=CtyString())
        cty_value = map_type.validate(items)

        msgpack_bytes = cty_to_msgpack(cty_value, map_type)
        decoded = cty_from_msgpack(msgpack_bytes, map_type)

        result = cty_to_native(decoded)
        assert len(result) == len(items)

    else:  # object
        # Object with many attributes
        num_attrs = data.draw(st.integers(min_value=20, max_value=50))
        attr_names = [f"attr_{i}" for i in range(num_attrs)]
        attr_types = {name: CtyString() for name in attr_names}
        obj_type = CtyObject(attribute_types=attr_types)

        obj_value = {name: CtyString().validate(f"value_{i}") for i, name in enumerate(attr_names)}
        cty_value = obj_type.validate(obj_value)

        msgpack_bytes = cty_to_msgpack(cty_value, obj_type)
        decoded = cty_from_msgpack(msgpack_bytes, obj_type)

        assert len(decoded.value) == len(obj_value)


# 🌊🪢🔚
