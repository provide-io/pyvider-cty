import pytest

from pyvider.cty.exceptions import ValidationError
from pyvider.cty.ctypes.structural.dynamic import CtyDynamic


class TestCtyDynamic():
    """Test the CtyDynamic type."""
    
    def setUp(self):
        """Set up objects for testing."""
        self.dynamic_type = CtyDynamic()
    
    def test_dynamic_init(self):
        """Test CtyDynamic initialization."""
        # Assertions
        self.assertIsInstance(self.dynamic_type, CtyDynamic)
    
    def test_validate_dict(self):
        """Test validating a dictionary."""
        value = {"name": "John", "age": 30}
        self.dynamic_type.validate(value)  # Should not raise an exception
    
    def test_validate_list(self):
        """Test validating a list."""
        value = [1, 2, 3, "mixed", True]
        self.dynamic_type.validate(value)  # Should not raise an exception
    
    def test_validate_primitives(self):
        """Test validating primitive values."""
        # Test various primitive types
        self.dynamic_type.validate(123)  # int
        self.dynamic_type.validate(45.67)  # float
        self.dynamic_type.validate("string")  # str
        self.dynamic_type.validate(True)  # bool
        self.dynamic_type.validate(None)  # None
    
    def test_validate_nested_structures(self):
        """Test validating nested data structures."""
        value = {
            "user": {
                "name": "John",
                "addresses": [
                    {"city": "New York", "zip": "10001"},
                    {"city": "Boston", "zip": "02108"}
                ],
                "active": True
            },
            "permissions": ["read", "write"],
            "metadata": None
        }
        self.dynamic_type.validate(value)  # Should not raise an exception
    
    def test_validate_unsupported_type(self):
        """Test validating an unsupported type."""
        # Create a custom class
        class CustomClass:
            pass
        
        # Try to validate an instance of the custom class
        custom_obj = CustomClass()
        with self.assertRaises(ValidationError):
            self.dynamic_type.validate(custom_obj)
    
    def test_equal_same_type(self):
        """Test equality with another CtyDynamic instance."""
        other_dynamic = CtyDynamic()
        self.assertTrue(self.dynamic_type.equal(other_dynamic))
    
    def test_equal_different_type(self):
        """Test equality with a different type."""
        from pyvider.cty.ctypes.primitives.string import CtyString
        string_type = CtyString()
        self.assertFalse(self.dynamic_type.equal(string_type))
    
    def test_usable_as_same_type(self):
        """Test usability with another CtyDynamic instance."""
        other_dynamic = CtyDynamic()
        self.assertTrue(self.dynamic_type.usable_as(other_dynamic))
    
    def test_usable_as_different_type(self):
        """Test usability with a different type."""
        from pyvider.cty.ctypes.primitives.number import CtyNumber
        number_type = CtyNumber()
        self.assertFalse(self.dynamic_type.usable_as(number_type))
    
    def test_string_representation(self):
        """Test string representation."""
        self.assertEqual(str(self.dynamic_type), "CtyDynamic")
        self.assertEqual(repr(self.dynamic_type), "CtyDynamic()")


class TestDynamicFactoryFunction():
    """Test the tfdynamic factory function."""
    
    def test_tfdynamic_factory(self):
        """Test the tfdynamic factory function."""
        from pyvider.cty.ctypes.structural.dynamic import tfdynamic
        from pyvider.schema.attributes import AttributeValue, AttributeMetadata
        
        # Call the factory function
        result = tfdynamic(description="A dynamic field")
        
        # Assertions
        self.assertIsInstance(result, AttributeValue)
        self.assertIsInstance(result.ctype, CtyDynamic)
        self.assertIsInstance(result.metadata, AttributeMetadata)
        self.assertEqual(result.metadata.description, "A dynamic field")
    
    def test_tfdynamic_with_multiple_kwargs(self):
        """Test tfdynamic factory with multiple keyword arguments."""
        from pyvider.cty.ctypes.structural.dynamic import tfdynamic
        
        # Call with multiple kwargs
        result = tfdynamic(
            description="A dynamic field",
            required=True,
            computed=False,
            sensitive=True
        )
        
        # Assertions
        self.assertEqual(result.metadata.description, "A dynamic field")
        self.assertTrue(result.metadata.required)
        self.assertFalse(result.metadata.computed)
        self.assertTrue(result.metadata.sensitive)
