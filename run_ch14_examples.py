from pyvider.cty.parser import parse_tf_type_to_ctytype
from pyvider.cty import CtyList, CtyString

tf_type_string = ["list", "string"]
cty_type = parse_tf_type_to_ctytype(tf_type_string)

assert cty_type == CtyList(element_type=CtyString())
print("Chapter 14 examples successful.")
