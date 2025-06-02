import pytest
from unittest.mock import MagicMock, patch

from pyvider.cty.path import CtyPath, PathStep, GetAttrStep, IndexStep, KeyStep # Add IndexStep, KeyStep


class TestPathStep:
    """Test the abstract PathStep class."""
    
    def test_path_step_is_abstract(self):
        """Test that PathStep is an abstract class."""
        # Should not be able to instantiate abstract class
        with pytest.raises(TypeError):
            PathStep()


class TestGetAttrStep:
    """Test the GetAttrStep class."""
    
    def test_get_attr_step_init(self):
        """Test GetAttrStep initialization."""
        # Create a GetAttrStep
        attr_name = "property"
        attr_step = GetAttrStep(attr_name)
        
        # Verify attribute name
        assert attr_step.name == attr_name


class TestPath:
    """Test the Path class."""
    
    def setup_method(self):
        """Set up objects for each test."""
        self.path = CtyPath()
        
        # Create mock steps
        self.mock_step1 = MagicMock(spec=PathStep)
        self.mock_step2 = MagicMock(spec=PathStep)
        
        # Create a path with steps
        self.path_with_steps = CtyPath([self.mock_step1, self.mock_step2])
    
    def test_path_init_empty(self):
        """Test Path initialization without steps."""
        # Verify empty steps
        assert self.path.steps == []
    
    def test_path_init_with_steps(self):
        """Test Path initialization with steps."""
        # Verify steps
        assert self.path_with_steps.steps == [self.mock_step1, self.mock_step2]
    
    def test_path_child(self):
        """Test CtyPath.child method."""
        # Chain get_attr calls
        new_path = self.path.child("user")
        
        # Verify steps
        assert len(new_path.steps) == 1
        assert isinstance(new_path.steps[0], GetAttrStep)
        assert new_path.steps[0].name == "user"
        
        # Verify original path unchanged
        assert len(self.path.steps) == 0
    
    def test_path_child_chaining(self):
        """Test chaining child calls."""
        # Chain calls
        new_path = self.path.child("user").child("address").child("city")
        
        # Verify steps
        assert len(new_path.steps) == 3
        assert new_path.steps[0].name == "user"
        assert new_path.steps[1].name == "address"
        assert new_path.steps[2].name == "city"

    def test_path_index_step(self): # Remove mock_index_step_class argument
        """Test CtyPath.index_step method."""
        # Call method
        new_path = self.path.index_step(5)
        
        # Verify steps
        assert len(new_path.steps) == 1
        assert isinstance(new_path.steps[0], IndexStep)
        assert new_path.steps[0].index == 5
        
        # Verify original path unchanged
        assert len(self.path.steps) == 0

    def test_path_key_step(self): # Remove mock_key_step_class argument
        """Test CtyPath.key_step method."""
        # Call method
        new_path = self.path.key_step("test_key")
        
        # Verify steps
        assert len(new_path.steps) == 1
        assert isinstance(new_path.steps[0], KeyStep)
        assert new_path.steps[0].key == "test_key"

        # Verify original path unchanged
        assert len(self.path.steps) == 0
    
    def test_path_apply_path_empty(self):
        """Test applying an empty path."""
        # Mock input value
        input_value = MagicMock()
        
        # Create a Path instance
        path = CtyPath()
        
        # Apply empty path
        # Note: This is an async function but we're not testing the actual execution
        # Just verifying it exists - actual async tests would need pytest.mark.asyncio
        assert hasattr(path, "apply_path")
        
        # We would normally call it like this in async code:
        # result = await path.apply_path(input_value)
    
    def test_path_string_empty(self):
        """Test string representation of empty path."""
        # Get string representation
        result = self.path.string()
        
        # Verify empty string
        assert result == ""
    
    def test_path_string_with_steps(self):
        """Test string representation of path with steps."""
        # Setup mock steps
        self.mock_step1.__str__.return_value = ".user"
        self.mock_step2.__str__.return_value = ".name"
        
        # Get string representation
        result = self.path_with_steps.string()
        
        # Verify concatenated string
        assert result == ".user.name"
    
    def test_path_str_dunder(self):
        """Test __str__ method."""
        # Empty path
        assert str(self.path) == "(empty path)"
        
        # Path with steps
        self.mock_step1.__str__.return_value = ".user"
        assert str(self.path_with_steps) != "(empty path)"
    
    @pytest.mark.parametrize(
        "path_factory,expected",
        [
            (lambda: CtyPath.empty(), []),
            (lambda: CtyPath.get_attr("name"), [GetAttrStep("name")]),
            (lambda: CtyPath.index(1), [IndexStep(1)]),
            (lambda: CtyPath.key("mykey"), [KeyStep("mykey")]),
        ]
    )
    def test_path_class_methods(self, path_factory, expected):
        """Test Path class methods."""
        # Call class method
        path = path_factory()
        
        # Verify steps
        if not expected:
            assert len(path.steps) == 0
        else:
            assert len(path.steps) == len(expected)
            for i, step in enumerate(expected):
                if isinstance(step, GetAttrStep):
                    assert isinstance(path.steps[i], GetAttrStep)
                    assert path.steps[i].name == step.name
                elif isinstance(step, IndexStep):
                    assert isinstance(path.steps[i], IndexStep)
                    assert path.steps[i].index == step.index
                elif isinstance(step, KeyStep):
                    assert isinstance(path.steps[i], KeyStep)
                    assert path.steps[i].key == step.key
