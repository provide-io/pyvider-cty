#!/usr/bin/env python3
from examples.example_utils import configure_for_example
from pyvider.cty import CtyDynamic, CtyList, CtyNumber, CtyString

configure_for_example()

dynamic_type = CtyDynamic()

cty_string = dynamic_type.validate("hello")
# The .value attribute holds the inner CtyValue with the inferred type.
assert isinstance(cty_string.value.type, CtyString)

cty_number = dynamic_type.validate(123)
assert isinstance(cty_number.value.type, CtyNumber)

dynamic_list_type = CtyList(element_type=CtyDynamic())
cty_list = dynamic_list_type.validate(["hello", 123, True])

print("Dynamic type examples ran successfully.")

# 🐍🎯📄🪄
