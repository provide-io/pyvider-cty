# Conversion

`pyvider.cty` provides functions for converting between `CtyValue`s and raw Python values.

## `cty_to_native`

The `cty_to_native` function converts a `CtyValue` to its raw Python representation.

```python
from pyvider.cty import CtyString
from pyvider.cty.conversion import cty_to_native

string_type = CtyString()
cty_value = string_type.validate("hello")

raw_value = cty_to_native(cty_value)
assert raw_value == "hello"
```

## `infer_cty_type_from_raw`

The `infer_cty_type_from_raw` function infers the most specific `CtyType` from a raw Python value.

```python
from pyvider.cty import CtyString, CtyNumber, CtyBool, CtyList, CtyObject
from pyvider.cty.conversion import infer_cty_type_from_raw

assert infer_cty_type_from_raw("hello").equal(CtyString())
assert infer_cty_type_from_raw(123).equal(CtyNumber())
assert infer_cty_type_from_raw(True).equal(CtyBool())
assert infer_cty_type_from_raw([1, 2, 3]).equal(CtyList(CtyNumber()))
assert infer_cty_type_from_raw({"name": "Alice", "age": 30}).equal(CtyObject({"name": CtyString(), "age": CtyNumber()}))
```

## Wire Format

`pyvider.cty` also provides a wire format for serializing and deserializing `CtyValue`s. The wire format is a JSON-serializable structure that can be used to send `CtyValue`s over the network or store them in a file.

The `cty_to_msgpack` and `cty_from_msgpack` functions can be used to convert between `CtyValue`s and the wire format.

```python
from pyvider.cty import CtyString
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

string_type = CtyString()
cty_value = string_type.validate("hello")

# Serialize to msgpack
msgpack_data = cty_to_msgpack(cty_value, string_type)

# Deserialize from msgpack
new_cty_value = cty_from_msgpack(msgpack_data, string_type)

assert new_cty_value.equal(cty_value)
```
