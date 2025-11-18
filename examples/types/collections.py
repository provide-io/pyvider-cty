#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.example_utils import configure_for_example  # noqa: E402
from pyvider.cty import CtyBool, CtyList, CtyMap, CtyNumber, CtySet, CtyString  # noqa: E402

configure_for_example()

# CtyList
string_list_type = CtyList(element_type=CtyString())
cty_list = string_list_type.validate(["a", "b", "c"])
assert cty_list.raw_value == ["a", "b", "c"]
try:
    string_list_type.validate(["a", "b", 123])
except Exception as e:
    print(f"List validation failed as expected: {e}")

# CtySet
number_set_type = CtySet(element_type=CtyNumber())
cty_set = number_set_type.validate({1, 2, 3})
assert sorted(cty_set.raw_value) == [1, 2, 3]
cty_set_dedup = number_set_type.validate({1, 2, 3})
assert sorted(cty_set_dedup.raw_value) == [1, 2, 3]
try:
    number_set_type.validate({1, 2, "c"})
except Exception as e:
    print(f"Set validation failed as expected: {e}")

# CtyMap
bool_map_type = CtyMap(element_type=CtyBool())
cty_map = bool_map_type.validate({"a": True, "b": False})
assert cty_map.raw_value == {"a": True, "b": False}
try:
    bool_map_type.validate({"a": True, "b": 123})
except Exception as e:
    print(f"Map validation failed as expected: {e}")

print("Collection type examples ran successfully.")

# 🌊🪢🔚
