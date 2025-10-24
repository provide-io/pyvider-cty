# CTY Validation

The `pyvider.cty.validation` module provides utilities for managing validation context and preventing infinite recursion during validation of deeply nested or circular data structures.

Key components:
- **`ValidationContext`** - Context manager that tracks validation depth to prevent stack overflow
- **`MAX_VALIDATION_DEPTH`** - Configurable maximum depth limit (default: 1000 levels)
- **Recursion protection** - Automatically enforced depth limits that raise errors before stack overflow occurs

The validation context is used internally by all types during the validation process. You typically won't need to interact with it directly unless you're implementing custom types or need to adjust depth limits for extremely deep data structures.

For comprehensive validation documentation, see: **[User Guide: Validation](../user-guide/core-concepts/validation.md)**

---

::: pyvider.cty.validation
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
