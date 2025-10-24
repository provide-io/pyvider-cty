# Pyvider Cty Examples

This directory contains a collection of executable examples demonstrating the features and usage patterns of `pyvider.cty`. Each example is designed to be run independently and showcases specific aspects of the type system.

## Quick Start

To run an example:

1. **Navigate to the project root directory** (if not already there).
2. **Run an example script**:
    ```bash
    python examples/getting-started/quick-start.py
    ```

Each example script automatically configures the Python path to find the `pyvider` modules from the project's `src` directory via `example_utils.py`.

## Example Organization

Examples are organized by topic in the following directories:

### Getting Started

**Location**: `examples/getting-started/`

- **quick-start.py** - The 5-minute quick start example demonstrating basic validation

### Type Examples

**Location**: `examples/types/`

- **primitives.py** - String, Number, and Bool types
- **collections.py** - List, Map, and Set types
- **structural.py** - Object and Tuple types
- **dynamic.py** - Dynamic type usage
- **capsule.py** - Capsule types for opaque data

### Advanced Examples

**Location**: `examples/advanced/`

- **marks.py** - Attaching metadata to values
- **functions.py** - Using built-in functions
- **serialization.py** - MessagePack serialization
- **path-navigation.py** - Navigating nested structures
- **terraform-interop.py** - Working with Terraform types

## Running Examples

### Prerequisites

- Python 3.11 or higher
- `pyvider.cty` installed or source available (i.e., run from the project root)

### Environment Setup

Each example script includes a utility function that automatically adjusts `sys.path` to ensure that the `pyvider.cty` library from the `src/` directory is correctly imported.

### Running All Examples

To run all the examples at once and check for failures, use the `run_all_examples.py` script:

```bash
python examples/run_all_examples.py
```

## Example Index

| File | Category | Description |
|------|----------|-------------|
| **getting-started/quick-start.py** | Getting Started | Basic type validation |
| **types/primitives.py** | Types | Primitive types demonstration |
| **types/collections.py** | Types | Collection types demonstration |
| **types/structural.py** | Types | Structural types demonstration |
| **types/dynamic.py** | Types | Dynamic type demonstration |
| **types/capsule.py** | Types | Capsule type demonstration |
| **advanced/marks.py** | Advanced | Marks system demonstration |
| **advanced/functions.py** | Advanced | Built-in functions demonstration |
| **advanced/serialization.py** | Advanced | Serialization demonstration |
| **advanced/path-navigation.py** | Advanced | Path navigation demonstration |
| **advanced/terraform-interop.py** | Advanced | Terraform interoperability demonstration |

## Further Reading

For more information and comprehensive documentation:

- **[Getting Started Guide](https://github.com/provide-io/pyvider-cty/blob/main/docs/getting-started/index.md)** - Learn the basics
- **[User Guide](https://github.com/provide-io/pyvider-cty/blob/main/docs/user-guide/index.md)** - Comprehensive documentation
- **[How-To Guides](https://github.com/provide-io/pyvider-cty/blob/main/docs/how-to/index.md)** - Task-oriented guides
- **[API Reference](https://github.com/provide-io/pyvider-cty/blob/main/docs/api/index.md)** - Complete API documentation
