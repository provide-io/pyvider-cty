# Welcome to Pyvider CTY

**A powerful and flexible type system for Python, compatible with HashiCorp's go-cty.**

`pyvider.cty` is a pure-Python implementation of the [go-cty](https://github.com/zclconf/go-cty) type system, providing strong type validation and serialization capabilities for configuration data. It's designed to work seamlessly with Terraform providers and other HashiCorp ecosystem tools.

---

## Why Pyvider CTY?

### ⚡ **Expressive and Flexible**
- **Rich Type System**: A comprehensive set of primitive, collection, and structural types to model your data accurately.
- **Dynamic Types**: Handle data with unknown or varying structures using the dynamic type.
- **Capsule Types**: Encapsulate and protect foreign data types within the `cty` system.

### 🛠️ **Developer Experience**
- **Modern Python**: Leverages Python 3.11+ features with complete type annotations.
- **Clear and Concise API**: A simple and intuitive API for defining types, validating data, and working with values.
- **Detailed Diagnostics**: Get detailed error messages and validation diagnostics to quickly identify and fix issues.

### 🏗️ **Robust and Reliable**
- **Immutable Values**: `cty` values are immutable, ensuring data integrity and preventing unintended side effects.
- **Thoroughly Tested**: A comprehensive test suite ensures the library is reliable and production-ready.
- **Battle-Tested Concepts**: Based on the well-established `cty` type system from HashiCorp's Terraform.

### 🔄 **Cross-Language Compatibility**
- **Go-Cty Interoperability**: Serialize and deserialize data in MessagePack format compatible with go-cty.
- **Terraform Integration**: Parse Terraform type strings and work with Terraform data structures.

---

## Quick Example

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyList

# Define a type schema
user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "hobbies": CtyList(element_type=CtyString())
    },
    optional_attributes={"age"}
)

# Validate data
user_data = {
    "name": "Alice",
    "hobbies": ["reading", "hiking"]
}

user_val = user_type.validate(user_data)
print(f"Name: {user_val['name'].raw_value}")
```

---

## Where to Start

<div class="grid cards" markdown>

-   :material-rocket-launch-outline: **[Getting Started](getting-started/index.md)**

    ---

    Install pyvider.cty and learn the basics in 5 minutes

-   :material-book-open-variant: **[User Guide](user-guide/index.md)**

    ---

    Comprehensive guide to types, values, and advanced features

-   :material-wrench: **[How-To Guides](how-to/index.md)**

    ---

    Practical guides for common tasks and use cases

-   :material-api: **[API Reference](api/index.md)**

    ---

    Complete API documentation for all types and functions

</div>

---

## Installation

```bash
# With uv (recommended)
uv add pyvider-cty

# With pip
pip install pyvider-cty
```

---

## Features at a Glance

- 🎯 **Complete Type System**: Primitives, collections, and structural types
- 🔄 **Cross-Language Compatibility**: Interoperates with go-cty via MessagePack
- 🛡️ **Type Safety**: Strong validation at value creation
- 🏷️ **Marks System**: Attach metadata without modifying values
- 🗺️ **Path Navigation**: Type-safe access to nested data
- ⚡ **Full Standard Library**: Comprehensive suite of functions for data manipulation

---

## Community and Support

- **GitHub**: [provide-io/pyvider-cty](https://github.com/provide-io/pyvider-cty)
- **Issues**: [Report bugs or request features](https://github.com/provide-io/pyvider-cty/issues)
- **Contributing**: See our [Contributing Guidelines](https://github.com/provide-io/pyvider-cty/blob/main/CONTRIBUTING.md)

---

## License

Apache License 2.0. See [LICENSE](https://github.com/provide-io/pyvider-cty/blob/main/LICENSE) for details.
