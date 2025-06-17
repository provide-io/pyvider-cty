
from typing import Never

import pytest

from pyvider.cty.context.operation_context import (
    OperationContext,
    _current_operation_context,  # For direct inspection/reset if necessary in tests
    get_current_operation,
    operation_context,
)


def test_initial_operation_context() -> None:
    """Test that the initial operation context is DEFAULT."""
    assert get_current_operation() == OperationContext.DEFAULT

def test_operation_context_manager_sets_and_restores_context() -> None:
    """Test that the OperationContextManager correctly sets and restores context."""
    initial_context = get_current_operation()
    assert initial_context == OperationContext.DEFAULT

    with operation_context(OperationContext.CONFIG):
        assert get_current_operation() == OperationContext.CONFIG

        with operation_context(OperationContext.STATE):
            assert get_current_operation() == OperationContext.STATE

        # Exiting STATE context
        assert get_current_operation() == OperationContext.CONFIG


    # Exiting CONFIG context
    assert get_current_operation() == initial_context # Should be DEFAULT


def test_operation_context_restores_on_exception() -> Never:
    """Test that context is restored even if an exception occurs within the context."""
    initial_context = get_current_operation()
    assert initial_context == OperationContext.DEFAULT

    with pytest.raises(ValueError, match="Test exception"):
        with operation_context(OperationContext.PLAN):
            assert get_current_operation() == OperationContext.PLAN
            raise ValueError("Test exception")

    assert get_current_operation() == initial_context # Should be restored to DEFAULT


def test_get_current_operation_default() -> None:
    """Test get_current_operation returns the default if no context is set explicitly."""
    # This implicitly tests the ContextVar default
    # To be absolutely sure, we could try to reset to a known state if tests could interfere,
    # but pytest usually isolates test function calls.
    # For safety, explicitly reset (if possible without direct _current_operation_context.reset which is not public)
    # This test is somewhat redundant with test_initial_operation_context but confirms default access.
    token = _current_operation_context.set(OperationContext.DEFAULT) # Set to known default
    try:
        assert get_current_operation() == OperationContext.DEFAULT
    finally:
        _current_operation_context.reset(token)


def test_enum_values_auto_generated() -> None:
    """Check that enum values are auto-generated and distinct."""
    values = [item.value for item in OperationContext]
    assert len(values) == len(set(values)), "Enum values should be unique"
    for item in OperationContext:
        assert isinstance(item.value, int), "Enum values should be integers from auto()"

# Clean up context var after tests if necessary, though pytest should handle test isolation.
# If tests were to run in a way that context could leak (e.g. within the same async task without proper reset),
# a fixture could be used to ensure cleanup. For now, assuming pytest's default isolation.
