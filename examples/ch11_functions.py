#!/usr/bin/env python3
from examples.example_utils import configure_for_example
from pyvider.cty import CtyNumber
from pyvider.cty.functions import abs_fn

configure_for_example()

# NOTE: As of this version, pyvider.cty does not support arithmetic
# operations like addition directly on CtyNumber values. The following
# is a demonstration of a function that is supported.

number_type = CtyNumber()
num1 = number_type.validate(-10)

# For available functions, you import them from the functions module
abs_result = abs_fn(num1)
assert abs_result.raw_value == 10

print("Functions examples ran successfully.")

# 🐍🎯📄🪄
