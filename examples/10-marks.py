#!/usr/bin/env python3

from pyvider.cty import CtyString

# Marking a Value
cty_string = CtyString().validate("hello")
sensitive_string = cty_string.with_marks({"sensitive"})
print("Marking a value successful.")

# Add multiple marks
private_sensitive_string = cty_string.with_marks({"sensitive", "private"})
print("Adding multiple marks successful.")

# Checking for Marks
assert sensitive_string.has_mark("sensitive") is True
assert sensitive_string.has_mark("private") is False
print("Checking for marks successful.")

# Get all marks
assert private_sensitive_string.marks == {"sensitive", "private"}
print("Getting all marks successful.")
