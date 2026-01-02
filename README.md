# pyvider.cty

**PREVIEW RELEASE**

This is a preview release of pyvider.cty. While the core functionality is complete and well-tested, this release is intended for early adopters and feedback gathering. Please report any issues or suggestions.

## Key Features
- Pure-Python implementation of the go-cty type system.
- Strong type validation and serialization for configuration data.
- Designed for Terraform provider and tooling integrations.

## Quick Start
1. Install: `uv pip install pyvider-cty`
2. Follow the [Getting Started guide](https://github.com/provide-io/pyvider-cty/blob/main/docs/getting-started/index.md).
3. See the [Quick Example](#quick-example) below.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Getting Started](https://github.com/provide-io/pyvider-cty/blob/main/docs/getting-started/index.md)** - Quick start and installation guide
- **[User Guide](https://github.com/provide-io/pyvider-cty/blob/main/docs/user-guide/index.md)** - Complete guide to all features
- **[How-To Guides](https://github.com/provide-io/pyvider-cty/blob/main/docs/how-to/index.md)** - Practical task-oriented guides
- **[API Reference](https://github.com/provide-io/pyvider-cty/blob/main/docs/api/index.md)** - Complete API documentation

Or start with the **[documentation index](https://github.com/provide-io/pyvider-cty/blob/main/docs/index.md)**.

## Development
- See [CLAUDE.md](https://github.com/provide-io/pyvider-cty/blob/main/CLAUDE.md) for local development notes.
- Run `uv sync --extra dev` to set up the dev environment.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/provide-io/pyvider-cty/blob/main/CONTRIBUTING.md) for details.

## License

Apache License 2.0. See [LICENSE](https://github.com/provide-io/pyvider-cty/blob/main/LICENSE) for details.

## Overview

`pyvider.cty` is a pure-Python implementation of the [go-cty](https://github.com/zclconf/go-cty) type system, providing strong type validation and serialization capabilities for configuration data. It's designed to work seamlessly with Terraform providers and other HashiCorp ecosystem tools.

**Key Features**: Complete type system, cross-language compatibility via MessagePack, type-safe validation, marks system, path navigation, and comprehensive standard library.

## Installation

```bash
uv add pyvider-cty
```

## Quick Example

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyList

# Define a type schema
user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "hobbies": CtyList(element_type=CtyString()),
    },
    optional_attributes={"age"},
)

# Validate data
user_data = {"name": "Alice", "hobbies": ["reading", "hiking"]}
user_val = user_type.validate(user_data)

# Access validated data
print(f"Name: {user_val['name'].raw_value}")  # Output: Alice
```

## Known Limitations

- **Python 3.11+ Required**: Due to modern type features and syntax used.
- **Performance**: The library is not yet optimized for performance-critical applications involving very large or deeply nested data structures. Performance is reasonable for typical use cases.

Copyright (c) Provide.io LLC.
