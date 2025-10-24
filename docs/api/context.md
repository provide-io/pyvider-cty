# CTY Context

The `pyvider.cty.context` module provides context managers and utilities for tracking state during type operations, particularly validation.

Key components:
- **`ValidationContext`** - Manages validation state and prevents infinite recursion
- **Thread-local state** - Validation context is stored per-thread for thread safety
- **Depth tracking** - Monitors nesting depth to prevent stack overflow

The context system is used internally by the validation system. You typically won't interact with it directly unless you're:
- Implementing custom types that need to participate in recursion detection
- Adjusting validation depth limits for extremely deep structures
- Debugging validation behavior

The validation context automatically tracks how deep the validation has recursed into nested structures and raises an error if the maximum depth is exceeded, protecting against malicious or malformed data that could cause stack overflow.

---

::: pyvider.cty.context
    options:
      show_source: true
      show_root_heading: true
      members_order: source
      show_if_no_docstring: false
      filters:
        - "!^_"
        - "^__init__$"
