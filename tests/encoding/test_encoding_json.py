import json
import pytest
from unittest.mock import MagicMock, patch

from pyvider.cty.encoding.json import marshal, unmarshal


class TestJsonEncoding():
    """Test the JSON encoding module."""
    
    def setUp(self):
        """Set up objects for testing."""
        # Mock Type and Value classes
        self.mock_type = MagicMock()
        self.mock_value = MagicMock()
        
        # Configure mock value properties
        self.mock_value.is_known = True
        self.mock_value.is_null = False
        self.mock_value._value = "test_value"
        self.mock_value.type = self.mock_type
    
    def test_marshal_known_value(self):
        """Test marshaling a known value."""
        # Call marshal
        result = marshal(self.mock_value)
        
        # Assertions
        expected = json.dumps("test_value").encode('utf-8')
        self.assertEqual(result, expected)
    
    def test_marshal_with_type(self):
        """Test marshaling with explicit type."""
        # Call marshal with type
        result = marshal(self.mock_value, self.mock_type)
        
        # Assertions
        expected = json.dumps("test_value").encode('utf-8')
        self.assertEqual(result, expected)
    
    def test_marshal_unknown_value(self):
        """Test marshaling an unknown value."""
        # Configure mock to be unknown
        self.mock_value.is_known = False
        
        # Call marshal
        with self.assertRaises(ValueError):
            marshal(self.mock_value)
    
    def test_marshal_null_value(self):
        """Test marshaling a null value."""
        # Configure mock to be null
        self.mock_value.is_null = True
        
        # Call marshal
        result = marshal(self.mock_value)
        
        # Assertions
        self.assertEqual(result, b"null")
    
    def test_unmarshal_string_data(self):
        """Test unmarshaling from string data."""
        # Mock the null_val function
        with patch('pyvider.cty.encoding.json.null_val') as mock_null_val:
            # Set up mock return value
            mock_null_val.return_value = "null_value"
            
            # Call unmarshal with string data
            result = unmarshal('"test_data"', self.mock_type)
            
            # Assertions
            self.mock_type.validate.assert_called_once_with("test_data")
            mock_null_val.assert_not_called()
    
    def test_unmarshal_bytes_data(self):
        """Test unmarshaling from bytes data."""
        # Mock the Value constructor
        with patch('pyvider.cty.encoding.json.CtyValue') as mock_value_class:
            # Set up mock return value
            mock_value_instance = MagicMock()
            mock_value_class.return_value = mock_value_instance
            
            # Set up mock validate
            validated_value = "validated_value"
            self.mock_type.validate.return_value = validated_value
            
            # Call unmarshal with bytes data
            result = unmarshal(b'{"key": "value"}', self.mock_type)
            
            # Assertions
            self.mock_type.validate.assert_called_once_with({"key": "value"})
            mock_value_class.assert_called_once_with(self.mock_type, validated_value)
            self.assertEqual(result, mock_value_instance)
    
    def test_unmarshal_null_data(self):
        """Test unmarshaling null data."""
        # Mock the null_val function
        with patch('pyvider.cty.encoding.json.null_val') as mock_null_val:
            # Set up mock return value
            mock_null_val.return_value = "null_value"
            
            # Call unmarshal with null data
            result = unmarshal(b"null", self.mock_type)
            
            # Assertions
            mock_null_val.assert_called_once_with(self.mock_type)
            self.assertEqual(result, "null_value")
    
    def test_unmarshal_invalid_json(self):
        """Test unmarshaling invalid JSON data."""
        # Call unmarshal with invalid JSON
        with self.assertRaises(ValueError):
            unmarshal(b"{invalid_json", self.mock_type)
    
    def test_marshal_complex_value(self):
        """Test marshaling a complex value."""
        # Configure mock with complex data
        self.mock_value._value = {
            "string": "value",
            "number": 123,
            "boolean": True,
            "list": [1, 2, 3],
            "object": {"nested": "value"}
        }
        
        # Call marshal
        result = marshal(self.mock_value)
        
        # Assertions
        expected = json.dumps(self.mock_value._value).encode('utf-8')
        self.assertEqual(result, expected)
    
    def test_unmarshal_complex_data(self):
        """Test unmarshaling complex data."""
        # Complex JSON data
        complex_data = {
            "string": "value",
            "number": 123,
            "boolean": True,
            "list": [1, 2, 3],
            "object": {"nested": "value"}
        }
        
        # Mock CtyValue constructor and type.validate
        with patch('pyvider.cty.encoding.json.CtyValue') as mock_value_class:
            # Set up mock return value
            mock_value_instance = MagicMock()
            mock_value_class.return_value = mock_value_instance
            
            # Set up mock validate to return the input
            self.mock_type.validate.return_value = complex_data
            
            # Call unmarshal
            result = unmarshal(json.dumps(complex_data).encode('utf-8'), self.mock_type)
            
            # Assertions
            self.mock_type.validate.assert_called_once_with(complex_data)
            mock_value_class.assert_called_once_with(self.mock_type, complex_data)
            self.assertEqual(result, mock_value_instance)
