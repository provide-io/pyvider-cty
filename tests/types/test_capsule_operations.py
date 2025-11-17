#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD Test Suite for CtyCapsule with custom operations.

These tests define the behavior for a capsule type that can be equipped with
custom logic for equality, hashing, and other operations, mirroring the
`CapsuleWithOps` feature from go-cty."""

from typing import Any
from unittest.mock import Mock

from attrs import define
import pytest

from pyvider.cty import (
    CtyCapsule,
    CtyCapsuleWithOps,
    CtyNumber,
    CtyString,
    CtyType,
    CtyValue,
    convert,
)
from pyvider.cty.exceptions import CtyConversionError
from pyvider.cty.marks import CtyMark


@define(frozen=True)
class OpaqueObject:
    """A simple class to be encapsulated."""

    id: int
    data: str


class TestCtyCapsuleWithEqAndHash:
    def test_equality_uses_custom_equal_fn(self) -> None:
        # Use a mock as a "spy" to track calls to a real lambda
        call_tracker = Mock()

        def my_equal_fn(a: Any, b: Any) -> bool:
            call_tracker(a, b)
            return True

        capsule_type = CtyCapsuleWithOps("Opaque", OpaqueObject, equal_fn=my_equal_fn)
        val1 = capsule_type.validate(OpaqueObject(1, "foo"))
        val2 = capsule_type.validate(OpaqueObject(2, "bar"))
        assert val1 == val2
        call_tracker.assert_called_once_with(val1.value, val2.value)

    def test_hash_uses_custom_hash_fn(self) -> None:
        # Use a mock as a "spy" to track calls to a real lambda
        call_tracker = Mock()

        def my_hash_fn(a: Any) -> int:
            call_tracker(a)
            return 42

        capsule_type = CtyCapsuleWithOps("Opaque", OpaqueObject, hash_fn=my_hash_fn)
        val = capsule_type.validate(OpaqueObject(1, "foo"))
        assert hash(val) == 42
        call_tracker.assert_called_once_with(val.value)

    def test_base_capsule_and_ops_capsule_are_not_equal(self) -> None:
        base_type = CtyCapsule("Opaque", OpaqueObject)
        ops_type = CtyCapsuleWithOps("Opaque", OpaqueObject)
        assert not base_type.equal(ops_type)
        assert not ops_type.equal(base_type)


class TestCtyCapsuleWithConversion:
    """TDD for capsules with custom conversion logic."""

    @pytest.fixture
    def mock_convert_fn(self) -> Mock:
        # By default, the mock cannot handle any conversion.
        return Mock(return_value=None)

    @pytest.fixture
    def capsule_type_with_converter(self, mock_convert_fn: Mock) -> CtyCapsuleWithOps:
        # Use a real lambda that calls the mock to satisfy the arity check
        def convert_wrapper(val: Any, target_type: CtyType) -> CtyValue | None:
            return mock_convert_fn(val, target_type)

        return CtyCapsuleWithOps("Opaque", OpaqueObject, convert_fn=convert_wrapper)

    def test_successful_conversion_uses_custom_fn(
        self, capsule_type_with_converter: CtyCapsuleWithOps, mock_convert_fn: Mock
    ) -> None:
        """TDD: Verifies that `convert` delegates to the capsule's `convert_fn`."""
        opaque_obj = OpaqueObject(id=1, data="test-data")
        capsule_val = capsule_type_with_converter.validate(opaque_obj)
        target_type = CtyString()

        # Configure the mock to handle this specific conversion
        expected_result = CtyValue(target_type, "ID:1|DATA:test-data")
        mock_convert_fn.return_value = expected_result

        # Perform the conversion
        result = convert(capsule_val, target_type)

        # Assert that the custom function was called correctly
        mock_convert_fn.assert_called_once_with(opaque_obj, target_type)
        # Assert that the result is what the custom function returned
        assert result == expected_result

    def test_unhandled_conversion_fails(
        self, capsule_type_with_converter: CtyCapsuleWithOps, mock_convert_fn: Mock
    ) -> None:
        """TDD: Verifies conversion fails if the `convert_fn` can't handle it."""
        capsule_val = capsule_type_with_converter.validate(OpaqueObject(1, "d"))
        target_type = CtyNumber()  # A type our mock is not configured for

        # The mock will return None, its default
        with pytest.raises(CtyConversionError):
            convert(capsule_val, target_type)

        # Assert that the custom function was still called
        mock_convert_fn.assert_called_once()

    def test_conversion_on_capsule_without_converter_fails(self) -> None:
        """TDD: Verifies conversion fails if no `convert_fn` is defined."""
        capsule_type = CtyCapsuleWithOps("Opaque", OpaqueObject)  # No convert_fn
        capsule_val = capsule_type.validate(OpaqueObject(1, "d"))

        with pytest.raises(CtyConversionError):
            convert(capsule_val, CtyString())

    def test_conversion_preserves_marks(
        self, capsule_type_with_converter: CtyCapsuleWithOps, mock_convert_fn: Mock
    ) -> None:
        """TDD: Verifies that marks are carried over after a custom conversion."""
        marked_val = capsule_type_with_converter.validate(OpaqueObject(1, "d")).mark(CtyMark("sensitive"))
        target_type = CtyString()

        # Configure mock to return an unmarked value
        unmarked_result = CtyValue(target_type, "converted")
        mock_convert_fn.return_value = unmarked_result

        result = convert(marked_val, target_type)

        # The final result should have the original marks
        assert result.has_mark(CtyMark("sensitive"))
        assert result.value == "converted"

    def test_conversion_fails_if_custom_fn_returns_wrong_type(
        self, capsule_type_with_converter: CtyCapsuleWithOps, mock_convert_fn: Mock
    ) -> None:
        """TDD: Verifies `convert` is robust against a misbehaving `convert_fn`."""
        capsule_val = capsule_type_with_converter.validate(OpaqueObject(1, "d"))
        target_type = CtyString()

        # Configure mock to return a value of the wrong type
        wrong_result = CtyValue(CtyNumber(), 123)
        mock_convert_fn.return_value = wrong_result

        with pytest.raises(CtyConversionError, match="returned a value of the wrong type"):
            convert(capsule_val, target_type)


# 🌊🪢🔚
