import pytest
from pyvider.cty.exceptions.conversion import CtyConversionError, CtyTypeConversionError
from pyvider.cty.types import CtyString # For a sample target_type

class TestConversionExceptions:

    def test_cty_conversion_error_basic(self):
        """Test CtyConversionError with just a message."""
        error = CtyConversionError("Basic conversion error")
        assert "Basic conversion error" in str(error)
        assert error.source_value is None
        assert error.target_type is None

    def test_cty_conversion_error_with_source(self):
        """Test CtyConversionError with a source_value."""
        source = [1, 2, 3]
        error = CtyConversionError("Conversion error with source", source_value=source)
        assert "Conversion error with source (source_type=list)" in str(error)
        assert error.source_value == source

    def test_cty_conversion_error_with_target_type(self):
        """Test CtyConversionError with a target_type."""
        target = CtyString
        error = CtyConversionError("Conversion error with target", target_type=target)
        assert f"Conversion error with target (target_type={target.__name__})" in str(error)
        assert error.target_type == target

    def test_cty_conversion_error_with_target_type_no_name(self):
        """Test CtyConversionError with a target_type that has no __name__."""
        class NoNameType:
            pass
        target = NoNameType() # instance, not class
        error = CtyConversionError("Conversion error with target no name", target_type=target)
        assert f"Conversion error with target no name (target_type={str(target)})" in str(error)
        assert error.target_type == target

    def test_cty_conversion_error_with_source_and_target(self):
        """Test CtyConversionError with both source_value and target_type."""
        source = 123
        target = CtyString
        error = CtyConversionError("Full conversion error", source_value=source, target_type=target)
        assert f"Full conversion error (source_type=int, target_type={target.__name__})" in str(error)
        assert error.source_value == source
        assert error.target_type == target

    def test_cty_type_conversion_error_basic(self):
        """Test CtyTypeConversionError with just a message."""
        error = CtyTypeConversionError("Basic type conversion error")
        assert "Basic type conversion error" in str(error) # Message is not prefixed if type_name is None
        assert error.type_name is None

    def test_cty_type_conversion_error_with_type_name(self):
        """Test CtyTypeConversionError with a type_name."""
        type_name = "MyCustomType"
        error = CtyTypeConversionError("Specific error", type_name=type_name)
        assert f'CTY Type "{type_name}" representation conversion failed: Specific error' in str(error)
        assert error.type_name == type_name

    def test_cty_type_conversion_error_with_all_params(self):
        """Test CtyTypeConversionError with all parameters."""
        type_name = "AnotherType"
        source = {"key": "val"}
        target = CtyString
        error = CtyTypeConversionError(
            "Full type conversion error",
            type_name=type_name,
            source_value=source,
            target_type=target
        )
        expected_msg_part1 = f'CTY Type "{type_name}" representation conversion failed: Full type conversion error'
        expected_msg_part2 = f"(source_type=dict, target_type={target.__name__})"
        assert expected_msg_part1 in str(error)
        assert expected_msg_part2 in str(error)
        assert error.type_name == type_name
        assert error.source_value == source
        assert error.target_type == target

    def test_cty_type_conversion_error_inherits_cty_conversion_error(self):
        """Check that CtyTypeConversionError is a CtyConversionError."""
        error = CtyTypeConversionError("Test inheritance")
        assert isinstance(error, CtyConversionError)

    def test_cty_conversion_error_no_context_parts(self):
        """Ensure message remains unchanged if no context parts are added."""
        original_message = "Error without context"
        error = CtyConversionError(original_message, source_value=None, target_type=None)
        assert str(error) == original_message

    def test_cty_type_conversion_error_no_type_name_with_context(self):
        """Test CtyTypeConversionError without type_name but with other context."""
        source = 123
        target = CtyString
        error = CtyTypeConversionError("Error without type_name", source_value=source, target_type=target)
        # Message should not have the "CTY Type..." prefix, but should have context parts
        assert "Error without type_name (source_type=int, target_type=CtyString)" in str(error)
        assert "CTY Type" not in str(error) # Ensure prefix is missing
        assert error.type_name is None
        assert error.source_value == source
        assert error.target_type == target
