# CTY Functions

The `pyvider.cty.functions` module provides a comprehensive standard library of type-safe functions for manipulating `CtyValue` instances. All functions operate on `CtyValue` objects and return new `CtyValue` objects, maintaining immutability throughout.

Functions are organized into categories:
- **Numeric** - Mathematical operations (add, multiply, abs_fn, ceil_fn, etc.)
- **String** - Text manipulation (upper, lower, trim, split, regex, etc.)
- **Collection** - List and map operations (concat, flatten, keys, values, etc.)
- **Comparison** - Value comparisons (equal, greater_than, less_than, etc.)
- **Conversion** - Type conversions (to_string, to_number, to_bool)
- **Encoding** - Serialization (jsonencode, jsondecode, csvdecode)
- **Date/Time** - Timestamp operations (formatdate, timeadd)

All functions perform proper null and unknown value handling, propagating these special states through operations as appropriate.

For a complete overview with descriptions, see: **[User Guide: Functions](../user-guide/advanced/functions.md)**

---

::: pyvider.cty.functions
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
