# tests/test_dynamic.py
from pyvider.cty.encoding.dynamic_value import CtyDynamicValue

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
        encoded = CtyDynamicValue.encode(value)
        decoded = CtyDynamicValue.decode(encoded)
        assert decoded == value, f"Roundtrip failed for {value}"
