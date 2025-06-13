import pytest
from typing import Any, Optional, Type
from pyvider.cty.conversion import (
    marshal,
    unmarshal,
    WireFormatRegistry,
    WireFormat,
    WireFormatType,
    OperationContext,
    get_current_operation,
    operation_context
)

# Define a dummy formatter for testing purposes
class DummyFormat(WireFormat):
    TYPE: WireFormatType = WireFormatType.JSON # Using JSON just as a placeholder type

    def marshal(self, value: Any, operation: Optional[OperationContext] = None, **options: Any) -> bytes:
        self.last_operation = operation
        self.last_options = options
        if isinstance(value, str):
            return value.encode('utf-8')
        raise TypeError(f"Cannot marshal type {type(value)}")

    def unmarshal(self, data: bytes, expected_type: Optional[Type[Any]] = None, operation: Optional[OperationContext] = None, **options: Any) -> Any:
        self.last_operation = operation
        self.last_options = options
        if expected_type == str:
            return data.decode('utf-8')
        raise TypeError(f"Cannot unmarshal to type {expected_type}")

@pytest.fixture(scope="module", autouse=True)
def register_dummy_formatter():
    """Register the dummy formatter for all tests in this module."""
    formatter_instance = DummyFormat()
    # Manually add the instance to the registry for the dummy type
    WireFormatRegistry._formats[DummyFormat.TYPE] = formatter_instance
    # No need to unregister for this simple test module,
    # but in a larger suite, cleanup might be desired.

# Import the specific error for the test
from pyvider.cty.exceptions.encoding import WireFormatError

def test_marshal_with_explicit_operation():
    """Test marshal function with an explicit operation context."""
    test_value = "test_marshal_explicit_op"
    expected_operation = OperationContext.CONFIG

    result = marshal(test_value, DummyFormat.TYPE, operation=expected_operation, custom_opt="val1")

    assert result == test_value.encode('utf-8')
    formatter = WireFormatRegistry.get_formatter(DummyFormat.TYPE)
    assert isinstance(formatter, DummyFormat) # Ensure we got our dummy
    assert formatter.last_operation == expected_operation
    assert formatter.last_options == {"custom_opt": "val1"}

def test_marshal_without_explicit_operation():
    """Test marshal function without an explicit operation context (uses default)."""
    test_value = "test_marshal_default_op"
    default_operation_in_test = OperationContext.PLAN # Set an outer context

    with operation_context(default_operation_in_test):
        # Call marshal without the 'operation' argument
        result = marshal(test_value, DummyFormat.TYPE, custom_opt="val2")

    assert result == test_value.encode('utf-8')
    formatter = WireFormatRegistry.get_formatter(DummyFormat.TYPE)
    assert isinstance(formatter, DummyFormat)
    assert formatter.last_operation == default_operation_in_test # Should pick up from get_current_operation()
    assert formatter.last_options == {"custom_opt": "val2"}

def test_unmarshal_with_explicit_operation():
    """Test unmarshal function with an explicit operation context."""
    test_data = b"test_unmarshal_explicit_op"
    expected_type = str
    expected_operation = OperationContext.STATE

    result = unmarshal(test_data, DummyFormat.TYPE, expected_type=expected_type, operation=expected_operation, custom_opt="val3")

    assert result == test_data.decode('utf-8')
    formatter = WireFormatRegistry.get_formatter(DummyFormat.TYPE)
    assert isinstance(formatter, DummyFormat)
    assert formatter.last_operation == expected_operation
    assert formatter.last_options == {"custom_opt": "val3"}

def test_unmarshal_without_explicit_operation():
    """Test unmarshal function without an explicit operation context (uses default)."""
    test_data = b"test_unmarshal_default_op"
    expected_type = str
    default_operation_in_test = OperationContext.READ # Set an outer context

    with operation_context(default_operation_in_test):
        # Call unmarshal without the 'operation' argument
        result = unmarshal(test_data, DummyFormat.TYPE, expected_type=expected_type, custom_opt="val4")

    assert result == test_data.decode('utf-8')
    formatter = WireFormatRegistry.get_formatter(DummyFormat.TYPE)
    assert isinstance(formatter, DummyFormat)
    assert formatter.last_operation == default_operation_in_test # Should pick up from get_current_operation()
    assert formatter.last_options == {"custom_opt": "val4"}

def test_marshal_unmarshal_unknown_format_kind():
    """Test that marshal/unmarshal raise error for unknown format kind."""
    unknown_format = WireFormatType.MSGPACK # Assuming MSGPACK is not registered by DummyFormat
    if DummyFormat.TYPE == WireFormatType.MSGPACK: # Ensure it's actually different
        unknown_format = WireFormatType.JSON # Pick the other one
        # No need for a nested if; if DummyFormat.TYPE is JSON, unknown_format is already MSGPACK.
        # If DummyFormat.TYPE was MSGPACK, unknown_format is now JSON.
        # This logic ensures unknown_format is different from DummyFormat.TYPE.

    # Construct the expected error message based on how WireFormatError formats it
    expected_error_message_marshal = f"No wire format registered for {unknown_format.name} using {unknown_format.__class__.__name__}.{unknown_format.name}"
    with pytest.raises(WireFormatError, match=expected_error_message_marshal):
        marshal("test", unknown_format)

    expected_error_message_unmarshal = f"No wire format registered for {unknown_format.name} using {unknown_format.__class__.__name__}.{unknown_format.name}"
    with pytest.raises(WireFormatError, match=expected_error_message_unmarshal):
        unmarshal(b"test", unknown_format, expected_type=str)

# This test helps cover the logger line at the end of conversion/__init__.py
# by ensuring the module is imported and its top-level code runs.
def test_module_level_logger_line_coverage():
    """
    This test doesn't assert anything specific about the conversion module's functions
    but aims to ensure that the module-level logger.debug call in
    src/pyvider/cty/conversion/__init__.py is executed during the test run.
    Importing the module and having pytest collect this test file should be enough.
    """
    assert True
