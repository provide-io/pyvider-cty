# Codec API

The `pyvider.cty.codec` module provides serialization and deserialization capabilities for `CtyValue` instances, enabling cross-language compatibility with go-cty and efficient binary storage.

Key functions:
- **`cty_to_msgpack(value, type)`** - Serialize a `CtyValue` to MessagePack binary format
- **`cty_from_msgpack(data, type)`** - Deserialize MessagePack binary data back to a `CtyValue`

**MessagePack Format**: The MessagePack serialization format is **fully compatible** with HashiCorp's go-cty library, enabling true cross-language data exchange. This is the recommended format for interoperability with Terraform providers and other Go-based tools.

**JSON Support**: For JSON encoding/decoding, use the `jsonencode()` and `jsondecode()` functions from `pyvider.cty.functions`. These operate on `CtyValue` objects and return `CtyValue` objects containing JSON strings, rather than providing direct serialization/deserialization.

**Type Preservation**: MessagePack serialization preserves type information, null values, unknown values, and marks, ensuring complete fidelity when round-tripping data.

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
