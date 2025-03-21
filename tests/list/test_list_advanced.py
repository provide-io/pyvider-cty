
import unittest

from pyvider.cty.exceptions import PyviderError, ValidationError
from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString

class TestCtyListAdvanced(unittest.TestCase):
    """Advanced tests for the CtyList type to improve coverage."""
    
    def setUp(self):
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())
    
    def test_post_init_validates_element_type(self):
        """Test that __post_init__ validates element_type is a CtyType."""
        # Try to create a CtyList with an invalid element_type
        with self.assertRaises(PyviderError):
            CtyList(element_type="not_a_cty_type")
    
    def test_validate_tuple_as_list(self):
        """Test that validate accepts tuples and converts them to lists."""
        # Create a tuple of strings
        data = ("apple", "banana", "cherry")
        
        # Validate
        result = self.string_list.validate(data)
        
        # Assertions
        self.assertIsInstance(result, list)
        self.assertEqual(result, ["apple", "banana", "cherry"])
    
    def test_validate_none_becomes_empty_list(self):
        """Test that None is treated as an empty list."""
        # Validate None
        result = self.string_list.validate(None)
        
        # Assertions
        self.assertEqual(result, [])
    
    def test_validate_invalid_container_type(self):
        """Test validation fails for non-list/tuple containers."""
        # Try to validate a dictionary
        with self.assertRaises(PyviderError):
            self.string_list.validate({"a": 1, "b": 2})
        
        # Try to validate a string (iterable but not list/tuple)
        with self.assertRaises(PyviderError):
            self.string_list.validate("not_a_list")
    
    def test_validate_homogeneous_list(self):
        """Test validation of a homogeneous list."""
        # Create a list of numbers
        data = [1, 2, 3, 4, 5]
        
        # Validate
        result = self.number_list.validate(data)
        
        # Assertions
        self.assertEqual(result, [1, 2, 3, 4, 5])
    
    def test_validate_heterogeneous_list_fails(self):
        """Test validation fails for heterogeneous lists."""
        # Create a mixed list
        data = [1, "two", 3, True]
        
        # Validate against number list
        with self.assertRaises(ValidationError):
            self.number_list.validate(data)
    
    def test_validate_nested_lists(self):
        """Test validation of nested lists."""
        # Create a list of lists
        nested_list_type = CtyList(element_type=self.string_list)
        data = [["a", "b"], ["c", "d", "e"]]
        
        # Validate
        result = nested_list_type.validate(data)
        
        # Assertions
        self.assertEqual(result, [["a", "b"], ["c", "d", "e"]])
    
    def test_validate_nested_list_with_errors(self):
        """Test validation of nested lists with errors."""
        # Create a list of lists with an error in the nested list
        nested_list_type = CtyList(element_type=self.number_list)
        data = [[1, 2], [3, "four", 5]]  # "four" is not a number
        
        # Validate
        with self.assertRaises(ValidationError):
            nested_list_type.validate(data)
    
    def test_element_at_valid_index(self):
        """Test retrieving an element at a valid index."""
        # Create and validate a list
        data = ["apple", "banana", "cherry"]
        validated = self.string_list.validate(data)
        
        # Get element at index
        element = self.string_list.element_at(validated, 1)
        
        # Assertions
        self.assertEqual(element, "banana")
    
    def test_element_at_invalid_index(self):
        """Test retrieving an element at an invalid index."""
        # Create and validate a list
        data = ["apple", "banana", "cherry"]
        validated = self.string_list.validate(data)
        
        # Try to get element at invalid index
        with self.assertRaises(IndexError):
            self.string_list.element_at(validated, 5)
    
    def test_element_at_negative_index(self):
        """Test retrieving an element at a negative index."""
        # Create and validate a list
        data = ["apple", "banana", "cherry"]
        validated = self.string_list.validate(data)
        
        # Get element at negative index
        element = self.string_list.element_at(validated, -1)
        
        # Assertions
        self.assertEqual(element, "cherry")
    
    def test_element_at_invalid_container(self):
        """Test element_at with an invalid container."""
        # Try to get element from non-list
        with self.assertRaises(ValidationError):
            self.string_list.element_at("not_a_list", 0)
    
    def test_equal_same_element_type(self):
        """Test equality with same element type."""
        # Create another string list
        other_string_list = CtyList(element_type=CtyString())
        
        # Test equality
        self.assertTrue(self.string_list.equal(other_string_list))
    
    def test_equal_different_element_type(self):
        """Test equality with different element type."""
        # Test inequality
        self.assertFalse(self.string_list.equal(self.number_list))
    
    def test_equal_non_list_type(self):
        """Test equality with non-list type."""
        # Create a CtyString
        string_type = CtyString()
        
        # Test inequality
        self.assertFalse(self.string_list.equal(string_type))
    
    def test_usable_as_same_type(self):
        """Test usable_as with same type."""
        # Create another string list
        other_string_list = CtyList(element_type=CtyString())
        
        # Test usability
        self.assertTrue(self.string_list.usable_as(other_string_list))
    
    def test_usable_as_different_type(self):
        """Test usable_as with different type."""
        # Test non-usability
        self.assertFalse(self.string_list.usable_as(self.number_list))
    
    def test_usable_as_non_list_type(self):
        """Test usable_as with non-list type."""
        # Create a CtyString
        string_type = CtyString()
        
        # Test non-usability
        self.assertFalse(self.string_list.usable_as(string_type))
    
    def test_string_representation(self):
        """Test string representation of CtyList."""
        # Create a list type
        list_type = CtyList(element_type=CtyString())
        
        # Test string representation
        self.assertEqual(str(list_type), "list(CtyString)")
    
    def test_string_representation_complex(self):
        """Test string representation of complex CtyList."""
        # Create a nested list type
        nested_list = CtyList(element_type=CtyList(element_type=CtyNumber()))
        
        # Test string representation
        self.assertEqual(str(nested_list), "list(list(CtyNumber))")
    
    def test_list_equality_operator(self):
        """Test the __eq__ operator."""
        # Create two identical list types
        list1 = CtyList(element_type=CtyString())
        list2 = CtyList(element_type=CtyString())
        
        # Test equality
        self.assertEqual(list1, list2)
    
    def test_list_inequality_operator(self):
        """Test inequality with different element types."""
        # Test inequality
        self.assertNotEqual(self.string_list, self.number_list)
    
    def test_repr_representation(self):
        """Test __repr__ representation."""
        # Test repr
        self.assertEqual(repr(self.string_list), "CtyList()")
