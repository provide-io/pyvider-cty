# CTY Validation

The `pyvider.cty.validation` module provides utilities for preventing infinite recursion during validation of deeply nested or circular data structures.

Key components:
- **`RecursionContext`** - Tracks visited objects during validation to detect cycles
- **`RecursionDetector`** - Manages recursion detection state
- **`with_recursion_detection`** - Decorator that adds recursion detection to validation methods
- **`get_recursion_context()`** - Returns the current recursion context
- **`clear_recursion_context()`** - Clears the recursion detection state
- **`validate_config(schema, config)`** - Convenience function for validating configurations against schemas (raises `CtyValidationError` on failure)

The recursion detection system is used internally by all types during the validation process. You typically won't need to interact with it directly unless you're implementing custom types that need to participate in cycle detection.

**Usage Example:**

```python
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.validation import validate_config

schema = CtyObject(attribute_types={"name": CtyString()})
config = {"name": "Alice"}

# This validates and raises on error, but doesn't return the CtyValue
validate_config(schema, config)

# For most use cases, prefer calling validate() directly on the type:
validated_value = schema.validate(config)  # Returns CtyValue
```

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
