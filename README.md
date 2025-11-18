# pyvider.cty

**PREVIEW RELEASE**

This is a preview release of pyvider.cty. While the core functionality is complete and well-tested, this release is intended for early adopters and feedback gathering. Please report any issues or suggestions.

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

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Getting Started](docs/getting-started/index.md)** - Quick start and installation guide
- **[User Guide](docs/user-guide/index.md)** - Complete guide to all features
- **[How-To Guides](docs/how-to/index.md)** - Practical task-oriented guides
- **[API Reference](docs/api/index.md)** - Complete API documentation

Or start with the **[documentation index](docs/index.md)**.

## Known Limitations

- **Python 3.11+ Required**: Due to modern type features and syntax used.
- **Performance**: The library is not yet optimized for performance-critical applications involving very large or deeply nested data structures. Performance is reasonable for typical use cases.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
