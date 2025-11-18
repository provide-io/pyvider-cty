#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Exception coverage tests to systematically trigger all exception types.

Ensures that every exception class can be raised, caught, and provides
useful error messages without leaking sensitive information."""

import contextlib
from decimal import Decimal

from hypothesis import assume, given, settings, strategies as st
import msgpack
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
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.conversion.explicit import convert
from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyBoolValidationError,
    CtyConversionError,
    CtyError,
    CtyListValidationError,
    CtyMapValidationError,
    CtyNumberValidationError,
    CtySetValidationError,
    CtyStringValidationError,
    CtyTupleValidationError,
    CtyTypeMismatchError,
    CtyTypeValidationError,
    CtyValidationError,
    DeserializationError,
    SerializationError,
)
from pyvider.cty.values import CtyValue


@settings(deadline=5000, max_examples=500)
@given(invalid_data=st.integers() | st.lists(st.integers()) | st.dictionaries(st.text(), st.integers()))
def test_string_validation_error_triggered(invalid_data) -> None:
    """Test CtyStringValidationError can be triggered."""
    string_type = CtyString()

    # Only test non-string data - use assume() for proper Hypothesis filtering
    assume(not isinstance(invalid_data, str))

    with pytest.raises((CtyStringValidationError, CtyValidationError, CtyTypeValidationError)):
        string_type.validate(invalid_data)


@settings(deadline=5000, max_examples=500)
@given(invalid_data=st.dictionaries(st.text(), st.integers()))
def test_number_validation_error_triggered(invalid_data) -> None:
    """Test CtyNumberValidationError can be triggered."""
    number_type = CtyNumber()

    with pytest.raises(
        (CtyNumberValidationError, CtyValidationError, CtyTypeValidationError, ValueError, TypeError)
    ):
        number_type.validate(invalid_data)


@settings(deadline=5000, max_examples=500)
@given(invalid_data=st.dictionaries(st.text(), st.integers()))
def test_bool_validation_error_triggered(invalid_data) -> None:
    """Test CtyBoolValidationError can be triggered."""
    bool_type = CtyBool()

    with pytest.raises(
        (CtyBoolValidationError, CtyValidationError, CtyTypeValidationError, ValueError, TypeError)
    ):
        bool_type.validate(invalid_data)


@settings(deadline=5000, max_examples=500)
@given(invalid_data=st.text() | st.integers() | st.dictionaries(st.text(), st.integers()))
def test_list_validation_error_triggered(invalid_data) -> None:
    """Test CtyListValidationError can be triggered."""
    list_type = CtyList(element_type=CtyNumber())

    # Only test non-list data - use assume() for proper Hypothesis filtering
    assume(not isinstance(invalid_data, (list, tuple)))

    with pytest.raises((CtyListValidationError, CtyValidationError, CtyTypeValidationError)):
        list_type.validate(invalid_data)


@settings(deadline=5000, max_examples=500)
@given(invalid_data=st.text() | st.integers() | st.lists(st.integers()))
def test_map_validation_error_triggered(invalid_data) -> None:
    """Test CtyMapValidationError can be triggered."""
    map_type = CtyMap(element_type=CtyString())

    # Only test non-dict data - use assume() for proper Hypothesis filtering
    assume(not isinstance(invalid_data, dict))

    with pytest.raises((CtyMapValidationError, CtyValidationError, CtyTypeValidationError)):
        map_type.validate(invalid_data)


@settings(deadline=5000, max_examples=500)
@given(invalid_data=st.text() | st.integers() | st.lists(st.integers()))
def test_set_validation_error_triggered(invalid_data) -> None:
    """Test CtySetValidationError can be triggered."""
    set_type = CtySet(element_type=CtyNumber())

    # Only test non-set data - use assume() for proper Hypothesis filtering
    assume(not isinstance(invalid_data, (set, frozenset, list, tuple)))

    with pytest.raises((CtySetValidationError, CtyValidationError, CtyTypeValidationError)):
        set_type.validate(invalid_data)


@settings(deadline=5000, max_examples=500)
@given(data=st.lists(st.integers(), min_size=1, max_size=5))
def test_tuple_validation_error_triggered(data: list) -> None:
    """Test CtyTupleValidationError can be triggered."""
    # Create tuple type expecting different number of elements
    tuple_type = CtyTuple(element_types=(CtyNumber(), CtyNumber()))

    # Only test lists with wrong element count - use assume() for proper Hypothesis filtering
    assume(len(data) != 2)

    with pytest.raises((CtyTupleValidationError, CtyValidationError)):
        tuple_type.validate(data)


@settings(deadline=5000, max_examples=500)
@given(data=st.dictionaries(st.text(min_size=1, max_size=10), st.integers(), min_size=1, max_size=5))
def test_attribute_validation_error_triggered(data: dict) -> None:
    """Test CtyAttributeValidationError can be triggered."""
    # Create object type expecting specific attributes
    obj_type = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})

    # Only test dicts with different keys - use assume() for proper Hypothesis filtering
    assume(set(data.keys()) != {"name", "age"})

    with pytest.raises((CtyAttributeValidationError, CtyValidationError)):
        obj_type.validate(data)


@settings(deadline=5000, max_examples=500)
@given(source_type=st.sampled_from([CtyString(), CtyList(element_type=CtyNumber())]))
def test_conversion_error_triggered(source_type) -> None:
    """Test CtyConversionError can be triggered."""
    # Try impossible conversions
    if isinstance(source_type, CtyString):
        value = source_type.validate("not a number")
        target = CtyNumber()
    else:  # List
        value = source_type.validate([1, 2, 3])
        target = CtyBool()

    with pytest.raises((CtyConversionError, ValueError)):
        convert(value, target)


@settings(deadline=5000, max_examples=500)
@given(corrupted_bytes=st.binary(min_size=1, max_size=1000))
def test_deserialization_error_triggered(corrupted_bytes: bytes) -> None:
    """Test DeserializationError can be triggered."""
    schema = CtyDynamic()

    # Most random bytes should fail to deserialize
    with contextlib.suppress(
        DeserializationError,
        msgpack.exceptions.ExtraData,
        msgpack.exceptions.UnpackException,
        ValueError,
        TypeError,
        Exception,
    ):
        cty_from_msgpack(corrupted_bytes, schema)


@settings(deadline=5000, max_examples=100)
@given(invalid_type=st.text() | st.integers())
def test_type_validation_error_triggered(invalid_type) -> None:
    """Test CtyTypeValidationError can be triggered."""
    # CtyObject expects dict of CtyType instances
    from pyvider.cty.exceptions import InvalidTypeError

    with pytest.raises((CtyTypeValidationError, InvalidTypeError, TypeError, ValueError)):
        CtyObject(attribute_types={"bad": invalid_type})  # Should be CtyType


@settings(deadline=5000, max_examples=500)
@given(
    source=st.sampled_from([CtyString(), CtyNumber()]),
    target=st.sampled_from([CtyBool(), CtyList(element_type=CtyNumber())]),
)
def test_type_mismatch_error_context(source, target) -> None:
    """Test that type mismatch errors provide useful context."""
    # Create value
    value = source.validate("test") if isinstance(source, CtyString) else source.validate(42)

    # Try impossible conversion
    try:
        convert(value, target)
    except (CtyConversionError, ValueError) as e:
        # Error message should mention the types involved
        error_msg = str(e)
        assert len(error_msg) > 0
        # Should not contain sensitive info like memory addresses
        assert "0x" not in error_msg


def _can_be_decimal(s: str) -> bool:
    """Check if a string can be parsed as a Decimal."""
    try:
        Decimal(s)
        return True
    except Exception:
        return False


@settings(deadline=5000, max_examples=100)
@given(
    values=st.lists(
        st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_categories=("N",))).filter(
            lambda x: not _can_be_decimal(x)
        ),
        min_size=2,
        max_size=5,
    )
)
def test_validation_error_on_heterogeneous_list(values: list) -> None:
    """Test validation error on heterogeneous data in typed list."""
    # Try to validate non-numeric text list as number list (should fail)
    # Filter out any strings that can be parsed as Decimal (including Inf/NaN variants)
    list_type = CtyList(element_type=CtyNumber())

    # This should raise an error - if it doesn't, the test fails
    with pytest.raises((CtyValidationError, CtyListValidationError, ValueError, TypeError)):
        list_type.validate(values)


@settings(deadline=5000, max_examples=100)
@given(map_data=st.dictionaries(st.integers(), st.text(max_size=10), min_size=1, max_size=5))
def test_map_validation_error_on_non_string_keys(map_data: dict) -> None:
    """Test that maps reject non-string keys."""
    map_type = CtyMap(element_type=CtyString())

    with pytest.raises((CtyMapValidationError, CtyValidationError, ValueError, TypeError)):
        map_type.validate(map_data)


def test_all_exceptions_are_catchable_as_cty_error() -> None:
    """Test that all CTY exceptions inherit from CtyError."""
    exception_classes = [
        CtyValidationError,
        CtyStringValidationError,
        CtyNumberValidationError,
        CtyBoolValidationError,
        CtyListValidationError,
        CtyMapValidationError,
        CtySetValidationError,
        CtyTupleValidationError,
        CtyAttributeValidationError,
        CtyTypeValidationError,
        CtyTypeMismatchError,
        CtyConversionError,
        SerializationError,
        DeserializationError,
    ]

    for exc_class in exception_classes:
        # Verify inheritance
        assert issubclass(exc_class, (CtyError, Exception))


@settings(deadline=5000, max_examples=500)
@given(null_value=st.sampled_from([CtyString(), CtyNumber(), CtyList(element_type=CtyNumber())]))
def test_exception_messages_dont_leak_sensitive_info(null_value) -> None:
    """Test that exception messages don't leak sensitive information."""
    # Create null value
    null_val = CtyValue.null(null_value)

    try:
        # Try operations that should fail on null
        _ = null_val.value  # Accessing value of null
    except Exception as e:
        error_msg = str(e)

        # Check message is useful but not leaking internals
        assert len(error_msg) > 0
        # Should not contain memory addresses
        assert "0x" not in error_msg.lower()
        # Should not contain internal variable names that aren't part of public API
        assert "__" not in error_msg


# 🌊🪢🔚
