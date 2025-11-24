#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Comprehensive test suite for error context integration with provide-foundation.

This test suite validates that all error boundaries and enhanced error contexts
are working correctly across the pyvider-cty codebase."""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValidationError,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.conversion import convert
from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyFunctionError,
    CtyListValidationError,
    CtyMapValidationError,
    CtyStringValidationError,
)
from pyvider.cty.exceptions.encoding import DeserializationError
from pyvider.cty.functions.collection_functions import (
    concat,
    element,
    keys,
    length,
)
from pyvider.cty.parser import parse_tf_type_to_ctytype


class TestConversionErrorContext:
    """Test error context for type conversion operations."""

    def test_conversion_error_has_rich_context(self) -> None:
        """Test that conversion errors include rich context information."""
        string_val = CtyString().validate("not_a_number")

        with pytest.raises(Exception) as exc_info:
            convert(string_val, CtyNumber())

        # Should have conversion context
        error = exc_info.value
        assert hasattr(error, "context") or "conversion" in str(error).lower()

    def test_conversion_bool_error_context(self) -> None:
        """Test boolean conversion error context."""
        string_val = CtyString().validate("invalid_bool")

        with pytest.raises(Exception) as exc_info:
            convert(string_val, CtyBool())

        error = exc_info.value
        assert "bool" in str(error).lower()


class TestValidationErrorContext:
    """Test enhanced error context for validation operations."""

    def test_string_validation_error_context(self) -> None:
        """Test string validation with enhanced error context."""
        string_type = CtyString()

        class BadValue:
            def __str__(self) -> str:
                raise ValueError("Cannot convert to string")

        with pytest.raises(CtyStringValidationError) as exc_info:
            string_type.validate(BadValue())

        error = exc_info.value
        assert hasattr(error, "context") or "BadValue" in str(error)

    def test_list_validation_nested_error_context(self) -> None:
        """Test list validation with nested error context."""
        list_type = CtyList(element_type=CtyString())

        class BadElement:
            def __str__(self) -> str:
                raise ValueError("Bad element")

        with pytest.raises(CtyListValidationError) as exc_info:
            list_type.validate(["good", BadElement(), "also_good"])

        error = exc_info.value
        # Should indicate which element failed
        assert "[1]" in str(error) or "index 1" in str(error).lower()

    def test_map_validation_error_context(self) -> None:
        """Test map validation with key-specific error context."""
        map_type = CtyMap(element_type=CtyString())

        class BadValue:
            def __str__(self) -> str:
                raise ValueError("Bad map value")

        with pytest.raises(CtyMapValidationError) as exc_info:
            map_type.validate({"good": "value", "bad": BadValue()})

        error = exc_info.value
        # Should indicate which key failed
        assert "bad" in str(error).lower()

    def test_object_validation_error_context(self) -> None:
        """Test object validation with attribute-specific error context."""
        obj_type = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})

        with pytest.raises(CtyAttributeValidationError) as exc_info:
            obj_type.validate({"name": "Alice"})  # Missing required attribute

        error = exc_info.value
        assert "age" in str(error) or "Missing" in str(error)


class TestFunctionErrorContext:
    """Test error context for CTY standard library functions."""

    def test_length_function_error_context(self) -> None:
        """Test length function with invalid input type."""
        number_val = CtyNumber().validate(42)

        with pytest.raises(CtyFunctionError) as exc_info:
            length(number_val)

        error = exc_info.value
        assert "length" in str(error) and "number" in str(error).lower()

    def test_keys_function_error_context(self) -> None:
        """Test keys function with invalid input type."""
        string_val = CtyString().validate("not_a_map")

        with pytest.raises(CtyFunctionError) as exc_info:
            keys(string_val)

        error = exc_info.value
        assert "keys" in str(error) and "string" in str(error).lower()

    def test_element_function_error_context(self) -> None:
        """Test element function with invalid collection type."""
        string_val = CtyString().validate("not_a_list")
        index_val = CtyNumber().validate(0)

        with pytest.raises(CtyFunctionError) as exc_info:
            element(string_val, index_val)

        error = exc_info.value
        assert "element" in str(error) and "string" in str(error).lower()


class TestParserErrorContext:
    """Test error context for Terraform type parsing."""

    def test_invalid_primitive_type_error_context(self) -> None:
        """Test parsing invalid primitive type."""
        with pytest.raises(CtyValidationError) as exc_info:
            parse_tf_type_to_ctytype("invalid_type")

        error = exc_info.value
        assert "invalid_type" in str(error)

    def test_malformed_complex_type_error_context(self) -> None:
        """Test parsing malformed complex type specification."""
        with pytest.raises(CtyValidationError) as exc_info:
            parse_tf_type_to_ctytype(["list"])  # Missing element type

        error = exc_info.value
        assert "Invalid" in str(error) or "specification" in str(error)


class TestCodecErrorContext:
    """Test error context for serialization/deserialization."""

    def test_serialization_with_context(self) -> None:
        """Test that serialization operations include context."""
        # This should work normally, testing the error boundary is active
        string_val = CtyString().validate("test")
        data = cty_to_msgpack(string_val, CtyString())
        result = cty_from_msgpack(data, CtyString())
        assert result.raw_value == "test"

    def test_deserialization_invalid_data(self) -> None:
        """Test deserialization with invalid data."""
        with pytest.raises((DeserializationError, ValueError)):
            cty_from_msgpack(b"invalid_msgpack_data", CtyString())


class TestCompositeErrorContext:
    """Test error context in complex nested scenarios."""

    def test_complex_nested_validation_error_chain(self) -> None:
        """Test error context propagation through complex nested structures."""
        user_type = CtyObject(
            attribute_types={
                "profile": CtyObject(attribute_types={"settings": CtyMap(element_type=CtyString())})
            }
        )

        class BadValue:
            def __str__(self) -> str:
                raise ValueError("Bad nested value")

        with pytest.raises(CtyAttributeValidationError) as exc_info:
            user_type.validate({"profile": {"settings": {"theme": BadValue()}}})

        error = exc_info.value
        # Should show the full path to the error
        assert "profile" in str(error) or "settings" in str(error) or "theme" in str(error)

    def test_function_with_validation_error_chain(self) -> None:
        """Test function error context with underlying validation errors."""
        # Create a list with mixed valid/invalid elements for concat
        list1 = CtyList(element_type=CtyString()).validate(["valid"])
        list2 = CtyList(element_type=CtyString()).validate(["also_valid"])

        # This should work - testing error boundary presence
        result = concat(list1, list2)
        assert len(result.raw_value) == 2


class TestErrorRecoveryAndBoundaries:
    """Test that error boundaries don't interfere with normal operation."""

    def test_normal_operations_still_work(self) -> None:
        """Ensure error boundaries don't break normal functionality."""
        # Basic type validation
        string_val = CtyString().validate("hello")
        assert string_val.raw_value == "hello"

        # Collection operations
        list_val = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        length_val = length(list_val)
        assert length_val.raw_value == 3

        # Type conversion
        converted = convert(string_val, CtyString())  # Identity conversion
        assert converted.raw_value == "hello"

        # Type parsing
        parsed_type = parse_tf_type_to_ctytype("string")
        assert isinstance(parsed_type, CtyString)

    def test_error_boundaries_preserve_original_error_types(self) -> None:
        """Ensure error boundaries don't change the error types being raised."""
        with pytest.raises(CtyStringValidationError):
            CtyString().validate(123)  # Should still raise CtyStringValidationError

        with pytest.raises(CtyFunctionError):
            length(CtyNumber().validate(42))  # Should still raise CtyFunctionError


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# 🌊🪢🔚
