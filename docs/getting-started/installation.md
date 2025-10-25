# Installation

This guide will help you install pyvider.cty in your Python project.

## Requirements

- **Python 3.11 or higher** - pyvider.cty uses modern Python type hints and features
- **pip or uv** - Package installer for Python

You can check your Python version with:

```bash
python --version
```

## Installation Methods

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
uv add pyvider-cty
```

This will:
- Add pyvider-cty to your project dependencies
- Install the package and its dependencies
- Update your project's lock file

### Using pip

If you're using pip, you can install pyvider.cty with:

```bash
pip install pyvider-cty
```

### Development Installation

If you want to contribute to pyvider.cty or work with the latest development version:

```bash
# Clone the repository
git clone https://github.com/provide-io/pyvider-cty.git
cd pyvider-cty

# Install in development mode with uv
uv sync

# Or with pip
pip install -e ".[dev]"
```

## Verify Installation

After installation, verify that pyvider.cty is installed correctly:

```python
import pyvider.cty
print(pyvider.cty.__version__)
```

You should see the version number printed without any errors.

## Dependencies

pyvider.cty has minimal dependencies:

- **attrs** - For clean class definitions
- **msgpack** - For MessagePack serialization (go-cty compatibility)
- **provide-foundation** - Foundation utilities and error handling

These will be installed automatically when you install pyvider.cty.

## Next Steps

Now that you have pyvider.cty installed, continue to the **[Quick Start](quick-start.md)** guide to build your first type-safe data structure.
