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

## Usage Examples

### Checking Current Validation Depth

```python
from pyvider.cty.context import get_validation_depth, MAX_VALIDATION_DEPTH

# Get current depth (defaults to 0 outside validation)
depth = get_validation_depth()
print(f"Current depth: {depth}")
print(f"Maximum allowed depth: {MAX_VALIDATION_DEPTH}")
```

### Using Depth Tracking in Custom Validation

```python
from pyvider.cty.context import deeper_validation, get_validation_depth
from pyvider.cty import CtyObject, CtyString, CtyList

# When implementing custom validation logic
def validate_nested_structure(data, depth_limit=10):
    """Custom validation with depth tracking."""
    current_depth = get_validation_depth()

    if current_depth > depth_limit:
        raise ValueError(f"Exceeded custom depth limit: {depth_limit}")

    with deeper_validation():
        # Validation depth is now current_depth + 1
        # Process nested data here
        pass

# Example: Validating deeply nested structures
nested_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "children": CtyList(element_type=CtyString())
    }
)

data = {"name": "root", "children": ["child1", "child2"]}
validated = nested_type.validate(data)
```

### Understanding Depth Limits

```python
from pyvider.cty import CtyObject, CtyList, CtyString
from pyvider.cty.context import MAX_VALIDATION_DEPTH

# The default MAX_VALIDATION_DEPTH is 500
# This prevents stack overflow with extremely deep nesting

# Example of structure that would hit depth limits:
def create_deeply_nested_data(depth):
    """Create nested dict with specified depth."""
    if depth == 0:
        return {"value": "leaf"}
    return {"nested": create_deeply_nested_data(depth - 1)}

# This would succeed (within limit)
shallow_data = create_deeply_nested_data(10)

# This would fail if depth > MAX_VALIDATION_DEPTH
try:
    very_deep_data = create_deeply_nested_data(600)
    # Attempting to validate would raise depth error
except RecursionError:
    print("Depth limit exceeded")
```

### Thread and Async Safety

The context system uses `contextvars` for thread-local and async-safe state management:

```python
import asyncio
from pyvider.cty import CtyString
from pyvider.cty.context import get_validation_depth

async def validate_in_context():
    """Validation depth is isolated per async context."""
    string_type = CtyString()

    # Each async context has its own validation depth
    depth = get_validation_depth()
    value = string_type.validate("test")

    return value

# Multiple concurrent validations don't interfere
async def main():
    results = await asyncio.gather(
        validate_in_context(),
        validate_in_context(),
        validate_in_context()
    )
    # Each had independent depth tracking

# asyncio.run(main())
```

## Related Documentation

- **[User Guide: Validation](../user-guide/core-concepts/validation.md)** - Comprehensive validation documentation
- **[Configuration](../reference/configuration.md)** - Configuration options including validation depth limits
- **[Troubleshooting: Recursion Depth](../reference/troubleshooting.md#scenario-5-recursion-depth-exceeded)** - Handling depth limit errors

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
