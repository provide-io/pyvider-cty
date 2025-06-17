#!/usr/bin/env python3
# docs/examples/example-01-hello-world.py
#

from pyvider.cty import CtyString, CtyValue

# Define a simple string type
string_type = CtyString()

# Validate a value against this type
validated = string_type.validate("Hello, World!")

# Create a CtyValue with the validated result
string_val = CtyValue(string_type, validated)

# Access the value
print(f"Value: {string_val.value}")
