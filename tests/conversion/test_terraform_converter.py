import pytest
import json
from decimal import Decimal
from typing import Any, Dict, List, cast

from pyvider.cty.conversion.terraform import (
    TerraformFormatConverter,
    serialize_value,
    extract_value,
    TerraformWireFormatConstants as TFC,
    HAS_MSGPACK,
    StateConvertible,
    OperationContext # Assuming OperationContext can be imported for testing
)
from pyvider.cty.conversion.wire import WireFormatError # For testing exceptions

# Mock OperationContext if it's complex or just use None if appropriate
# For serialize_value, an OperationContext is required.
# We can use a default one or mock it if its internal state matters.
# For now, let's assume None can be passed if get_current_operation() handles it,
# or create a simple stand-in if needed.
# The code uses `op_ctx = operation or get_current_operation()`.
# Let's assume get_current_operation() provides a default.
def get_mock_operation_context():
    # This is a simplified mock. If OperationContext has complex behavior,
    # a more sophisticated mock might be needed.
    return OperationContext.DEFAULT # Changed to a valid member

# --- Tests for serialize_value ---
@pytest.mark.parametrize("input_val, expected_serialization", [
    (None, [TFC.NULL, None]),
    (True, [TFC.BOOL, True]),
    (False, [TFC.BOOL, False]),
    (123, [TFC.NUMBER, 123]),
    (123.45, [TFC.NUMBER, 123.45]),
    (Decimal("123.45"), [TFC.NUMBER, "123.45"]),
    (Decimal("123"), [TFC.NUMBER, "123"]), # Should also be string for consistency before marshalling
    ("hello", [TFC.STRING, "hello"]),
    ("", [TFC.STRING, ""]),
    ([1, "two", True], [TFC.TUPLE, [[TFC.NUMBER, 1], [TFC.STRING, "two"], [TFC.BOOL, True]]]),
    ((1, "two", True), [TFC.TUPLE, [[TFC.NUMBER, 1], [TFC.STRING, "two"], [TFC.BOOL, True]]]),
    # Corrected set test case based on repr sorting of {10, True, "two"}
    # repr("two") is "'two'", repr(10) is '10', repr(True) is 'True'. Sorted: "two", 10, True
    ({10, True, "two"}, [TFC.SET, [ [TFC.STRING, "two"], [TFC.NUMBER, 10], [TFC.BOOL, True] ]]),
    ({"a": 1, "b": "two"}, [TFC.OBJECT, {"a": [TFC.NUMBER, 1], "b": [TFC.STRING, "two"]}]),
    ({"nested": {"c": True}}, [TFC.OBJECT, {"nested": [TFC.OBJECT, {"c": [TFC.BOOL, True]}]}]),
    ([], [TFC.TUPLE, []]),
    (set(), [TFC.SET, []]),
    ({}, [TFC.OBJECT, {}]),
])
def test_serialize_value_various_types(input_val: Any, expected_serialization: List[Any]):
    mock_op = get_mock_operation_context()
    assert serialize_value(input_val, operation=mock_op) == expected_serialization

class UnserializableObject:
    def __str__(self) -> str:
        raise TypeError("Cannot be stringified")

class SimpleObject:
    def __str__(self) -> str:
        return "simple_object_str"

def test_serialize_value_unhandled_types():
    mock_op = get_mock_operation_context()
    # Test fallback to str()
    so = SimpleObject()
    assert serialize_value(so, operation=mock_op) == [TFC.STRING, "simple_object_str"]

    # Test fallback to NULL if str() fails
    uo = UnserializableObject()
    assert serialize_value(uo, operation=mock_op) == [TFC.NULL, None]


# --- Tests for extract_value ---
@pytest.mark.parametrize("input_payload, expected_value", [
    ([TFC.NULL, None], None),
    ([TFC.STRING, "hello"], "hello"),
    ([TFC.STRING, ""], ""),
    ([TFC.STRING, None], ""), # As per current logic str(None) if None is payload for string
    ([TFC.NUMBER, "123.45"], 123.45),
    ([TFC.NUMBER, "123"], 123),
    ([TFC.NUMBER, 123], 123),
    ([TFC.NUMBER, 123.0], 123),
    ([TFC.NUMBER, 123.45], 123.45),
    ([TFC.NUMBER, None], None),
    ([TFC.BOOL, True], True),
    ([TFC.BOOL, False], False),
    ([TFC.BOOL, None], False), # As per current logic bool(None) is False
    ([TFC.TUPLE, [[TFC.NUMBER, 1], [TFC.STRING, "two"]]], [1, "two"]),
    ([TFC.LIST, [[TFC.NUMBER, 1], [TFC.STRING, "two"]]], [1, "two"]),
    ([TFC.SET, [[TFC.NUMBER, 1], [TFC.STRING, "two"]]], [1, "two"]), # Order might not be guaranteed by test here, but extract logic is same as list
    ([TFC.OBJECT, {"a": [TFC.NUMBER, 1], "b": [TFC.STRING, "two"]}], {"a": 1, "b": "two"}),
    ([TFC.MAP, {"a": [TFC.NUMBER, 1], "b": [TFC.STRING, "two"]}], {"a": 1, "b": "two"}),
    ([TFC.DYNAMIC, [TFC.STRING, "dynamic_val"]], "dynamic_val"),
    # Cases where input is not [type, payload]
    ("bare_string", "bare_string"),
    (123, 123),
    ([1,2,3], [1,2,3]), # If it's a list not matching [type, payload] structure
    ({"key": "val"}, {"key": "val"}), # If it's a dict not matching [type, payload] structure
    ([[TFC.STRING, "a"], [TFC.STRING, "b"]], ["a", "b"]), # list of serialized values
    ({"k1": [TFC.STRING, "v1"], "k2": [TFC.NUMBER, 10]}, {"k1": "v1", "k2": 10}), # dict of serialized values
])
def test_extract_value_various_types(input_payload: Any, expected_value: Any):
    assert extract_value(input_payload) == expected_value

def test_extract_value_number_conversion_error():
    # Test case where Decimal conversion might fail
    assert extract_value([TFC.NUMBER, "not_a_number"]) == "not_a_number"

# --- Mocks and Helpers for StateConvertible ---
class MockStateConvertible(StateConvertible):
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def to_dict(self) -> Dict[str, Any]:
        return self._data # Corrected from self_data

    def __cty_state_convert__(self, operation: OperationContext) -> Any:
        # Not directly used by serialize_state_convertible, but part of protocol
        return self.to_dict()

def test_serialize_state_convertible():
    mock_op_state = OperationContext.STATE
    mock_op_other = OperationContext.DEFAULT # Changed to a valid member

    sc_simple = MockStateConvertible({"a": 1, "b": "hello", "c": Decimal("10.2")})

    # Test with OperationContext.STATE
    expected_state = {"a": 1, "b": "hello", "c": "10.2"}
    # serialize_state_convertible is not directly exported, tested via serialize_value
    # assert serialize_state_convertible(sc_simple, mock_op_state) == expected_state
    # Instead, test via serialize_value
    assert serialize_value(sc_simple, operation=mock_op_state) == expected_state


    # Test with other OperationContext (e.g., NONE, should use the object wrapper)
    expected_other_op = [TFC.OBJECT, {
        "a": [TFC.NUMBER, 1],
        "b": [TFC.STRING, "hello"],
        "c": [TFC.NUMBER, "10.2"]
    }]
    assert serialize_value(sc_simple, operation=mock_op_other) == expected_other_op

    # Test with nested complex types within StateConvertible
    sc_complex = MockStateConvertible({
        "d": [1,2],
        "e": {"f": True}
    })
    expected_state_complex = {
        "d": [TFC.TUPLE, [[TFC.NUMBER, 1],[TFC.NUMBER, 2]]],
        "e": [TFC.OBJECT, {"f": [TFC.BOOL, True]}]
    }
    assert serialize_value(sc_complex, operation=mock_op_state) == expected_state_complex

    expected_other_op_complex = [TFC.OBJECT, {
        "d": [TFC.TUPLE, [[TFC.NUMBER, 1],[TFC.NUMBER, 2]]],
        "e": [TFC.OBJECT, {"f": [TFC.BOOL, True]}]
    }]
    assert serialize_value(sc_complex, operation=mock_op_other) == expected_other_op_complex


# --- Tests for TerraformFormatConverter ---
class TestTerraformFormatConverter:

    def test_marshal_json_simple(self):
        data = {"key": "value", "num": 123, "dec": Decimal("1.23")}
        expected_bytes = b'["object",{"key":["string","value"],"num":["number",123],"dec":["number","1.23"]}]'
        # To avoid issues with dict ordering in JSON, compare loaded JSON
        result_bytes = TerraformFormatConverter.marshal(data)
        assert json.loads(result_bytes.decode()) == json.loads(expected_bytes.decode())

    def test_unmarshal_json_simple(self):
        json_bytes = b'["object",{"key":["string","value"],"num":["number",123],"dec":["number","1.23"]}]'
        expected_data = {"key": "value", "num": 123, "dec": 1.23}
        assert TerraformFormatConverter.unmarshal(json_bytes) == expected_data

    @pytest.mark.skipif(not HAS_MSGPACK, reason="msgpack not installed")
    def test_marshal_msgpack_simple(self):
        import msgpack # Ensure it's imported for this test
        data = {"key": "value", "num": 123, "dec": Decimal("1.23")}
        # Expected structure after serialize_value, before msgpack
        expected_intermediate = ["object",{"key":["string","value"],"num":["number",123],"dec":["number","1.23"]}]

        result_bytes = TerraformFormatConverter.marshal(data, use_msgpack=True)
        unpacked_result = msgpack.unpackb(result_bytes, raw=False)
        assert unpacked_result == expected_intermediate

    @pytest.mark.skipif(not HAS_MSGPACK, reason="msgpack not installed")
    def test_unmarshal_msgpack_simple(self):
        import msgpack # Ensure it's imported for this test
        intermediate_data = ["object",{"key":["string","value"],"num":["number",123],"dec":["number","1.23"]}]
        msgpack_bytes = msgpack.packb(intermediate_data, default=TerraformFormatConverter._msgpack_default, use_bin_type=True)

        expected_data = {"key": "value", "num": 123, "dec": 1.23}
        assert TerraformFormatConverter.unmarshal(msgpack_bytes) == expected_data

    def test_marshal_error_handling(self):
        class BadSerializable:
            def __str__(self): raise ValueError("Cannot serialize me")

        # serialize_value catches the ValueError and returns [TFC.NULL, None]
        # This then gets marshalled successfully.
        expected_null_serialization = TerraformFormatConverter.marshal(None) # Marshal of [TFC.NULL, None]
        assert TerraformFormatConverter.marshal(BadSerializable()) == expected_null_serialization
        # To make it raise WireFormatError, serialize_value's fallback would need to change
        # or the test would need to mock serialize_value to raise an error directly.

    def test_unmarshal_error_handling_bad_json(self):
        bad_json_bytes = b'{"key": "value"' # Incomplete JSON
        with pytest.raises(WireFormatError, match="Unmarshal failed"):
            TerraformFormatConverter.unmarshal(bad_json_bytes)

    @pytest.mark.skipif(not HAS_MSGPACK, reason="msgpack not installed")
    def test_unmarshal_error_handling_bad_msgpack(self):
        bad_msgpack_bytes = b'\x81\xa3key\xa5value\xc1' # Corrupted msgpack (invalid byte)
        with pytest.raises(WireFormatError, match="Unmarshal failed"):
            TerraformFormatConverter.unmarshal(bad_msgpack_bytes)

    def test_unmarshal_pre_parsed_data(self):
        # Test when data is already a Python object (not bytes)
        pre_parsed = ["object",{"key":["string","value"]}]
        expected = {"key": "value"}
        assert TerraformFormatConverter.unmarshal(pre_parsed) == expected

    # TODO: Add tests for DynamicValue-like input to unmarshal if its structure is defined
    # For now, assuming it's a class with .msgpack or .json attributes
    # Example:
    # class MockDynamicValue:
    #     def __init__(self, json_data=None, msgpack_data=None):
    #         self.json = json_data
    #         self.msgpack = msgpack_data
    #
    # def test_unmarshal_dynamic_value_json(self):
    #     dyn_val = MockDynamicValue(json_data=b'["string", "hello"]')
    #     assert TerraformFormatConverter.unmarshal(dyn_val) == "hello"


# Placeholder for OperationContext if not easily importable or for specific test scenarios
# This might need to be adjusted based on actual OperationContext definition
# For now, the tests use OperationContext.NONE or rely on get_current_operation(),
# which should be fine if get_current_operation() has a default.
# If tests need specific operation contexts, they can be defined or mocked here.

# Example of how OperationContext might be used if it has simple enum-like values
# class MockOperationContext:
#     NONE = "NONE"
#     STATE = "STATE"
#     CONFIG = "CONFIG"

# Replace OperationContext with MockOperationContext in tests if needed,
# e.g., test_serialize_state_convertible(..., operation=MockOperationContext.STATE)

# ``` (This line was causing a syntax error)
