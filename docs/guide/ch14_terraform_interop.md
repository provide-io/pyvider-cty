# Chapter 14: Terraform Interoperability

`pyvider.cty` is designed to be compatible with Terraform's type system. This allows you to work with Terraform configurations and state files in a type-safe way.

## Parsing Terraform Type Strings

The `parse_tf_type_to_ctytype` function in the `pyvider.cty.parser` module is used to parse Terraform's JSON-based type constraint strings into `CtyType` objects.

For example, to parse the Terraform type string `["list", "string"]`, you would do the following:

```python
from pyvider.cty.parser import parse_tf_type_to_ctytype
from pyvider.cty import CtyList, CtyString

tf_type_string = ["list", "string"]
cty_type = parse_tf_type_to_ctytype(tf_type_string)

assert cty_type == CtyList(element_type=CtyString())
```

This is useful for creating `CtyType` objects from schemas defined in Terraform providers.
