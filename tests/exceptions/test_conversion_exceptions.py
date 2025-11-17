#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pyvider.cty.exceptions.conversion import (
    CtyConversionError,
    CtyTypeConversionError,
    CtyTypeParseError,
)
from pyvider.cty.types import CtyList, CtyNumber, CtyString


class TestCtyConversionError:
    def test_instantiation_with_message_only(self) -> None:
        """Test CtyConversionError with message only."""
        error = CtyConversionError("Base conversion error")
        assert str(error) == "Base conversion error"
        assert error.source_value is None
        assert error.target_type is None

    def test_instantiation_with_source_value(self) -> None:
        """Test CtyConversionError with message and source_value."""
        source = 123
        error = CtyConversionError("Conversion failed", source_value=source)
        expected_msg = "Conversion failed (source_type=int)"
        assert str(error) == expected_msg
        assert error.source_value == source
        assert error.target_type is None

    def test_instantiation_with_target_type_with_name(self) -> None:
        """Test CtyConversionError with message and target_type that has __name__."""
        target = CtyString
        error = CtyConversionError("Conversion failed", target_type=target)
        expected_msg = "Conversion failed (target_type=CtyString)"
        assert str(error) == expected_msg
        assert error.source_value is None
        assert error.target_type == target

    def test_instantiation_with_target_type_without_name(self) -> None:
        """Test CtyConversionError with message and target_type that is a string."""
        target_str = "some_type_string"
        error = CtyConversionError("Conversion failed", target_type=target_str)
        expected_msg = f"Conversion failed (target_type={target_str})"
        assert str(error) == expected_msg
        assert error.source_value is None
        assert error.target_type == target_str

        class SimpleClass:
            pass

        target_instance = SimpleClass()
        error_instance = CtyConversionError("Conversion failed", target_type=target_instance)
        expected_msg_instance = f"Conversion failed (target_type={target_instance!s})"
        assert str(error_instance) == expected_msg_instance

    def test_instantiation_with_all_params(self) -> None:
        """Test CtyConversionError with message, source_value, and target_type."""
        source = 456.7
        target = CtyNumber
        error = CtyConversionError("Full context conversion error", source_value=source, target_type=target)
        expected_msg = "Full context conversion error (source_type=float, target_type=CtyNumber)"
        assert str(error) == expected_msg
        assert error.source_value == source
        assert error.target_type == target


class TestCtyTypeConversionError:
    def test_instantiation_with_type_name(self) -> None:
        """Test CtyTypeConversionError with message and type_name."""
        error = CtyTypeConversionError("Type specific error", type_name="MyCustomType")
        expected_msg_part = 'CTY Type "MyCustomType" representation conversion failed: Type specific error'
        assert str(error).startswith(expected_msg_part)
        assert error.type_name == "MyCustomType"
        assert error.source_value is None
        assert error.target_type is None

    def test_instantiation_without_type_name(self) -> None:
        """Test CtyTypeConversionError with message but no type_name."""
        error = CtyTypeConversionError("Generic type error")
        assert str(error) == "Generic type error"  # No type_name prefix
        assert error.type_name is None

    def test_instantiation_with_type_name_and_source_value(self) -> None:
        """Test CtyTypeConversionError with type_name and source_value."""
        source = "test_source"
        error = CtyTypeConversionError("Type error with source", type_name="SourceType", source_value=source)
        expected_msg = (
            'CTY Type "SourceType" representation conversion failed: Type error with source (source_type=str)'
        )
        assert str(error) == expected_msg
        assert error.type_name == "SourceType"
        assert error.source_value == source
        assert error.target_type is None

    def test_instantiation_with_type_name_and_target_type(self) -> None:
        """Test CtyTypeConversionError with type_name and target_type."""
        target = CtyString
        error = CtyTypeConversionError("Type error with target", type_name="TargetingType", target_type=target)
        expected_msg = 'CTY Type "TargetingType" representation conversion failed: Type error with target (target_type=CtyString)'
        assert str(error) == expected_msg
        assert error.type_name == "TargetingType"
        assert error.source_value is None
        assert error.target_type == target

    def test_instantiation_without_type_name_all_conversion_params(self) -> None:
        """Test CtyTypeConversionError without type_name but with CtyConversionError params."""
        source = 123
        target = CtyNumber
        error = CtyTypeConversionError("Conversion part only", source_value=source, target_type=target)
        expected_msg = "Conversion part only (source_type=int, target_type=CtyNumber)"
        assert str(error) == expected_msg
        assert error.type_name is None
        assert error.source_value == source
        assert error.target_type == target

    def test_instantiation_with_all_params(self) -> None:
        """Test CtyTypeConversionError with all possible parameters."""
        type_name = "ComplexScenarioType"
        source = [1, 2]
        target = CtyList  # Now CtyList is defined
        error = CtyTypeConversionError(
            "Full context type error",
            type_name=type_name,
            source_value=source,
            target_type=target,
        )
        expected_msg = 'CTY Type "ComplexScenarioType" representation conversion failed: Full context type error (source_type=list, target_type=CtyList)'
        assert str(error) == expected_msg
        assert error.type_name == type_name
        assert error.source_value == source
        assert error.target_type == target


class TestCtyTypeParseError:
    def test_instantiation(self) -> None:
        """Test CtyTypeParseError instantiation."""
        type_string = "list(string"
        error = CtyTypeParseError("Invalid type string", type_string=type_string)
        expected_msg = f"Invalid type string: '{type_string}' (source_type=str)"
        assert str(error) == expected_msg
        assert error.type_string == type_string
        assert error.source_value == type_string


# 🌊🪢🔚
