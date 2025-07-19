# 📖 Pyvider Cty Examples

This directory contains a collection of executable examples demonstrating the features and usage patterns of `pyvider.cty`. Each example is designed to be run independently and showcases specific aspects of the type system.

## 🚀 Quick Start

To run the quick start example:

1.  **Navigate to the project root directory** (if not already there).
2.  **Run the client script**:
    ```bash
    python examples/ch02_getting_started.py
    ```
    This script will demonstrate basic type validation.

Each example script automatically configures the Python path to find the `pyvider` modules from the project's `src` directory via `example_utils.py`.

## 📋 Example Files

The examples are named with a `chXX_` prefix corresponding to the main documentation chapter they illustrate.

| File | Description | Relevant Chapter(s) |
|---|---|---|
| **`ch02_getting_started.py`** | 🚀 Basic type validation. | Ch02 |
| **`ch05_primitive_types.py`** | ⚙️ Demonstrates the primitive types. | Ch05 |
| **`ch06_collection_types.py`** | 🚚 Demonstrates the collection types. | Ch06 |
| **`ch07_structural_types.py`** | 📢 Demonstrates the structural types. | Ch07 |
| **`ch08_dynamic_types.py`** | 💻 Demonstrates the dynamic type. | Ch08 |
| **`ch09_capsule_types.py`** | 🔌 Demonstrates the capsule type. | Ch09 |
| **`ch10_marks.py`** | 🔒 Demonstrates marks. | Ch10 |
| **`ch11_functions.py`** | ⚡ Demonstrates functions. | Ch11 |

## 🏃‍♂️ Running Examples

### **Prerequisites**
- Python 3.13+
- `pyvider.cty` installed or source available (i.e., run from the project root).

### **Environment Setup**

The examples are designed to be run from the root of the `pyvider-cty` repository.
Each example script includes:
```python
from examples.example_utils import configure_for_example
configure_for_example()
```
This utility function automatically adjusts `sys.path` to ensure that the `pyvider.cty` library from the `src/` directory and `example_utils` itself are correctly imported.

### **Running Individual Examples**
(Run from the project root directory)
```bash
python examples/ch02_getting_started.py
python examples/ch05_primitive_types.py
python examples/ch06_collection_types.py
python examples/ch07_structural_types.py
python examples/ch08_dynamic_types.py
python examples/ch09_capsule_types.py
python examples/ch10_marks.py
python examples/ch11_functions.py
```

### **Running All Examples**
To run all the examples at once and check for failures, you can use the `run_all_examples.py` script:
```bash
python examples/run_all_examples.py
```

## 🤝 Contributing Examples

When adding new examples:

1. Use the `chXX_descriptive_name.py` format, where `XX` is the primary chapter number it relates to.
2. Include comprehensive docstrings and comments.
3. Add appropriate logging with `from pyvider.telemetry import logger`.
4. Update this README with the new example.
5. Ensure examples are self-contained and runnable where possible.
6. Follow the established patterns for path resolution and `example_utils`.

---

**Happy coding with pyvider-cty!** 🐍🚀
