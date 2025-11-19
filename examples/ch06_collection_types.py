#!/usr/bin/env python3
from examples.example_utils import configure_for_example
from pyvider.cty import CtyBool, CtyList, CtyMap, CtyNumber, CtySet, CtyString

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
