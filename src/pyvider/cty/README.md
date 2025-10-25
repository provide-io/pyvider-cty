# pyvider.cty

**PREVIEW RELEASE**

This is a preview release of pyvider.cty. While the core functionality is complete and well-tested, this release is intended for early adopters and feedback gathering. Please report any issues or suggestions.

## Overview

`pyvider.cty` is a pure-Python implementation of the [go-cty](https://github.com/zclconf/go-cty) type system, providing strong type validation and serialization capabilities for configuration data. It's designed to work seamlessly with Terraform providers and other HashiCorp ecosystem tools.

## Features

- **Complete Type System**: Primitives, collections, and structural types
- **Cross-Language Compatibility**: Interoperates with go-cty via JSON and MessagePack
- **Type Safety**: Strong validation at value creation
- **Marks System**: Attach metadata without modifying values
- **Path Navigation**: Type-safe access to nested data
- **Full Standard Library**: Comprehensive suite of functions for data manipulation

## Core Concepts

### Types

A **Type** defines the shape and constraints of your data. Types in pyvider.cty include:

- **Primitives**: `CtyString`, `CtyNumber`, `CtyBool`
- **Collections**: `CtyList`, `CtyMap`, `CtySet`
- **Structural**: `CtyObject`, `CtyTuple`
- **Special**: `CtyDynamic` (runtime type determination), `CtyCapsule` (opaque data)

### Values

A **Value** is an instance of a type. Values are:

- **Immutable** - Once created, they cannot be changed
- **Type-safe** - They always conform to their type schema
- **Rich** - They carry metadata like marks and null status

### Special Values

- **Null Values**: Represent the explicit absence of a value
- **Unknown Values**: Represent a value that will be known later

## Quick Start Example

```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyList
from pyvider.cty.exceptions import CtyValidationError

# 1. Define a type schema
user_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
    "hobbies": CtyList(element_type=CtyString())
})

# 2. Validate data against the schema
user_data = {
    "name": "Alice",
    "age": 30,
    "hobbies": ["reading", "hiking"]
}

try:
    user_value = user_type.validate(user_data)
    print("Validation successful!")

    # 3. Access validated data
    print(f"Name: {user_value['name'].raw_value}")
    print(f"Age: {user_value['age'].raw_value}")

    # Iterate over hobbies
    for hobby in user_value['hobbies']:
        print(f"Hobby: {hobby.raw_value}")

except CtyValidationError as e:
    print(f"Validation failed: {e}")
```

## Installation

```bash
# With uv (recommended)
uv add pyvider-cty

# With pip
pip install pyvider-cty
```

## Requirements

- **Python 3.11 or higher** - Uses modern Python type hints and features

## Documentation

For complete documentation, see the main project documentation:

- **Getting Started** - Quick start and installation guide
- **User Guide** - Complete guide to all features
- **How-To Guides** - Practical task-oriented guides
- **API Reference** - Complete API documentation

## Serialization

pyvider.cty supports MessagePack serialization that is fully compatible with go-cty:

```python
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

# Serialize
msgpack_bytes = cty_to_msgpack(user_value, user_type)

# Deserialize
reconstructed = cty_from_msgpack(msgpack_bytes, user_type)
```

## License

Apache License 2.0. See LICENSE for details.
