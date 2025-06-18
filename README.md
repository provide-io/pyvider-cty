# pyvider.cty

⚠️ **PREVIEW RELEASE** ⚠️

This is a preview release (v0.1.0-preview1) of pyvider.cty. While the core functionality is complete and well-tested, this release is intended for early adopters and feedback gathering. Please report any issues or suggestions.

## Overview

`pyvider.cty` is a pure-Python implementation of the [go-cty](https://github.com/zclconf/go-cty) type system, providing strong type validation and serialization capabilities for configuration data. It's designed to work seamlessly with Terraform providers and other HashiCorp ecosystem tools.

## Features

- 🎯 **Complete Type System**: Primitives, collections, and structural types
- 🔄 **Cross-Language Compatibility**: Interoperates with go-cty
- 📦 **Multiple Serialization Formats**: JSON and MessagePack support
- 🛡️ **Type Safety**: Strong validation at value creation
- 🏷️ **Marks System**: Attach metadata without modifying values
- 🗺️ **Path Navigation**: Type-safe access to nested data

## Installation

```bash
pip install pyvider-cty==0.1.0-preview1
```

## Quick Start

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyList, CtyValue

# Define a type schema
user_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
    "hobbies": CtyList(element_type=CtyString())
})

# Create a value matching the schema
user = CtyValue.object(user_type, {
    "name": "Alice",
    "age": 30,
    "hobbies": [
        "reading",
        "hiking"
    ]
})

# Access values
# The .value attribute gives the underlying Python value
print(user["name"].value)
print(user["age"].value)

# Example of accessing list elements
print("Hobbies:")
# user["hobbies"] is a CtyValue; user["hobbies"].value is the Python list of CtyValues
for hobby_val in user["hobbies"].value:
    print(f"- {hobby_val.value}") # hobby_val is a CtyValue; hobby_val.value is the Python string
```
```
```
```

## Documentation

- [Type System Overview](src/pyvider/cty/README.md)
- [API Reference](docs/api/)
- [Examples](examples/)
- [Contributing Guidelines](CONTRIBUTING.md)

## Known Limitations

- **Python 3.13+ Required**: Due to advanced type features used
- **MessagePack Compatibility**: Some edge cases with go-cty interop
- **Performance**: Not yet optimized for very large data structures

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.

## Support

- 📧 Email: code@provide.io
- 🐛 Issues: [GitHub Issues](https://github.com/provide/pyvider-cty/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/provide/pyvider-cty/discussions)
