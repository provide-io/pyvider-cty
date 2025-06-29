import pytest
from pyvider.cty.context.validation_context import get_validation_depth, deeper_validation, MAX_VALIDATION_DEPTH

def test_initial_validation_depth():
    """Ensures the initial validation depth is zero."""
    assert get_validation_depth() == 0

def test_deeper_validation_context_manager():
    """Tests that the context manager correctly increments and decrements depth."""
    assert get_validation_depth() == 0
    with deeper_validation():
        assert get_validation_depth() == 1
        with deeper_validation():
            assert get_validation_depth() == 2
    assert get_validation_depth() == 0

def test_deeper_validation_restores_on_exception():
    """Ensures validation depth is restored even if an exception occurs."""
    assert get_validation_depth() == 0
    with pytest.raises(ValueError, match="Test exception"):
        with deeper_validation():
            assert get_validation_depth() == 1
            raise ValueError("Test exception")
    assert get_validation_depth() == 0

def test_max_validation_depth_constant():
    """Checks that the MAX_VALIDATION_DEPTH constant is accessible and an integer."""
    assert isinstance(MAX_VALIDATION_DEPTH, int)
    assert MAX_VALIDATION_DEPTH > 0
