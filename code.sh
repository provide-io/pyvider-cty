#!/bin/bash
# 🛠️ Project Patching Script
set -eo pipefail

# --- Logging ---
log_info() { echo -e "ℹ️  $1"; }
log_patch() { echo -e "🩹 $1"; }
log_success() { echo -e "✅ $1"; }

# --- Operations ---
log_info "Applying fixes to example scripts and documentation..."

# --- 1. Fix the assertion in the dynamic types example ---
log_patch "Fixing: examples/ch08_dynamic_types.py"
cat <<'EOF' > examples/ch08_dynamic_types.py
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
EOF

# --- 2. Fix the serialization example to only use implemented functions ---
log_patch "Fixing: examples/ch12_serialization.py"
cat <<'EOF' > examples/ch12_serialization.py
#!/usr/bin/env python3
from examples.example_utils import configure_for_example
from pyvider.cty import CtyNumber, CtyObject, CtyString
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

configure_for_example()

# 1. Define a type and a CtyValue
user_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
user_value = user_type.validate({"name": "Alice", "age": 30})

# 2. Serialize to Msgpack
msgpack_bytes = cty_to_msgpack(user_value, user_type)
print(f"Serialized Msgpack (bytes): {msgpack_bytes!r}")


# 3. Deserialize from Msgpack
reconstructed_value = cty_from_msgpack(msgpack_bytes, user_type)
assert reconstructed_value == user_value
print("\nSuccessfully reconstructed value from Msgpack.")
EOF

# --- 3. Update the serialization documentation to match the implementation ---
log_patch "Fixing: docs/guide/ch12_serialization.md"
cat <<'EOF' > docs/guide/ch12_serialization.md
# Chapter 12: Serialization (Msgpack)

Serialization is the process of converting your in-memory `CtyValue` into a format (like a byte sequence) that can be easily stored or transmitted. Deserialization is the reverse: taking that stored format and faithfully reconstructing the original `CtyValue`.

`pyvider.cty` provides built-in support for **Msgpack**, a binary format that's often more compact and faster to process than JSON. This is the primary format used for `go-cty` interoperability.

## Key Concepts

1.  **Type Fidelity**: `pyvider.cty`'s serialization aims to preserve as much type information and value precision as possible. The serialized form includes information about the value's `cty` type, its actual data, its known/null status, and any marks.

2.  **Handling of Null and Unknown Values**: Null and unknown values are explicitly represented in the serialized output, so they can be correctly restored.

3.  **The Role of `target_type` in Deserialization**: When you deserialize data, you **must** provide the `target_type`—the `CtyType` you expect the data to conform to. This guides the reconstruction process and ensures the data is validated against the correct schema.

## Msgpack Serialization

The `pyvider.cty.codec` module provides functions for Msgpack serialization.

*   `cty_to_msgpack(value: CtyValue, schema: CtyType) -> bytes`: Serializes a `CtyValue` to a Msgpack byte string.
*   `cty_from_msgpack(data: bytes, cty_type: CtyType) -> CtyValue`: Deserializes a Msgpack byte string to a `CtyValue`.

```python
from pyvider.cty import CtyString, CtyObject
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

# 1. Define a type and a CtyValue
user_type = CtyObject({"name": CtyString()})
user_value = user_type.validate({"name": "Alice"})

# 2. Serialize to Msgpack
msgpack_bytes = cty_to_msgpack(user_value, user_type)

# 3. Deserialize from Msgpack
reconstructed_value = cty_from_msgpack(msgpack_bytes, user_type)

assert reconstructed_value == user_value
```
EOF

log_success "Script finished."