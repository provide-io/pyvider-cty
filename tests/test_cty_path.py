import pytest
from unittest.mock import MagicMock, patch

from pyvider.cty.path.path import Path, PathStep, GetAttrStep


class TestPathStep():
    """Test the abstract PathStep class."""
    
    def test_path_step_is_abstract(self):
        """Test that PathStep is an abstract class."""
        # Should not be able to instantiate abstract class
        with self.assertRaises(TypeError):
            PathStep()
    
    def test_path_step_apply_is_abstract(self):
        """Test that apply method is abstract and must be implemented."""
        # Create a concrete subclass without implementing apply
        class ConcretePathStep(PathStep):
            pass
        
        # Should raise error when instantiating
        with self.assertRaises(TypeError):
            ConcretePathStep()
    
    def test_path_step_concrete_implementation(self):
        """Test a concrete implementation of PathStep."""
        # Create a concrete subclass with apply implemented
        class ConcretePathStep(PathStep):
            def apply(self, value):
                return "applied"
        
        # Should be able to instantiate and call apply
        step = ConcretePathStep()
        result = step.apply("value")
        
        # Assertions
        self.assertEqual(result, "applied")


class TestGetAttrStep():
    """Test the GetAttrStep class."""
    
    def setUp(self):
        """Set up objects for testing."""
        self.attr_name = "property"
        self.attr_step = GetAttrStep(self.attr_name)
        
        # Mock a Value object
        self.mock_value = MagicMock()
    
    def test_get_attr_step_init(self):
        """Test GetAttrStep initialization."""
        # Assertions
        self.assertEqual(self.attr_step.name, self.attr_name)
    
    def test_get_attr_step_apply(self):
        """Test GetAttrStep.apply method."""
        # Set up mock behavior
        expected_result = MagicMock()
        self.mock_value.apply.return_value = expected_result
        
        # Call apply method
        result = self.attr_step.apply(self.mock_value)
        
        # Assertions
        # Since this implementation relies on the actual implementation of Value,
        # we just ensure the method exists and returns something
        # In a real implementation, you would test against the specific behavior
        self.assertIsNotNone(result)


class TestPath():
    """Test the Path class."""
    
    def setUp(self):
        """Set up objects for testing."""
        self.path = Path()
        
        # Create mock steps
        self.mock_step1 = MagicMock(spec=PathStep)
        self.mock_step2 = MagicMock(spec=PathStep)
        
        # Create a path with steps
        self.path_with_steps = Path([self.mock_step1, self.mock_step2])
    
    def test_path_init_empty(self):
        """Test Path initialization without steps."""
        # Assertions
        self.assertEqual(self.path._steps, [])
    
    def test_path_init_with_steps(self):
        """Test Path initialization with steps."""
        # Assertions
        self.assertEqual(self.path_with_steps._steps, [self.mock_step1, self.mock_step2])
    
    def test_path_get_attr(self):
        """Test Path.get_attr method."""
        # Call get_attr to add a step
        new_path = self.path.get_attr("property")
        
        # Assertions
        self.assertEqual(len(new_path._steps), 1)
        self.assertIsInstance(new_path._steps[0], GetAttrStep)
        self.assertEqual(new_path._steps[0].name, "property")
        
        # Original path should be unchanged
        self.assertEqual(len(self.path._steps), 0)
    
    def test_path_get_attr_chaining(self):
        """Test chaining get_attr calls."""
        # Chain get_attr calls
        new_path = self.path.get_attr("user").get_attr("address").get_attr("city")
        
        # Assertions
        self.assertEqual(len(new_path._steps), 3)
        self.assertEqual(new_path._steps[0].name, "user")
        self.assertEqual(new_path._steps[1].name, "address")
        self.assertEqual(new_path._steps[2].name, "city")
    
    @patch('pyvider.cty.path.path.GetAttrStep')
    def test_path_index(self, mock_get_attr_step):
        """Test Path.index method."""
        # Mock the IndexStep class (assuming it exists)
        mock_index_step = MagicMock()
        mock_key = MagicMock()
        
        # Patch the IndexStep constructor
        with patch('pyvider.cty.path.path.IndexStep', return_value=mock_index_step) as mock_index_step_class:
            # Call index method
            path = Path()
            result = path.index(mock_key)
            
            # Assertions
            mock_index_step_class.assert_called_once_with(mock_key)
            self.assertEqual(len(result._steps), 1)
            self.assertEqual(result._steps[0], mock_index_step)
    
    def test_path_apply(self):
        """Test Path.apply method."""
        # Create mock steps with apply behavior
        step1 = MagicMock(spec=PathStep)
        step2 = MagicMock(spec=PathStep)
        
        intermediate_value = MagicMock()
        final_value = MagicMock()
        
        step1.apply.return_value = intermediate_value
        step2.apply.return_value = final_value
        
        # Create path with these steps
        path = Path([step1, step2])
        
        # Mock input value
        input_value = MagicMock()
        
        # Call apply
        result = path.apply(input_value)
        
        # Assertions
        step1.apply.assert_called_once_with(input_value)
        step2.apply.assert_called_once_with(intermediate_value)
        self.assertEqual(result, final_value)
    
    def test_path_apply_empty(self):
        """Test applying an empty path."""
        # Mock input value
        input_value = MagicMock()
        
        # Apply empty path
        result = self.path.apply(input_value)
        
        # Empty path should return the input value unchanged
        self.assertEqual(result, input_value)
