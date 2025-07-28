from pyvider.cty import CtyNumber
from pyvider.cty.functions import add, abs_fn

num1 = CtyNumber().validate(10)
num2 = CtyNumber().validate(-20)

# Add two numbers
sum_val = add(num1, num2)
assert sum_val.raw_value == -10

# Get the absolute value
abs_val = abs_fn(num2)
assert abs_val.raw_value == 20

print("Chapter 11 examples successful.")
