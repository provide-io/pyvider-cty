# Codec API

The `pyvider.cty.codec` module provides serialization and deserialization capabilities for `CtyValue` instances, enabling cross-language compatibility with go-cty and efficient binary storage.

Key functions:
- **`cty_to_msgpack(value, type)`** - Serialize a `CtyValue` to MessagePack binary format
- **`cty_from_msgpack(data, type)`** - Deserialize MessagePack binary data back to a `CtyValue`

**MessagePack Format**: The MessagePack serialization format is **fully compatible** with HashiCorp's go-cty library, enabling true cross-language data exchange. This is the recommended format for interoperability with Terraform providers and other Go-based tools.

**JSON Support**: For JSON encoding/decoding, use the `jsonencode()` and `jsondecode()` functions from `pyvider.cty.functions`. These operate on `CtyValue` objects and return `CtyValue` objects containing JSON strings, rather than providing direct serialization/deserialization.

**Type Preservation**: MessagePack serialization preserves type information, null values, unknown values (including refinements on a refined unknown), and unmarked containers with unknown elements, ensuring complete fidelity when round-tripping data.

**Marks Are Not Serializable**: A marked value cannot cross the wire. `cty_to_msgpack()` raises `CtyMarksSerializationError` for any value carrying a mark anywhere in it, matching go-cty's own encoder — marks exist to track things like sensitivity in memory, and silently dropping them on the way to disk or across a process boundary would be the actual bug. Use `unmark_deep()` from `pyvider.cty.marks` to strip marks (and get back the set of marks that were removed) before serializing, and reapply them after decoding if the caller still needs them:

```python
from pyvider.cty import CtyString
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack
from pyvider.cty.marks import unmark_deep

string_type = CtyString()
value = string_type.validate("secret").mark("sensitive")

unmarked_value, marks = unmark_deep(value)
data = cty_to_msgpack(unmarked_value, string_type)
restored = cty_from_msgpack(data, string_type).with_marks(marks)
```

For detailed serialization documentation, see: **[User Guide: Serialization](../user-guide/advanced/serialization.md)**

---

::: pyvider.cty.codec
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
