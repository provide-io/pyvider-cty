# examples/ch14_terraform_interop.py
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from examples.example_utils import configure_for_example
from pyvider.cty import CtyList, CtyString
from pyvider.cty.parser import parse_tf_type_to_ctytype

configure_for_example()

tf_type_string = ["list", "string"]
cty_type = parse_tf_type_to_ctytype(tf_type_string)

assert cty_type == CtyList(element_type=CtyString())

print("Terraform interop examples ran successfully.")

# 🐍⛓️📁🪄
