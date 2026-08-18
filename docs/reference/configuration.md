# Configuration

`pyvider.cty` provides configuration options to customize behavior for different use cases and environments.

## Configuration System

The library uses a configuration system based on environment variables, with sensible defaults for all settings. Configuration is handled through the `CtyConfig` class.

### Accessing Configuration

```python
from pyvider.cty.config.runtime import CtyConfig

# Get current configuration from environment
config = CtyConfig.get_current()

print(f"Type inference cache enabled: {config.enable_type_inference_cache}")
```

## Available Configuration Options

### Type Inference Cache

**Environment Variable**: `PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE`
**Default**: `True`
**Type**: Boolean

Controls whether the type inference cache is enabled for performance optimization.

```bash
# Disable type inference caching
export PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE=false
```

**When to disable:**
- During development when you want fresh type inference on every operation
- In testing scenarios where caching might hide bugs
- In memory-constrained environments

**When to enable (default):**
- Production environments for better performance
- Applications with repeated type inference operations
- Normal usage scenarios

## Configuration Constants

The library defines several important constants in `pyvider.cty.config.defaults`. While these are not configurable at runtime, they define the behavior of the library:

### Validation Limits

- **`MAX_VALIDATION_DEPTH`**: Maximum depth for nested validation (protects against stack overflow). **Derived, not fixed** — see [Validation Depth Management](#validation-depth-management).
- **`MAX_OBJECT_REVISITS`**: `100` - Maximum times an object can be revisited during validation
- **`MAX_VALIDATION_TIME_MS`**: `30000` (30 seconds) - Timeout for pathological validation cases

### MessagePack Codec Settings

- **`MSGPACK_EXT_TYPE_CTY`**: `0` - Extension type code for cty values in MessagePack
- **`MSGPACK_EXT_TYPE_REFINED_UNKNOWN`**: `12` - Extension type code for refined unknowns
- **`MSGPACK_USE_BIN_TYPE_TRUE`**: `True` - Use binary type in MessagePack encoding

## Examples

### Custom Configuration in Tests

```python
import os
from pyvider.cty.config.runtime import CtyConfig

# Disable caching for testing
os.environ["PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE"] = "false"

# Get configuration
config = CtyConfig.get_current()
assert config.enable_type_inference_cache is False
```

### Production Configuration

```bash
# .env file or deployment configuration
PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE=true
```

## Validation Depth Management

`MAX_VALIDATION_DEPTH` is **derived from the interpreter's recursion limit**, and it is runtime-configurable.

Each level of nesting costs two Python frames — the recursion guard's wrapper, then the `validate` it wraps — so the deliverable depth is bounded by `sys.getrecursionlimit()`. Deriving the limit this way keeps the documented ceiling and the real one the same number, rather than letting a hardcoded figure drift away from what the interpreter can actually honour.

```python
import sys
from pyvider.cty.config.defaults import MAX_VALIDATION_DEPTH

print(sys.getrecursionlimit())   # 1000
print(MAX_VALIDATION_DEPTH)      # 449  == (1000 - 100) // 2 - 1
```

Raising the recursion limit raises the depth with it; validation nested exactly `MAX_VALIDATION_DEPTH` deep is guaranteed to validate, and one level past it is a controlled `unknown` rather than a `RecursionError`.

To pin a fixed limit instead, set `PYVIDER_CTY_MAX_VALIDATION_DEPTH` to a positive integer. Lower it to fail earlier; raise it only if you have also raised `sys.setrecursionlimit` to match.

```bash
export PYVIDER_CTY_MAX_VALIDATION_DEPTH=200
```

The live value in force is `get_recursion_context().max_depth_allowed`, which is derived per context and so tracks a recursion limit changed after import.

If you encounter depth limit errors, consider:
1. Restructuring your data to be less deeply nested
2. Breaking validation into smaller chunks
3. Using dynamic types for extremely nested structures

## Default Values Reference

All configuration defaults are centralized in `pyvider.cty.config.defaults`:

| Constant | Default | Purpose |
|----------|---------|---------|
| `MAX_VALIDATION_DEPTH` | derived from `sys.getrecursionlimit()` | Recursion depth limit for validation |
| `MAX_OBJECT_REVISITS` | 100 | Circular reference detection limit |
| `MAX_VALIDATION_TIME_MS` | 30000 | Validation timeout (milliseconds) |
| `ENABLE_TYPE_INFERENCE_CACHE` | True | Type inference caching |

## Advanced: Using Configuration in Custom Types

If you're implementing custom types or validators, you can access configuration:

```python
from pyvider.cty.config.runtime import CtyConfig
from pyvider.cty.config.defaults import MAX_VALIDATION_DEPTH

class MyCustomValidator:
    def __init__(self):
        # Access runtime config
        self.config = CtyConfig.get_current()

        # Access constants
        self.max_depth = MAX_VALIDATION_DEPTH

    def validate(self, data):
        if self.config.enable_type_inference_cache:
            # Use cached inference
            pass
        else:
            # Fresh inference
            pass
```

## Environment Variable Prefix

All pyvider.cty environment variables use the prefix `PYVIDER_CTY_`.

**Example variables:**
- `PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE`

## Related Documentation

- **[Validation](../user-guide/core-concepts/validation.md)** - Understanding validation depth limits
- **[Context](../api/context.md)** - Validation depth tracking
- **[Troubleshooting](troubleshooting.md)** - Handling configuration-related issues
