from unittest.mock import MagicMock

from pyvider.cty.convert.base import (
    Conversion, 
    register_conversion, 
    get_conversion,
    get_conversion_unsafe, 
    convert, 
    convert_unsafe
)


class TestConversion():
    """Test the Conversion class."""
    
    def setUp(self):
        """Set up objects for testing."""
        # Mock source and target types
        self.mock_source_type = MagicMock()
        self.mock_target_type = MagicMock()
        
        # Mock converter function
        self.mock_converter = MagicMock()
        self.mock_converter.return_value = "converted_value"
        
        # Create a conversion
        self.conversion = Conversion(
            source_type=self.mock_source_type,
            target_type=self.mock_target_type,
            converter=self.mock_converter,
            is_safe=True
        )
        
        # Mock value
        self.mock_value = MagicMock()
    
    def test_conversion_init(self):
        """Test Conversion initialization."""
        # Assertions
        self.assertEqual(self.conversion.source_type, self.mock_source_type)
        self.assertEqual(self.conversion.target_type, self.mock_target_type)
        self.assertEqual(self.conversion.converter, self.mock_converter)
        self.assertTrue(self.conversion.is_safe)
    
    def test_conversion_convert(self):
        """Test Conversion.convert method."""
        # Call convert
        result = self.conversion.convert(self.mock_value)
        
        # Assertions
        self.mock_converter.assert_called_once_with(self.mock_value)
        self.assertEqual(result, "converted_value")


class TestConversionRegistry():
    """Test the conversion registry functions."""
    
    def setUp(self):
        """Set up objects for testing."""
        # Mock source and target types
        self.mock_source_type = MagicMock()
        self.mock_source_type.__class__ = type('MockSourceType', (), {})
        
        self.mock_target_type = MagicMock()
        self.mock_target_type.__class__ = type('MockTargetType', (), {})
        
        # Mock converter function
        self.mock_converter = MagicMock()
        
        # Clear registries before each test
        from pyvider.cty.convert import base
        base._SAFE_CONVERSIONS = {}
        base._UNSAFE_CONVERSIONS = {}
    
    def test_register_safe_conversion(self):
        """Test registering a safe conversion."""
        # Register a safe conversion
        register_conversion(
            source_type=self.mock_source_type,
            target_type=self.mock_target_type,
            converter=self.mock_converter,
            is_safe=True
        )
        
        # Get the conversion
        conversion = get_conversion(self.mock_source_type, self.mock_target_type)
        
        # Assertions
        self.assertIsNotNone(conversion)
        self.assertEqual(conversion.source_type, self.mock_source_type)
        self.assertEqual(conversion.target_type, self.mock_target_type)
        self.assertEqual(conversion.converter, self.mock_converter)
        self.assertTrue(conversion.is_safe)
        
        # Also check it's in the unsafe registry
        unsafe_conversion = get_conversion_unsafe(self.mock_source_type, self.mock_target_type)
        self.assertIsNotNone(unsafe_conversion)
    
    def test_register_unsafe_conversion(self):
        """Test registering an unsafe conversion."""
        # Register an unsafe conversion
        register_conversion(
            source_type=self.mock_source_type,
            target_type=self.mock_target_type,
            converter=self.mock_converter,
            is_safe=False
        )
        
        # Get the conversion (should not be in safe registry)
        safe_conversion = get_conversion(self.mock_source_type, self.mock_target_type)
        
        # Assertions
        self.assertIsNone(safe_conversion)
        
        # Check it's in the unsafe registry
        unsafe_conversion = get_conversion_unsafe(self.mock_source_type, self.mock_target_type)
        self.assertIsNotNone(unsafe_conversion)
    
    def test_get_nonexistent_conversion(self):
        """Test getting a conversion that doesn't exist."""
        # Get a nonexistent conversion
        conversion = get_conversion(self.mock_source_type, self.mock_target_type)
        
        # Assertions
        self.assertIsNone(conversion)
    
    def test_convert_same_type(self):
        """Test converting a value to the same type."""
        # Mock value with type
        mock_value = MagicMock()
        mock_value.type = self.mock_source_type
        
        # Make types equal
        mock_value.type.equals.return_value = True
        
        # Call convert
        result = convert(mock_value, self.mock_source_type)
        
        # Assertions
        self.assertEqual(result, mock_value)
    
    def test_convert_with_conversion(self):
        """Test converting a value using a registered conversion."""
        # Mock value with type
        mock_value = MagicMock()
        mock_value.type = self.mock_source_type
        
        # Make types different
        mock_value.type.equals.return_value = False
        
        # Register a conversion
        register_conversion(
            source_type=self.mock_source_type,
            target_type=self.mock_target_type,
            converter=self.mock_converter,
            is_safe=True
        )
        
        # Call convert
        result = convert(mock_value, self.mock_target_type)
        
        # Assertions
        self.mock_converter.assert_called_once_with(mock_value)
        self.assertEqual(result, "converted_value")
    
    def test_convert_no_conversion(self):
        """Test converting a value with no available conversion."""
        # Mock value with type
        mock_value = MagicMock()
        mock_value.type = self.mock_source_type
        
        # Make types different
        mock_value.type.equals.return_value = False
        
        # Call convert (no conversion registered)
        with self.assertRaises(TypeError):
            convert(mock_value, self.mock_target_type)
    
    def test_convert_unsafe_with_unsafe_conversion(self):
        """Test unsafe conversion with an unsafe conversion."""
        # Mock value with type
        mock_value = MagicMock()
        mock_value.type = self.mock_source_type
        
        # Make types different
        mock_value.type.equals.return_value = False
        
        # Register an unsafe conversion
        register_conversion(
            source_type=self.mock_source_type,
            target_type=self.mock_target_type,
            converter=self.mock_converter,
            is_safe=False
        )
        
        # Call convert_unsafe
        result = convert_unsafe(mock_value, self.mock_target_type)
        
        # Assertions
        self.mock_converter.assert_called_once_with(mock_value)
        self.assertEqual(result, "converted_value")
    
    def test_convert_unsafe_no_conversion(self):
        """Test unsafe conversion with no available conversion."""
        # Mock value with type
        mock_value = MagicMock()
        mock_value.type = self.mock_source_type
        
        # Make types different
        mock_value.type.equals.return_value = False
        
        # Call convert_unsafe (no conversion registered)
        with self.assertRaises(TypeError):
            convert_unsafe(mock_value, self.mock_target_type)
    
    def test_multiple_conversions(self):
        """Test registering multiple conversions."""
        # Create additional types
        mock_type2 = MagicMock()
        mock_type2.__class__ = type('MockType2', (), {})
        
        mock_type3 = MagicMock()
        mock_type3.__class__ = type('MockType3', (), {})
        
        # Register multiple conversions
        register_conversion(
            source_type=self.mock_source_type,
            target_type=self.mock_target_type,
            converter=self.mock_converter,
            is_safe=True
        )
        
        register_conversion(
            source_type=self.mock_source_type,
            target_type=mock_type2,
            converter=self.mock_converter,
            is_safe=True
        )
        
        register_conversion(
            source_type=mock_type2,
            target_type=mock_type3,
            converter=self.mock_converter,
            is_safe=False
        )
        
        # Get conversions
        conv1 = get_conversion(self.mock_source_type, self.mock_target_type)
        conv2 = get_conversion(self.mock_source_type, mock_type2)
        conv3 = get_conversion(mock_type2, mock_type3)
        
        # Assertions
        self.assertIsNotNone(conv1)
        self.assertIsNotNone(conv2)
        self.assertIsNone(conv3)  # Not a safe conversion
        
        # Get unsafe conversions
        unsafe_conv3 = get_conversion_unsafe(mock_type2, mock_type3)
        self.assertIsNotNone(unsafe_conv3)
