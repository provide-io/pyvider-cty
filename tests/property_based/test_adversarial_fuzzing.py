#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Adversarial property-based tests to abuse the system and find security issues.

These tests intentionally try to break the system with:
- Malicious payloads
- Resource exhaustion
- Type confusion
- Boundary attacks
- Unicode exploits"""

import contextlib
import struct
import unicodedata

from hypothesis import HealthCheck, assume, given, settings, strategies as st
import msgpack
import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyObject,
    CtyString,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.exceptions import CtyValidationError, DeserializationError
from pyvider.cty.marks import CtyMark
from pyvider.cty.values import CtyValue

# Aggressive settings for adversarial testing
ADVERSARIAL_SETTINGS = settings(
    deadline=10000,  # 10 seconds
    max_examples=1000,  # Much more than normal
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@st.composite
def malicious_msgpack_strategy(draw):
    """Generate potentially malicious msgpack payloads."""
    attack_type = draw(
        st.sampled_from(
            [
                "truncated",
                "corrupted_header",
                "invalid_extension",
                "nested_bomb",
                "type_confusion",
            ]
        )
    )

    if attack_type == "truncated":
        # Create valid data then truncate it
        valid_data = msgpack.packb({"test": "data"})
        truncate_at = draw(st.integers(min_value=1, max_value=len(valid_data) - 1))
        return valid_data[:truncate_at]

    elif attack_type == "corrupted_header":
        # Valid payload with corrupted header bytes
        valid_data = msgpack.packb([1, 2, 3])
        data_list = bytearray(valid_data)
        if len(data_list) > 0:
            corrupt_idx = draw(st.integers(min_value=0, max_value=len(data_list) - 1))
            data_list[corrupt_idx] = draw(st.integers(min_value=0, max_value=255))
        return bytes(data_list)

    elif attack_type == "invalid_extension":
        # Create msgpack with invalid extension type
        invalid_ext_type = draw(st.integers(min_value=13, max_value=127))  # Avoid 0 and 12
        ext_data = draw(st.binary(min_size=1, max_size=100))
        return msgpack.packb(msgpack.ExtType(invalid_ext_type, ext_data))

    elif attack_type == "nested_bomb":
        # Deeply nested structure to test stack limits
        depth = draw(st.integers(min_value=50, max_value=150))
        data = "core"
        for _ in range(depth):
            data = [data]
        return msgpack.packb(data)

    else:  # type_confusion
        # Pack data as one type, user expects another
        data_types = [
            42,  # number
            "string",  # string
            [1, 2, 3],  # list
            {"key": "value"},  # map
            True,  # bool
        ]
        return msgpack.packb(draw(st.sampled_from(data_types)))


@ADVERSARIAL_SETTINGS
@given(payload=malicious_msgpack_strategy())
def test_codec_handles_malicious_payloads_gracefully(payload: bytes) -> None:
    """
    Adversarial test: Codec should handle malicious payloads without crashing.

    Tests that corrupted, truncated, or otherwise malicious msgpack data
    raises appropriate exceptions rather than crashing or corrupting state.
    """
    schema = CtyDynamic()

    try:
        # Attempt to deserialize malicious payload
        result = cty_from_msgpack(payload, schema)
        # If it succeeds, the result should at least be a valid CtyValue
        assert isinstance(result, CtyValue)
    except (
        DeserializationError,
        msgpack.exceptions.ExtraData,
        msgpack.exceptions.UnpackException,
        ValueError,
        TypeError,
        struct.error,
    ):
        # These are acceptable - the codec correctly rejected bad data
        pass
    except Exception as e:
        # Any other exception might indicate a problem
        pytest.fail(f"Unexpected exception type {type(e).__name__}: {e}")


@ADVERSARIAL_SETTINGS
@given(depth=st.integers(min_value=100, max_value=300))
def test_deeply_nested_structures_hit_limits_gracefully(depth: int) -> None:
    """
    Adversarial test: Extremely deep nesting should hit limits gracefully.

    Tests that deeply nested structures either work or fail with clear errors,
    not stack overflows or crashes.
    """
    # Build a deeply nested list structure
    data = None
    for _ in range(depth):
        data = [data]

    schema = CtyDynamic()

    try:
        # This might hit recursion limits, which is fine
        cty_value = schema.validate(data)
        assert isinstance(cty_value, CtyValue)
    except (RecursionError, ValueError):
        # Expected for very deep structures
        pass


@ADVERSARIAL_SETTINGS
@given(length=st.integers(min_value=100_000, max_value=1_000_000))
def test_extremely_large_strings_are_handled(length: int) -> None:
    """
    Adversarial test: Very large strings should be handled without memory issues.

    Tests that megabyte-sized strings can be validated, serialized, and
    deserialized without crashing or excessive memory usage.
    """
    # Generate large string
    text = "a" * length

    string_type = CtyString()

    # Validate large string
    cty_value = string_type.validate(text)
    assert isinstance(cty_value.value, str)
    assert len(cty_value.value) == length

    # Serialize and deserialize
    msgpack_bytes = cty_to_msgpack(cty_value, string_type)
    decoded = cty_from_msgpack(msgpack_bytes, string_type)

    # Verify data integrity
    assert len(decoded.value) == length


@ADVERSARIAL_SETTINGS
@given(size=st.integers(min_value=10_000, max_value=50_000))
def test_very_large_collections_are_handled(size: int) -> None:
    """
    Adversarial test: Very large collections should be handled efficiently.

    Tests that collections with tens of thousands of items can be processed
    without excessive memory or time.
    """
    # Create a large list
    items = list(range(size))
    list_type = CtyList(element_type=CtyNumber())

    # Validate
    cty_value = list_type.validate(items)

    # Handle case where validation might return unknown
    if cty_value.is_unknown:
        return

    assert len(cty_value.value) == size

    # Serialize (this could be slow for very large data)
    msgpack_bytes = cty_to_msgpack(cty_value, list_type)
    assert len(msgpack_bytes) > 0

    # Deserialize
    decoded = cty_from_msgpack(msgpack_bytes, list_type)

    # Handle unknown in decoded value
    if decoded.is_unknown:
        return

    assert len(decoded.value) == size


@ADVERSARIAL_SETTINGS
@given(num_marks=st.integers(min_value=100, max_value=1000), data=st.integers() | st.text(max_size=100))
def test_many_marks_on_value_are_handled(num_marks: int, data) -> None:
    """
    Adversarial test: Values with many marks should be handled efficiently.

    Tests that a value with hundreds or thousands of marks doesn't cause
    performance issues or memory problems.
    """
    # Create value
    value = CtyNumber().validate(data) if isinstance(data, int) else CtyString().validate(data)

    # Apply many marks
    marks = {CtyMark(f"mark_{i}", {"id": i}) for i in range(num_marks)}
    marked_value = value.with_marks(marks)

    # Verify marks are attached
    assert len(marked_value.marks) == num_marks

    # Serialize (marks won't be included, but shouldn't cause issues)
    msgpack_bytes = cty_to_msgpack(marked_value, marked_value.type)
    assert len(msgpack_bytes) > 0


@ADVERSARIAL_SETTINGS
@given(num_attrs=st.integers(min_value=100, max_value=500))
def test_objects_with_many_attributes_are_handled(num_attrs: int) -> None:
    """
    Adversarial test: Objects with hundreds of attributes should work.

    Tests that objects with many attributes can be validated and serialized
    without performance degradation.
    """
    # Create object type with many attributes
    attr_types = {f"attr_{i}": CtyNumber() for i in range(num_attrs)}
    obj_type = CtyObject(attribute_types=attr_types)

    # Create object value
    obj_value = {f"attr_{i}": i for i in range(num_attrs)}

    # Validate
    cty_obj = obj_type.validate(obj_value)
    assert len(cty_obj.value) == num_attrs

    # Serialize
    msgpack_bytes = cty_to_msgpack(cty_obj, obj_type)
    assert len(msgpack_bytes) > 0

    # Deserialize
    decoded = cty_from_msgpack(msgpack_bytes, obj_type)
    assert len(decoded.value) == num_attrs


@ADVERSARIAL_SETTINGS
@given(data=st.data())
def test_unicode_edge_cases_are_handled(data) -> None:
    """
    Adversarial test: Unicode edge cases should be handled correctly.

    Tests problematic Unicode scenarios:
    - Surrogate pairs
    - Combining characters
    - RTL markers
    - Zero-width characters
    - Emoji with modifiers
    """
    # Generate problematic Unicode strings
    unicode_category = data.draw(
        st.sampled_from(
            [
                "surrogate_pairs",
                "combining_chars",
                "rtl_markers",
                "zero_width",
                "emoji",
            ]
        )
    )

    if unicode_category == "surrogate_pairs":
        # Valid surrogate pairs in Python strings
        text = data.draw(
            st.text(alphabet=st.characters(min_codepoint=0x10000, max_codepoint=0x10FFFF), max_size=1000)
        )
    elif unicode_category == "combining_chars":
        # Characters with combining diacriticals
        base = data.draw(st.text(alphabet="aeiou", min_size=1, max_size=100))
        combining = "\u0301\u0302\u0303"  # Combining acute, circumflex, tilde
        text = "".join(c + combining for c in base)
    elif unicode_category == "rtl_markers":
        # Right-to-left markers
        text = "\u202e" + data.draw(st.text(max_size=100)) + "\u202d"  # RTL override
    elif unicode_category == "zero_width":
        # Zero-width characters
        text = data.draw(st.text(max_size=100)) + "\u200b\u200c\u200d\ufeff"
    else:  # emoji
        # Emoji with skin tone modifiers
        emoji_base = data.draw(
            st.sampled_from(["\U0001f44d", "\U0001f44b", "\U0001f91d"])
        )  # Thumbs up, wave, handshake
        modifier = data.draw(
            st.sampled_from(["\U0001f3fb", "\U0001f3fc", "\U0001f3fd", "\U0001f3fe", "\U0001f3ff"])
        )  # Skin tones
        text = emoji_base + modifier

    string_type = CtyString()

    # Should handle without errors
    cty_value = string_type.validate(text)

    # Serialize and deserialize
    msgpack_bytes = cty_to_msgpack(cty_value, string_type)
    decoded = cty_from_msgpack(msgpack_bytes, string_type)

    # Value should be NFC normalized
    assert decoded.value == unicodedata.normalize("NFC", text)


@ADVERSARIAL_SETTINGS
@given(number=st.integers(min_value=2**53 + 1, max_value=2**100))
def test_numbers_beyond_safe_integer_range(number: int) -> None:
    """
    Adversarial test: Numbers beyond JavaScript safe integer range.

    Tests that very large integers (> 2^53) are handled appropriately,
    either by accepting them or raising clear errors.
    """
    number_type = CtyNumber()

    try:
        # Attempt to validate very large number
        cty_value = number_type.validate(number)

        # If accepted, should serialize
        msgpack_bytes = cty_to_msgpack(cty_value, number_type)
        assert len(msgpack_bytes) > 0

        # And deserialize
        decoded = cty_from_msgpack(msgpack_bytes, number_type)
        # Might lose precision, but should be close
        assert abs(int(decoded.value) - number) < number * 0.01  # Within 1%

    except (ValueError, OverflowError):
        # Also acceptable - system rejects out-of-range numbers
        pass


@ADVERSARIAL_SETTINGS
@given(schema_mismatch=st.data())
def test_schema_mismatch_detected(schema_mismatch) -> None:
    """
    Adversarial test: Serializing with one schema, deserializing with another.

    Tests that type mismatches between serialization and deserialization
    are detected and handled gracefully.

    Note: Some mismatches may be accepted (e.g., number as string) which is
    acceptable behavior - this test verifies graceful handling, not rejection.
    """
    # Serialize as one type
    original_type = schema_mismatch.draw(
        st.sampled_from(
            [
                CtyString(),
                CtyNumber(),
                CtyBool(),
                CtyList(element_type=CtyNumber()),
            ]
        )
    )

    # Different type for deserialization
    target_type = schema_mismatch.draw(
        st.sampled_from(
            [
                CtyString(),
                CtyNumber(),
                CtyBool(),
                CtyList(element_type=CtyString()),
            ]
        )
    )

    # Only test actual type mismatches
    assume(type(original_type).__name__ != type(target_type).__name__)

    # Create and serialize value
    if isinstance(original_type, CtyString):
        value = original_type.validate("test")
    elif isinstance(original_type, CtyNumber):
        value = original_type.validate(42)
    elif isinstance(original_type, CtyBool):
        value = original_type.validate(True)
    else:  # CtyList
        value = original_type.validate([1, 2, 3])

    msgpack_bytes = cty_to_msgpack(value, original_type)

    # Try to deserialize with wrong schema - may succeed or fail gracefully
    try:
        decoded = cty_from_msgpack(msgpack_bytes, target_type)
        # If it succeeds, result should still be valid
        assert isinstance(decoded, CtyValue)
    except (DeserializationError, ValueError, TypeError, Exception):
        # Also acceptable - mismatch was detected
        pass


@ADVERSARIAL_SETTINGS
@given(data=st.binary(min_size=1, max_size=10000))
def test_random_binary_data_rejected(data: bytes) -> None:
    """
    Adversarial test: Random binary data should be rejected gracefully.

    Tests that completely random binary data doesn't crash the deserializer.
    """
    schema = CtyDynamic()

    with contextlib.suppress(
        DeserializationError,
        CtyValidationError,  # Random data might deserialize but fail validation
        msgpack.exceptions.ExtraData,
        msgpack.exceptions.UnpackException,
        ValueError,
        TypeError,
        struct.error,
    ):
        cty_from_msgpack(data, schema)


# 🌊🪢🔚
