import pytest
from unittest.mock import MagicMock

from pyvider.cty.type import DynamicPseudoType
from pyvider.cty.types.base import CtyType


class TestDynamicPseudoType():
    """Test the DynamicPseudoType class."""
    
    def setUp(self):
        """Set up objects for testing."""
        self.dynamic_type = DynamicPseudoType()
        
        # Create a mock for another CtyType to test compatibility
        self.other_type = MagicMock(spec=CtyType)
    
    def test_dynamic_type_init(self):
        """Test DynamicPseudoType initialization."""
        # Create a dynamic type
        dynamic = DynamicPseudoType()
        
        # Assertions
        self.assertEqual(dynamic.metadata, ())
        self.assertEqual(dynamic.validators, ())
    
    def test_dynamic_type_init_with_metadata(self):
        """Test DynamicPseudoType initialization with metadata."""
        # Create a dynamic type with metadata
        metadata = ("description", "purpose")
        dynamic = DynamicPseudoType(metadata=metadata)
        
        # Assertions
        self.assertEqual(dynamic.metadata, metadata)
        self.assertEqual(dynamic.validators, ())
    
    def test_dynamic_type_init_with_validators(self):
        """Test DynamicPseudoType initialization with validators."""
        # Create mock validators
        validator1 = MagicMock()
        validator2 = MagicMock()
        validators = (validator1, validator2)
        
        # Create a dynamic type with validators
        dynamic = DynamicPseudoType(validators=validators)
        
        # Assertions
        self.assertEqual(dynamic.validators, validators)
        self.assertEqual(dynamic.metadata, ())
    
    def test_dynamic_type_validate(self):
        """Test DynamicPseudoType.validate method."""
        # Test with various value types
        values = [
            "string",
            123,
            True,
            {"key": "value"},
            [1, 2, 3],
            None
        ]
        
        for value in values:
            # Dynamic type should accept any value
            result = self.dynamic_type.validate(value)
            
            # Assertions - value should be returned as is
            self.assertEqual(result, value)
    
    def test_dynamic_type_validate_with_validators(self):
        """Test DynamicPseudoType.validate with validators."""
        # Create a dynamic type with a validator
        validator = MagicMock()
        dynamic = DynamicPseudoType(validators=(validator,))
        
        # Patch the _run_validators method
        dynamic._run_validators = MagicMock()
        
        # Call validate
        result = dynamic.validate("test")
        
        # Assertions
        dynamic._run_validators.assert_called_once_with("test")
        self.assertEqual(result, "test")
    
    def test_dynamic_type_equal(self):
        """Test DynamicPseudoType.equal method."""
        # Create another dynamic type
        another_dynamic = DynamicPseudoType()
        
        # Assertions - dynamic types should be equal to each other
        self.assertTrue(self.dynamic_type.equal(another_dynamic))
        self.assertFalse(self.dynamic_type.equal(self.other_type))
    
    def test_dynamic_type_usable_as(self):
        """Test DynamicPseudoType.usable_as method."""
        # Dynamic type should be usable as any other type
        self.assertTrue(self.dynamic_type.usable_as(self.other_type))
        
        # And also usable as another dynamic type
        another_dynamic = DynamicPseudoType()
        self.assertTrue(self.dynamic_type.usable_as(another_dynamic))
    
    def test_dynamic_type_string_representation(self):
        """Test string representation of DynamicPseudoType."""
        # Assertions
        self.assertEqual(str(self.dynamic_type), "DynamicPseudoType")
        self.assertEqual(repr(self.dynamic_type), "DynamicPseudoType()")
