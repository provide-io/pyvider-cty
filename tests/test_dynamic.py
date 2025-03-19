# tests/test_dynamic.py
import pytest
from pyvider.cty.encoding.dynamic import DynamicValue

def test_roundtrip():
    test_values = [
        "Hello, world!",
        42,
        3.14,
        True,
        None,
        [1, 2, 3],
        {"name": "John", "age": 30},
        {"items": [1, 2, {"key": "value"}]}
    ]
    
    for value in test_values:
        encoded = DynamicValue.encode(value)
        decoded = DynamicValue.decode(encoded)
        assert decoded == value, f"Roundtrip failed for {value}"
