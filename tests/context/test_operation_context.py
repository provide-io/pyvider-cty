import pytest
from pyvider.cty.context.operation_context import (
    OperationContext,
    get_current_operation,
    operation_context
)

def test_default_operation_context():
    """Test that the default operation context is DEFAULT."""
    assert get_current_operation() == OperationContext.DEFAULT

def test_operation_context_switching_all_members():
    """Test setting and getting operation contexts for all enum members."""
    initial_context = get_current_operation()

    for context_member in OperationContext:
        with operation_context(context_member):
            assert get_current_operation() == context_member
        # Check if context is restored after exiting the 'with' block
        assert get_current_operation() == initial_context

    # Final check to ensure it's back to the initial state (usually DEFAULT if run standalone)
    assert get_current_operation() == initial_context

def test_operation_context_nesting():
    """Test nested operation contexts."""
    assert get_current_operation() == OperationContext.DEFAULT

    with operation_context(OperationContext.CONFIG):
        assert get_current_operation() == OperationContext.CONFIG
        with operation_context(OperationContext.PLAN):
            assert get_current_operation() == OperationContext.PLAN
        assert get_current_operation() == OperationContext.CONFIG

    assert get_current_operation() == OperationContext.DEFAULT

def test_operation_context_reset_after_exception():
    """Test that operation context is reset even if an exception occurs."""
    initial_context = get_current_operation()
    assert initial_context == OperationContext.DEFAULT

    custom_context = OperationContext.APPLY

    with pytest.raises(ValueError, match="Test exception"):
        with operation_context(custom_context):
            assert get_current_operation() == custom_context
            raise ValueError("Test exception")

    # Check if context is restored to the state before the 'with' block
    # that set 'custom_context', which is 'initial_context'.
    assert get_current_operation() == initial_context

def test_operation_context_manager_token_handling_on_exception():
    """
    Test specifically that the token is reset in the __exit__ method
    even when an exception occurs. This is mostly for covering the
    `self._token = None` line within the __exit__ if it's not already covered.
    """
    manager = operation_context(OperationContext.SCHEMA) # Get the manager instance

    # Simulate entering the context
    try:
        manager.__enter__()
        assert get_current_operation() == OperationContext.SCHEMA
        # Simulate an exception occurring
        raise RuntimeError("Simulated error")
    except RuntimeError:
        # Simulate Python's context management calling __exit__
        # with exception details
        manager.__exit__(RuntimeError, RuntimeError("Simulated error"), None) # type: ignore

    # Context should be reset to DEFAULT (or whatever it was before this specific manager)
    # Depending on how tests are run, initial might not be DEFAULT if other tests polluted it.
    # For this isolated test part, assuming it should revert what this manager did.
    # If _current_operation_context was DEFAULT before manager.__enter__(), it should be DEFAULT now.
    # This mainly checks that __exit__ was called and reset the token.
    # A more robust check would be to query the internal state of the manager,
    # but that's not possible without changing the class.
    # We rely on get_current_operation() reflecting the reset.
    assert get_current_operation() != OperationContext.SCHEMA
    # It should revert to the state before this specific context manager was entered.
    # If this test runs in isolation and default is DEFAULT, this will hold.
    # If other tests run before, the "previous" context might be something else.
    # The critical part is that it's NOT OperationContext.SCHEMA.

    # To be absolutely sure, let's set a known outer context
    with operation_context(OperationContext.READ):
        assert get_current_operation() == OperationContext.READ
        manager_inner = operation_context(OperationContext.FUNCTION)
        try:
            manager_inner.__enter__()
            assert get_current_operation() == OperationContext.FUNCTION
            raise ValueError("test error")
        except ValueError:
            manager_inner.__exit__(ValueError, ValueError("test error"), None) # type: ignore
        assert get_current_operation() == OperationContext.READ


# Test logging (indirectly, by ensuring code paths with logs are hit)
# The actual log content capture is problematic, so we focus on execution.
def test_logging_paths_in_context_manager(caplog):
    """Ensure __enter__ and __exit__ logging lines are covered."""
    # This test primarily ensures that the logging lines in __enter__ and __exit__
    # are executed. caplog is used to enable log capturing, even if we don't
    # assert specific messages due to capture issues with the telemetry logger.

    with caplog.at_level("DEBUG", logger="pyvider.telemetry"): # Match logger used in module
        initial_ctx = get_current_operation()
        with operation_context(OperationContext.FUNCTION):
            pass # __enter__ and __exit__ logs should be generated

        # Check that context was restored
        assert get_current_operation() == initial_ctx

        # Test with an exception
        with pytest.raises(KeyError):
            with operation_context(OperationContext.SCHEMA):
                raise KeyError("test")
        assert get_current_operation() == initial_ctx

# Ensure all enum values are distinct
def test_enum_values_distinct():
    values = [member.value for member in OperationContext]
    assert len(values) == len(set(values)), "All OperationContext enum values should be distinct"

# Ensure all enum names are present
def test_enum_names_present():
    expected_names = ["DEFAULT", "CONFIG", "STATE", "PLAN", "APPLY", "READ", "FUNCTION", "SCHEMA"]
    member_names = [member.name for member in OperationContext]
    for name in expected_names:
        assert name in member_names
    assert len(member_names) == len(expected_names)
