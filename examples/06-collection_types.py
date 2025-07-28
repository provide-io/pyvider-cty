from pyvider.cty import CtyList, CtyString, CtySet, CtyNumber, CtyMap, CtyBool

# CtyList
string_list_type = CtyList(element_type=CtyString())
cty_list = string_list_type.validate(["a", "b", "c"])
assert cty_list.raw_value == ["a", "b", "c"]
print("CtyList example successful.")
try:
    string_list_type.validate(["a", "b", 123])
except Exception as e:
    print(f"CtyList validation failed as expected: {e}")

# CtySet
number_set_type = CtySet(element_type=CtyNumber())
cty_set = number_set_type.validate({1, 2, 3})
assert sorted(list(cty_set.raw_value)) == [1, 2, 3]
cty_set_dedup = number_set_type.validate({1, 2, 2, 3})
assert sorted(list(cty_set_dedup.raw_value)) == [1, 2, 3]
print("CtySet examples successful.")
try:
    number_set_type.validate({1, 2, "c"})
except Exception as e:
    print(f"CtySet validation failed as expected: {e}")

# CtyMap
bool_map_type = CtyMap(element_type=CtyBool())
cty_map = bool_map_type.validate({"a": True, "b": False})
assert cty_map.raw_value == {"a": True, "b": False}
print("CtyMap example successful.")
try:
    bool_map_type.validate({"a": True, "b": 123})
except Exception as e:
    print(f"CtyMap validation failed as expected: {e}")
