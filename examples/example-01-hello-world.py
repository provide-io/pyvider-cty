#!/usr/bin/env python3
# docs/examples/example-01-hello-world.py

from pyvider.cty import CtyString
from pyvider.cty.exceptions import CtyValidationError

# 1. Define the desired CtyType.
string_type = CtyString()

# 2. Validate a raw Python value against the type.
# The .validate() method is the canonical way to create a CtyValue.
# It returns a CtyValue instance if validation succeeds.
try:
    string_val = string_type.validate("Hello, World!")

    # 3. Access the type-safe value.
    # The .type property confirms its CtyType.
    # The .raw_value property gives access to the underlying Python value.
    print(f"Validated CtyValue of type: {string_val.type}")
    print(f"Raw value: {string_val.raw_value}")

except CtyValidationError as e:
    print(f"Validation failed: {e}")
