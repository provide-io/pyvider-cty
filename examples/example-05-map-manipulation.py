#!/usr/bin/env python3
# docs/examples/example-05-map-manipulation.py

from pyvider.cty import CtyMap, CtyNumber, CtyString
from pyvider.cty.exceptions import CtyValidationError

# --- Immutable Update Pattern for CtyValue using Ergonomic Helpers ---
# CtyValue objects are immutable. The new helper methods provide a clean,
# fluent API to create modified copies without manual re-validation.

try:
    # 1. Define a map type and create an initial CtyValue.
    config_type = CtyMap(value_type=CtyNumber())
    initial_data = {"max_connections": 100, "timeout": 30}
    config_val = config_type.validate(initial_data)

    print("Initial Config:")
    for key, value_cty in config_val.raw_value.items():
        print(f"  {key}: {value_cty.raw_value}")

    # --- Operation: Add and update keys using chained helpers ---
    print("\nAdding 'batch_size' and updating 'timeout'...")
    
    # The helper methods return a new, validated CtyValue instance.
    new_config_val = (
        config_val
        .with_key("batch_size", 1000)
        .with_key("timeout", 60)
    )

    print("Config after adding and updating:")
    for key, value_cty in new_config_val.raw_value.items():
        print(f"  {key}: {value_cty.raw_value}")

    # --- Operation: Delete a key ---
    print("\nDeleting 'max_connections'...")
    
    final_config_val = new_config_val.without_key("max_connections")

    print("Final config keys:")
    print(f"  {list(final_config_val.raw_value.keys())}")

    # --- Verify original is unchanged ---
    print("\nOriginal config keys (should be unchanged):")
    print(f"  {list(config_val.raw_value.keys())}")
    print(f"Original timeout value: {config_val['timeout'].raw_value}")

except CtyValidationError as e:
    print(f"A CTY validation error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
