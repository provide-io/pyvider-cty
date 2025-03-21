
import unittest

from unittest.mock import MagicMock, patch

from pyvider.cty import CtyValue


class TestValue(unittest.TestCase):
    """Test the Value class."""
    
    def setUp(self):
        """Set up mocks for testing."""
        self.mock_type = MagicMock()
        self.mock_mark = "sensitive"
    
    def test_value_initialization(self):
        """Test basic Value initialization."""
        # Create a regular value
        val = CtyValue(type_=self.mock_type, value="test")
        
        # Assertions
        self.assertEqual(val._type, self.mock_type)
        self.assertEqual(val._value, "test")
        self.assertFalse(val._is_unknown)
        self.assertFalse(val._is_null)
        self.assertEqual(val._marks, frozenset())
    
    def test_value_unknown(self):
        """Test unknown Value initialization."""
        # Create an unknown value
        val = CtyValue(type_=self.mock_type, is_unknown=True)
        
        # Assertions
        self.assertEqual(val._type, self.mock_type)
        self.assertIsNone(val._value)
        self.assertTrue(val._is_unknown)
        self.assertFalse(val._is_null)
        self.assertEqual(val._marks, frozenset())
        self.assertFalse(val.is_known)
    
    def test_value_null(self):
        """Test null Value initialization."""
        # Create a null value
        val = CtyValue(type_=self.mock_type, is_null=True)
        
        # Assertions
        self.assertEqual(val._type, self.mock_type)
        self.assertIsNone(val._value)
        self.assertFalse(val._is_unknown)
        self.assertTrue(val._is_null)
        self.assertEqual(val._marks, frozenset())
        self.assertTrue(val.is_known)
        self.assertTrue(val.is_null)
    
    def test_value_with_marks(self):
        """Test Value with marks."""
        # Create a value with marks
        marks = frozenset(["sensitive", "encrypted"])
        val = CtyValue(type_=self.mock_type, value="password", marks=marks)
        
        # Assertions
        self.assertEqual(val._type, self.mock_type)
        self.assertEqual(val._value, "password")
        self.assertEqual(val._marks, marks)
        self.assertTrue(val.has_mark("sensitive"))
        self.assertTrue(val.has_mark("encrypted"))
        self.assertFalse(val.has_mark("public"))
    
    def test_value_has_mark(self):
        """Test has_mark method."""
        # Create a value with a mark
        val = CtyValue(type_=self.mock_type, value="test", marks=frozenset([self.mock_mark]))
        
        # Assertions
        self.assertTrue(val.has_mark(self.mock_mark))
        self.assertFalse(val.has_mark("other_mark"))
    
    def test_value_add_mark(self):
        """Test mark method to add a mark."""
        # Create a value without marks
        val = CtyValue(type_=self.mock_type, value="test")
        
        # Add a mark
        marked_val = val.mark(self.mock_mark)
        
        # Assertions
        self.assertFalse(val.has_mark(self.mock_mark))  # Original value unchanged
        self.assertTrue(marked_val.has_mark(self.mock_mark))  # New value has mark
        self.assertEqual(marked_val._value, "test")  # Other properties preserved
        self.assertEqual(marked_val._type, self.mock_type)
    
    def test_value_add_multiple_marks(self):
        """Test adding multiple marks to a value."""
        # Create a value with one mark
        val = CtyValue(type_=self.mock_type, value="test", marks=frozenset(["mark1"]))
        
        # Add another mark
        marked_val = val.mark("mark2")
        
        # Assertions
        self.assertTrue(marked_val.has_mark("mark1"))
        self.assertTrue(marked_val.has_mark("mark2"))
        self.assertEqual(len(marked_val._marks), 2)
    
    def test_value_unmark(self):
        """Test unmark method to remove all marks."""
        # Create a value with marks
        val = CtyValue(
            type_=self.mock_type, 
            value="test", 
            marks=frozenset(["mark1", "mark2"])
        )
        
        # Remove all marks
        unmarked_val, removed_marks = val.unmark()
        
        # Assertions
        self.assertEqual(len(unmarked_val._marks), 0)  # No marks left
        self.assertEqual(removed_marks, frozenset(["mark1", "mark2"]))  # Removed marks returned
        self.assertEqual(unmarked_val._value, "test")  # Other properties preserved
        self.assertEqual(unmarked_val._type, self.mock_type)
    
    def test_value_type_property(self):
        """Test type property."""
        # Create a value
        val = CtyValue(type_=self.mock_type, value="test")
        
        # Assertions
        self.assertEqual(val.type, self.mock_type)
    
    def test_value_is_known_property(self):
        """Test is_known property."""
        # Create a known value
        known_val = CtyValue(type_=self.mock_type, value="test")
        
        # Create an unknown value
        unknown_val = CtyValue(type_=self.mock_type, is_unknown=True)
        
        # Assertions
        self.assertTrue(known_val.is_known)
        self.assertFalse(unknown_val.is_known)
    
    def test_value_is_null_property(self):
        """Test is_null property."""
        # Create a null value
        null_val = CtyValue(type_=self.mock_type, is_null=True)
        
        # Create a non-null value
        non_null_val = CtyValue(type_=self.mock_type, value="test")
        
        # Assertions
        self.assertTrue(null_val.is_null)
        self.assertFalse(non_null_val.is_null)
    
    def test_value_refine(self):
        """Test refine method."""
        # Create a value
        val = CtyValue(type_=self.mock_type, value="test")
        
        # Mock the ValueRefinementBuilder class
        with patch('pyvider.cty.values.refinement.ValueRefinementBuilder') as mock_builder:
            # Set up the mock
            mock_builder_instance = MagicMock()
            mock_builder.return_value = mock_builder_instance
            
            # Call refine method
            builder = val.refine()
            
            # Assertions
            mock_builder.assert_called_once_with(val)
            self.assertEqual(builder, mock_builder_instance)
