#!/usr/bin/env python3
# docs/examples/example-05-map-manipulation.py

from pyvider.cty import CtyMap, CtyNumber, CtyString

# Import specific exceptions for better handling
from pyvider.cty.exceptions import CtyError, CtyMapValidationError, CtyValidationError

# Define a map type with string keys and number values
config_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

# Create and validate map data
config_data = {"max_connections": 100, "timeout": 30, "retry_limit": 5}

try:
    # Validate returns a CtyValue instance
    config_val = config_type.validate(config_data)

    # --- Access/Manipulation ---
    print("Initial Config:")
    if not config_val.is_null and not config_val.is_unknown:
        # Iterate over the internal dictionary (.value) of the CtyValue
        # config_val.value is Dict[str, CtyValue]
        for key_str, value_cty in config_val.value.items():
            # Access internal value of the CtyValue value
            print(f"Key: {key_str}, Value: {value_cty.value}")  # Use .value

    # --- Set a new value ---
    # Operates on the CtyValue, returns a NEW CtyValue
    # Assumes CtyValue.set exists and handles raw python types for key/value
    print("\nAttempting to set 'batch_size'...")
    new_config = config_val.set("batch_size", 1000)
    print("... set operation finished.")

    print("\nConfig after setting 'batch_size':")
    if not new_config.is_null and not new_config.is_unknown:
        # Use CtyValue's get method
        batch_size_val = new_config.get("batch_size")
        if (
            batch_size_val
            and not batch_size_val.is_null
            and not batch_size_val.is_unknown
        ):
            print(f"  batch_size: {batch_size_val.value}")
        else:
            print("  batch_size: Not Found or Null/Unknown")
    else:
        print("  Resulting config is null or unknown.")

    # --- Delete a value ---
    # Operates on the CtyValue, returns a NEW CtyValue
    print("\nAttempting to delete 'timeout'...")
    # Use the 'new_config' which contains 'batch_size'
    modified_config = new_config.delete("timeout")
    print("... delete operation finished.")

    print("\nKeys after deletion (modified object):")
    if not modified_config.is_null and not modified_config.is_unknown:
        # Keys are strings in the internal dict
        print(f"  {list(modified_config.value.keys())}")
    else:
        print("  Resulting config after delete is null or unknown.")

    # --- Verify original is unchanged ---
    print("\nOriginal config keys (should be unchanged):")
    if not config_val.is_null and not config_val.is_unknown:
        print(f"  {list(config_val.value.keys())}")
    else:
        print("  Original config was null or unknown.")


# Catch specific Cty errors first
except (CtyValidationError, CtyMapValidationError, CtyError) as e:
    print(f"\nA CTY Error occurred: {e}")
# Catch potential TypeErrors like the one reported
except TypeError as e:
    print(f"\nA TypeError occurred (potentially the 'int' has no len() issue): {e}")
    # You might want to add more debugging here if it still fails
    import traceback

    traceback.print_exc()
# Catch any other unexpected errors
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
    import traceback

    traceback.print_exc()
