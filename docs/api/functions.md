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

Every function is built on the `cty/function` framework (`CtyFunction`, `CtyFunctionSpec`, `CtyParameter`) and declares each parameter's null and unknown policy up front, matching go-cty's own `Spec` exactly. Unknown values propagate: the result is an unknown of the correct return type, refined wherever go-cty's stdlib refines it (`upper(unknown_string)` is an unknown *string*, not a bare unknown `dynamic`). Null values do **not** uniformly propagate — most parameters refuse a null argument outright, raising `CtyArgumentError` (`"<func>: argument N must not be null"`), and only the handful of parameters go-cty itself marks `AllowNull` (for example `coalesce`, `merge`, `tostring`) accept one.

```python
from pyvider.cty import CtyString
from pyvider.cty.functions import upper

null_val = CtyString().validate(None)
try:
    upper(null_val)
except Exception as e:
    print(f"{type(e).__name__}: {e}")  # CtyArgumentError: upper: argument 0 must not be null
```

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
