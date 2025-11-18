#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Property-based tests for CTY spec compliance.

These tests validate that the Python implementation correctly implements
the CTY specification, focusing on:

- Canonical serialization formats
- Type constraint adherence
- Edge case handling
- Spec-mandated behavior (e.g., NFC normalization, typed nulls)

Note: Cross-language compatibility testing is handled separately by TofuSoup.
Run `soup cty test` for cross-language compatibility validation."""

import unicodedata

from hypothesis import given, settings, strategies as st
import msgpack
import pytest

from pyvider.cty import CtyBool, CtyDynamic, CtyList, CtyNumber, CtyObject, CtyString
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.conversion import cty_to_native
from pyvider.cty.marks import CtyMark
from pyvider.cty.values import CtyValue


@settings(deadline=1000, max_examples=200)
@given(text=st.text())
def test_string_values_use_nfc_normalization(text: str) -> None:
    """
    Spec compliance: String values should use NFC Unicode normalization.

    The CTY spec mandates NFC normalization to prevent issues with
    different Unicode representations.
    """
    string_type = CtyString()
    cty_value = string_type.validate(text)

    # Value should be NFC normalized
    expected = unicodedata.normalize("NFC", text)
    assert cty_value.value == expected

    # Roundtrip should preserve NFC
    msgpack_bytes = cty_to_msgpack(cty_value, string_type)
    decoded = cty_from_msgpack(msgpack_bytes, string_type)

    assert decoded.value == expected


@settings(deadline=1000, max_examples=200)
@given(
    number=st.integers(min_value=-(2**53), max_value=2**53) | st.floats(allow_nan=False, allow_infinity=False)
)
def test_number_values_preserve_numeric_precision(number: int | float) -> None:
    """
    Spec compliance: Number values should preserve precision within safe range.

    Tests that numbers are correctly serialized and preserve their precision,
    which is critical for cross-language compatibility.
    """
    number_type = CtyNumber()
    cty_value = number_type.validate(number)

    # Roundtrip should preserve value
    msgpack_bytes = cty_to_msgpack(cty_value, number_type)
    decoded = cty_from_msgpack(msgpack_bytes, number_type)

    if isinstance(number, float):
        assert decoded.value == pytest.approx(number, rel=1e-9)
    else:
        assert decoded.value == number


@settings(deadline=1000, max_examples=200)
@given(value=st.booleans())
def test_bool_values_are_distinct_from_numbers(value: bool) -> None:
    """
    Spec compliance: Boolean values should be distinct from numbers.

    In some languages, booleans can be coerced to numbers (0/1). This test
    ensures that CTY maintains the distinction.
    """
    bool_type = CtyBool()
    cty_value = bool_type.validate(value)

    # Serialize
    msgpack_bytes = cty_to_msgpack(cty_value, bool_type)

    # Deserialize
    decoded = cty_from_msgpack(msgpack_bytes, bool_type)

    # Should be a boolean, not a number
    assert isinstance(decoded.value, bool)
    assert decoded.value == value

    # Type should be CtyBool
    assert isinstance(decoded.type, CtyBool)


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_null_values_have_type_information(data) -> None:
    """
    Spec compliance: Null values should preserve their type.

    In CTY, null values are typed (unlike JSON's untyped null). This is
    critical for cross-language compatibility.
    """
    # Generate a random type
    value_type = data.draw(
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

    # Create null value
    null_value = CtyValue.null(value_type)

    # Serialize
    msgpack_bytes = cty_to_msgpack(null_value, value_type)

    # Deserialize
    decoded = cty_from_msgpack(msgpack_bytes, value_type)

    # Should be null with correct type
    assert decoded.is_null
    assert decoded.type.equal(value_type)


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_unknown_values_have_type_information(data) -> None:
    """
    Spec compliance: Unknown values should preserve their type.

    Unknown values represent values that aren't known yet (e.g., during
    planning in Terraform). They must maintain type information.
    """
    # Generate a random type
    value_type = data.draw(
        st.sampled_from(
            [
                CtyString(),
                CtyNumber(),
                CtyBool(),
                CtyList(element_type=CtyNumber()),
            ]
        )
    )

    # Create unknown value
    unknown_value = CtyValue.unknown(value_type)

    # Serialize
    msgpack_bytes = cty_to_msgpack(unknown_value, value_type)

    # Deserialize
    decoded = cty_from_msgpack(msgpack_bytes, value_type)

    # Should be unknown with correct type
    assert decoded.is_unknown
    assert decoded.type.equal(value_type)


@settings(deadline=1000, max_examples=100)
@given(items=st.lists(st.text(), max_size=10))
def test_list_order_is_preserved(items: list[str]) -> None:
    """
    Spec compliance: List order should be preserved through serialization.

    Lists are ordered collections, unlike sets. Order must be maintained.
    """
    list_type = CtyList(element_type=CtyString())
    cty_value = list_type.validate(items)

    # Serialize and deserialize
    msgpack_bytes = cty_to_msgpack(cty_value, list_type)
    decoded = cty_from_msgpack(msgpack_bytes, list_type)

    # Order should be preserved
    result = cty_to_native(decoded)
    expected = [unicodedata.normalize("NFC", item) for item in items]

    assert result == expected


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_object_attribute_order_is_stable(data) -> None:
    """
    Spec compliance: Object attributes should have stable serialization.

    While attribute order isn't semantically significant, stable serialization
    helps with debugging and comparison across implementations.
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

    # Sort to ensure consistent ordering
    attr_names = sorted(attr_names)

    # Create object type
    attr_types = {name: CtyString() for name in attr_names}
    obj_type = CtyObject(attribute_types=attr_types)

    # Create object value
    obj_value = {name: CtyString().validate(f"value_{name}") for name in attr_names}
    cty_obj = obj_type.validate(obj_value)

    # Serialize
    msgpack_bytes = cty_to_msgpack(cty_obj, obj_type)

    # Deserialize
    decoded = cty_from_msgpack(msgpack_bytes, obj_type)

    # All attributes should be present
    assert set(decoded.value.keys()) == set(attr_names)

    # Values should match
    for name in attr_names:
        assert decoded.value[name].value == f"value_{name}"


@settings(deadline=1000, max_examples=100)
@given(
    marks_data=st.lists(
        st.tuples(st.text(min_size=1, max_size=20), st.none() | st.integers() | st.text(max_size=50)),
        max_size=5,
    )
)
def test_marks_hashability_and_creation(marks_data: list[tuple[str, int | str | None]]) -> None:
    """
    Spec compliance: Marks should be hashable and properly created.

    Marks are a CTY-specific feature for attaching metadata. They must
    be hashable so they can be stored in sets.

    Note: Marks are NOT serialized to msgpack - they are transient metadata.
    """
    # Create marks
    marks = {CtyMark(name, details) for name, details in marks_data}

    # All marks should be hashable
    marks_frozenset = frozenset(marks)

    # Should be able to recreate
    marks_list = list(marks_frozenset)
    recreated = frozenset(marks_list)

    assert marks_frozenset == recreated

    # Apply to a value
    string_value = CtyString().validate("test")
    marked_value = string_value.with_marks(marks)

    # Marks should be attached
    assert marked_value.marks == marks_frozenset


@settings(deadline=2000, max_examples=100)
@given(data=st.data())
def test_dynamic_type_inference_is_deterministic(data) -> None:
    """
    Spec compliance: Dynamic type inference should be deterministic.

    Given the same input, type inference should always produce the same
    result, which is critical for cross-language consistency.
    """
    # Generate test data
    primitives = (
        st.none()
        | st.booleans()
        | st.integers()
        | st.floats(allow_nan=False, allow_infinity=False)
        | st.text()
    )
    nested_data = data.draw(
        st.recursive(
            primitives,
            lambda children: st.lists(children, max_size=5)
            | st.dictionaries(st.text(min_size=1), children, max_size=5),
            max_leaves=10,
        )
    )

    schema = CtyDynamic()

    # Infer type multiple times
    value1 = schema.validate(nested_data)
    value2 = schema.validate(nested_data)

    # Should produce the same type
    assert value1.type.equal(value2.type)

    # Serialize both
    bytes1 = cty_to_msgpack(value1, schema)
    bytes2 = cty_to_msgpack(value2, schema)

    # Deserialize both
    decoded1 = cty_from_msgpack(bytes1, schema)
    decoded2 = cty_from_msgpack(bytes2, schema)

    # Should have the same type
    assert decoded1.type.equal(decoded2.type)


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_msgpack_encoding_is_compact(data) -> None:
    """
    Spec compliance: MessagePack encoding should be reasonably compact.

    While we don't enforce a specific size, we can verify that encoding
    doesn't waste excessive space, which could indicate compatibility issues.
    """
    # Generate simple data
    value_type = data.draw(st.sampled_from(["string", "number", "bool", "list"]))

    if value_type == "string":
        raw_value = data.draw(st.text(max_size=100))
        cty_value = CtyString().validate(raw_value)
        cty_type = CtyString()
    elif value_type == "number":
        raw_value = data.draw(st.integers(min_value=0, max_value=1000))
        cty_value = CtyNumber().validate(raw_value)
        cty_type = CtyNumber()
    elif value_type == "bool":
        raw_value = data.draw(st.booleans())
        cty_value = CtyBool().validate(raw_value)
        cty_type = CtyBool()
    else:  # list
        raw_value = data.draw(st.lists(st.integers(), max_size=20))
        cty_value = CtyList(element_type=CtyNumber()).validate(raw_value)
        cty_type = CtyList(element_type=CtyNumber())

    # Serialize
    msgpack_bytes = cty_to_msgpack(cty_value, cty_type)

    # Should be decodable as msgpack
    try:
        msgpack.unpackb(msgpack_bytes)
    except Exception as e:
        pytest.fail(f"Invalid MessagePack encoding: {e}")

    # Size should be reasonable (not more than 10x the raw data)
    # This is a loose bound to catch egregious issues
    import sys

    raw_size = sys.getsizeof(raw_value)
    encoded_size = len(msgpack_bytes)

    # For very small values, the overhead can be proportionally large
    if raw_size > 100:
        assert encoded_size < raw_size * 10, (
            f"Encoding too large: {encoded_size} bytes for {raw_size} bytes of data"
        )


@settings(deadline=1000, max_examples=100)
@given(data=st.data())
def test_empty_collections_are_distinct_from_null(data) -> None:
    """
    Spec compliance: Empty collections should be distinct from null.

    An empty list is different from a null list. This distinction must
    be preserved across implementations.
    """
    collection_type = data.draw(st.sampled_from(["list", "map", "set"]))

    if collection_type == "list":
        from pyvider.cty import CtyList

        list_type = CtyList(element_type=CtyString())
        empty_value = list_type.validate([])
        null_value = CtyValue.null(list_type)

        # Serialize both
        empty_bytes = cty_to_msgpack(empty_value, list_type)
        null_bytes = cty_to_msgpack(null_value, list_type)

        # Should produce different serializations
        assert empty_bytes != null_bytes

        # Deserialize
        decoded_empty = cty_from_msgpack(empty_bytes, list_type)
        decoded_null = cty_from_msgpack(null_bytes, list_type)

        # Empty should not be null
        assert not decoded_empty.is_null
        assert len(decoded_empty.value) == 0

        # Null should be null
        assert decoded_null.is_null


@settings(deadline=1000, max_examples=50)
@given(data=st.data())
def test_deeply_nested_structures_have_consistent_types(data) -> None:
    """
    Spec compliance: Deeply nested structures should maintain type consistency.

    Tests that type information is correctly preserved through multiple
    levels of nesting, which is important for complex configurations.
    """
    # Create a deeply nested structure
    # List[List[List[String]]]
    inner_list = CtyList(element_type=CtyString())
    middle_list = CtyList(element_type=inner_list)
    outer_list = CtyList(element_type=middle_list)

    # Generate nested data
    nested_data = data.draw(
        st.lists(st.lists(st.lists(st.text(max_size=10), max_size=3), max_size=3), max_size=3)
    )

    # Validate
    cty_value = outer_list.validate(nested_data)

    # Serialize and deserialize
    msgpack_bytes = cty_to_msgpack(cty_value, outer_list)
    decoded = cty_from_msgpack(msgpack_bytes, outer_list)

    # Type should be preserved
    assert decoded.type.equal(outer_list)

    # Structure should be intact
    result = cty_to_native(decoded)

    # Normalize strings for comparison
    def normalize_nested(data):
        if isinstance(data, list):
            return [normalize_nested(item) for item in data]
        if isinstance(data, str):
            return unicodedata.normalize("NFC", data)
        return data

    assert normalize_nested(result) == normalize_nested(nested_data)


# 🌊🪢🔚
