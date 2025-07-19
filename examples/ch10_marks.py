#!/usr/bin/env python3
from pyvider.cty import CtyString
from examples.example_utils import configure_for_example

configure_for_example()

cty_string = CtyString().validate("hello")

sensitive_string = cty_string.with_marks(("sensitive",))

private_sensitive_string = cty_string.with_marks(("sensitive", "private"))

assert sensitive_string.has_mark("sensitive") is True
assert sensitive_string.has_mark("private") is False

assert sensitive_string.marks == {"sensitive"}

print("Marks examples ran successfully.")
