#!/usr/bin/env python3
from pyvider.cty import CtyNumber
from pyvider.cty.functions import cty_add
from examples.example_utils import configure_for_example

configure_for_example()

num1 = CtyNumber(10)
num2 = CtyNumber(20)

result = cty_add(num1, num2)

assert result.raw_value == 30

print("Functions examples ran successfully.")
