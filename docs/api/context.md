# CTY Context

The `pyvider.cty.context` module provides utilities for tracking validation depth during type operations.

Key components:
- **`deeper_validation()`** - Context manager to safely increment and decrement validation depth
- **`get_validation_depth()`** - Returns the current validation depth
- **`MAX_VALIDATION_DEPTH`** - Configurable maximum depth limit (default: 500 levels)
- **Context-local state** - Validation depth is stored per-context using `contextvars` for thread and async safety

The context system is used internally by the validation system to track nesting depth. You typically won't interact with it directly unless you're:
- Implementing custom types that need to participate in depth tracking
- Adjusting validation depth limits for extremely deep structures
- Debugging validation behavior

The context automatically tracks how deep the validation has recursed into nested structures and raises an error if the maximum depth is exceeded, protecting against malicious or malformed data that could cause stack overflow.

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
