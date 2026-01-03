# 🌊🪢 Pyvider CTY

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-package_manager-FF6B35.svg)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/provide-io/pyvider-cty/actions/workflows/ci.yml/badge.svg)](https://github.com/provide-io/pyvider-cty/actions)

**Pure-Python implementation of the go-cty type system for Terraform tooling**

pyvider.cty provides strong type validation and serialization capabilities for configuration data, designed to work seamlessly with Terraform providers and HashiCorp ecosystem tools.

## ✨ Key Features

- 🎯 **Complete Type System** - Full implementation of go-cty primitives, collections, and structural types
- 🔄 **Cross-Language Compatibility** - JSON/MessagePack serialization for Go interoperability
- ✅ **Type-Safe Validation** - Strong validation with detailed error messages
- 🏷️ **Marks System** - Attach metadata to values without modification
- 🧭 **Path Navigation** - Type-safe access to nested data structures
- 📚 **Standard Library** - Comprehensive collection of type functions

## Quick Start
1. Install: `uv add pyvider-cty`
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
- **Performance**: The library is not optimized for performance-critical applications involving very large or deeply nested data structures. Performance is reasonable for typical use cases.

Copyright (c) provide.io LLC.
