
from decimal import Decimal
from unittest.mock import MagicMock, patch

from pyvider.cty.convert.primitive import string_to_number


class TestPrimitiveConversions():
    """Test primitive type conversions."""
    
    def setUp(self):
        """Set up objects for testing."""
        # Mock Value, String, and Number classes
        self.mock_value = MagicMock()
        self.mock_string = MagicMock()
        self.mock_number = MagicMock()
        
        # Configure mock value properties
        self.mock_value.is_known = True
        self.mock_value.is_null = False
        self.mock_value._value = "123.45"
        self.mock_value._marks = frozenset()
    
    def test_string_to_number_known_value(self):
        """Test converting a known string value to number."""
        # Call string_to_number
        with patch('pyvider.cty.convert.primitive.Number', return_value=self.mock_number):
            with patch('pyvider.cty.convert.primitive.Value') as mock_value_class:
                # Set up mock return value
                mock_value_instance = MagicMock()
                mock_value_class.return_value = mock_value_instance
                
                # Configure Decimal
                with patch('pyvider.cty.convert.primitive.Decimal') as mock_decimal:
                    mock_decimal.return_value = Decimal("123.45")
                    
                    # Call string_to_number
                    result = string_to_number(self.mock_value)
                    
                    # Assertions
                    mock_decimal.assert_called_once_with("123.45")
                    mock_value_class.assert_called_once_with(
                        self.mock_number, 
                        Decimal("123.45"),
                        marks=self.mock_value._marks
                    )
                    self.assertEqual(result, mock_value_instance)
    
    def test_string_to_number_unknown_value(self):
        """Test converting an unknown string value to number."""
        # Configure mock to be unknown
        self.mock_value.is_known = False
        
        # Call string_to_number
        with patch('pyvider.cty.convert.primitive.Number', return_value=self.mock_number):
            with patch('pyvider.cty.convert.primitive.unknown_val') as mock_unknown_val:
                # Set up mock return value
                mock_unknown_val.return_value = "unknown_number"
                
                # Call string_to_number
                result = string_to_number(self.mock_value)
                
                # Assertions
                mock_unknown_val.assert_called_once_with(self.mock_number)
                self.assertEqual(result, "unknown_number")
    
    def test_string_to_number_null_value(self):
        """Test converting a null string value to number."""
        # Configure mock to be null
        self.mock_value.is_null = True
        
        # Call string_to_number
        with patch('pyvider.cty.convert.primitive.Number', return_value=self.mock_number):
            with patch('pyvider.cty.convert.primitive.null_val') as mock_null_val:
                # Set up mock return value
                mock_null_val.return_value = "null_number"
                
                # Call string_to_number
                result = string_to_number(self.mock_value)
                
                # Assertions
                mock_null_val.assert_called_once_with(self.mock_number)
                self.assertEqual(result, "null_number")
    
    def test_string_to_number_invalid_string(self):
        """Test converting an invalid string value to number."""
        # Configure mock with invalid number string
        self.mock_value._value = "not_a_number"
        
        # Call string_to_number
        with patch('pyvider.cty.convert.primitive.Number', return_value=self.mock_number):
            with patch('pyvider.cty.convert.primitive.Decimal') as mock_decimal:
                # Make Decimal raise an exception
                mock_decimal.side_effect = ValueError("Invalid literal for Decimal")
                
                # Call string_to_number
                with self.assertRaises(ValueError):
                    string_to_number(self.mock_value)
    
    def test_string_to_number_with_marks(self):
        """Test that marks are preserved when converting string to number."""
        # Configure mock with marks
        self.mock_value._marks = frozenset(["sensitive", "encrypted"])
        
        # Call string_to_number
        with patch('pyvider.cty.convert.primitive.Number', return_value=self.mock_number):
            with patch('pyvider.cty.convert.primitive.Value') as mock_value_class:
                # Call string_to_number
                string_to_number(self.mock_value)
                
                # Assertions
                _, kwargs = mock_value_class.call_args
                self.assertEqual(kwargs["marks"], frozenset(["sensitive", "encrypted"]))
    
    def test_register_conversion_call(self):
        """Test that register_conversion is called for string_to_number."""
        with patch('pyvider.cty.convert.primitive.register_conversion') as mock_register:
            # Import the module again to trigger the registration
            from importlib import reload
            from pyvider.cty.convert import primitive
            reload(primitive)
            
            # Assertions - check that register_conversion was called
            mock_register.assert_called()
            
            # Find the call for string_to_number
            string_to_number_call = None
            for call in mock_register.call_args_list:
                args, kwargs = call
                if args[2] == string_to_number:
                    string_to_number_call = call
                    break
            
            # Assertions
            self.assertIsNotNone(string_to_number_call)
            
            # Check that it's registered as unsafe
            args, kwargs = string_to_number_call
            self.assertFalse(kwargs.get("is_safe", False))
