#!/usr/bin/env python3
from examples.example_utils import configure_for_example
from pyvider.cty import CtyList, CtyString
from pyvider.cty.parser import parse_tf_type_to_ctytype

configure_for_example()

tf_type_string = ["list", "string"]
cty_type = parse_tf_type_to_ctytype(tf_type_string)

assert cty_type == CtyList(element_type=CtyString())

print("Terraform interop examples ran successfully.")
