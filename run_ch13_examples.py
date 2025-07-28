from pyvider.cty import CtyObject, CtyString
from pyvider.cty.path import CtyPath

# Creating a Path
path_to_attr = CtyPath.get_attr("my_attr")
path_to_index = CtyPath.index(0)
path_to_key = CtyPath.key("my_key")
complex_path = CtyPath.get_attr("users").index(0).get_attr("name")
print("Path creation successful.")

# Applying a Path
user_type = CtyObject({"name": CtyString()})
user_val = user_type.validate({"name": "Alice"})
name_path = CtyPath.get_attr("name")
name_val = name_path.apply_path(user_val)
assert name_val.raw_value == "Alice"
print("Path application successful.")

# Applying a Path to a Type
user_type = CtyObject({"name": CtyString()})
name_path = CtyPath.get_attr("name")
name_type = name_path.apply_path_type(user_type)
assert name_type == CtyString()
print("Path application to type successful.")
