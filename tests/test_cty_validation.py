import pytest

from unittest.mock import MagicMock, patch

from pyvider.cty.validation import ValidationContext, validate_schema


class TestValidationContext(unittest.TestCase):
    """Test the ValidationContext class."""

    def test_validation_context_init(self):
        """Test that ValidationContext initializes with empty lists."""
        ctx = ValidationContext()
        self.assertEqual(ctx.path, [])
        self.assertEqual(ctx.errors, [])
    
    def test_validation_context_custom_values(self):
        """Test initializing ValidationContext with custom values."""
        ctx = ValidationContext(path=["user", "address"], errors=["Invalid zip code"])
        self.assertEqual(ctx.path, ["user", "address"])
        self.assertEqual(ctx.errors, ["Invalid zip code"])


class TestValidateSchema(unittest.TestCase):
    """Test the validate_schema function."""
    
    def setUp(self):
        """Set up mocks for testing."""
        self.mock_schema = MagicMock()
        self.mock_field1 = MagicMock()
        self.mock_field2 = MagicMock()
        
        # Configure schema with fields
        self.mock_schema._fields = {
            "name": self.mock_field1,
            "age": self.mock_field2
        }
        
        # Configure field properties
        self.mock_field1.required = True
        self.mock_field2.required = False
    
    def test_validate_schema_valid_data(self):
        """Test schema validation with valid data."""
        data = {"name": "John", "age": 30}
        
        errors = validate_schema(self.mock_schema, data)
        
        # Assertions
        self.assertEqual(errors, [])
        self.mock_field1.validate.assert_called_once_with("John")
        self.mock_field2.validate.assert_called_once_with(30)
    
    def test_validate_schema_missing_required(self):
        """Test schema validation with missing required field."""
        data = {"age": 30}  # Missing required "name" field
        
        errors = validate_schema(self.mock_schema, data)
        
        # Assertions
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing required field: name", errors)
        self.mock_field1.validate.assert_not_called()
        self.mock_field2.validate.assert_called_once_with(30)
    
    def test_validate_schema_validation_failure(self):
        """Test schema validation with field validation failure."""
        data = {"name": "John", "age": "invalid"}
        
        # Make the age field validation fail
        self.mock_field2.validate.side_effect = ValueError("Age must be a number")
        
        errors = validate_schema(self.mock_schema, data)
        
        # Assertions
        self.assertEqual(len(errors), 1)
        self.assertIn("Validation failed for age:", errors[0])
        self.assertIn("Age must be a number", errors[0])
    
    def test_validate_schema_multiple_errors(self):
        """Test schema validation with multiple errors."""
        data = {"age": "invalid"}  # Missing name and invalid age
        
        # Make the age field validation fail
        self.mock_field2.validate.side_effect = ValueError("Age must be a number")
        
        errors = validate_schema(self.mock_schema, data)
        
        # Assertions
        self.assertEqual(len(errors), 2)
        self.assertIn("Missing required field: name", errors)
        self.assertIn("Validation failed for age:", errors[1])
    
    def test_validate_schema_empty_data(self):
        """Test schema validation with empty data."""
        data = {}
        
        errors = validate_schema(self.mock_schema, data)
        
        # Assertions
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing required field: name", errors)
    
    def test_validate_schema_none_values(self):
        """Test schema validation with None values."""
        data = {"name": None, "age": None}
        
        errors = validate_schema(self.mock_schema, data)
        
        # Assertions
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing required field: name", errors)
        self.mock_field1.validate.assert_not_called()
        self.mock_field2.validate.assert_not_called()
    
    def test_validate_schema_extra_fields(self):
        """Test schema validation with extra fields not in schema."""
        data = {"name": "John", "age": 30, "email": "john@example.com"}
        
        errors = validate_schema(self.mock_schema, data)
        
        # Assertions
        self.assertEqual(errors, [])  # Extra fields are ignored
        self.mock_field1.validate.assert_called_once_with("John")
        self.mock_field2.validate.assert_called_once_with(30)
