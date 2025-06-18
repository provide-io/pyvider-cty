#!/usr/bin/env python3
# docs/examples/example-04-serialization.py

# Corrected imports and usage for serialization
from pyvider.cty import CtyNumber, CtyObject, CtyString
from pyvider.cty.conversion import WireFormatType, marshal, unmarshal

# Create a value to serialize
config_type = CtyObject(
    attribute_types={"api_url": CtyString(), "timeout": CtyNumber()}
)

config_data = {"api_url": "https://api.example.com", "timeout": 30}

# Validation returns a CtyValue now, no need to wrap again
config_val = config_type.validate(config_data)

# --- Corrected Serialization/Deserialization ---
# Use CtyWireFormat which delegates to registered formatters (like JsonEncoder)
try:
    # Marshal using the default format (JSON)
    json_bytes = marshal(config_val, format_kind=WireFormatType.JSON)
    print(f"Serialized: {json_bytes.decode('utf-8')}")

    # Unmarshal, assuming JSON format (can add format detection if needed)
    # Pass expected_type=config_type for validation upon unmarshalling
    deserialized = unmarshal(
        json_bytes, format_kind=WireFormatType.JSON, expected_type=config_type
    )
    print(f"Deserialized: {deserialized}")
    # Access deserialized data safely
    if not deserialized.is_null and not deserialized.is_unknown:
        print(f"Deserialized URL: {deserialized['api_url'].value}")
        print(f"Deserialized Timeout: {deserialized['timeout'].value}")

except Exception as e:
    print(f"Serialization/Deserialization Error: {e}")
