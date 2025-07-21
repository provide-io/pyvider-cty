# Chapter 14: Contributing to Pyvider Cty

Thank you for your interest in contributing to `pyvider.cty`! We welcome contributions from the community to help improve and evolve the framework.

## How to Contribute

1.  **Reporting Bugs**: If you find a bug, please open an issue on the project's GitHub repository. Include as much detail as possible.

2.  **Suggesting Enhancements or New Features**: If you have ideas for new features or improvements, please open an issue on GitHub to discuss them.

3.  **Pull Requests**: If you'd like to contribute code:
    *   Please first open an issue to discuss the change you wish to make.
    *   Fork the repository and create a new branch for your feature or bug fix.
    *   Write clean, well-tested, and well-documented code.
    *   Ensure your changes pass all existing tests (`pytest`).
    *   Add new tests to cover your changes.
    *   Follow the existing code style.
    *   Submit a pull request with a clear description of your changes.

## Development Setup

If you plan to contribute code, you'll need to set up a development environment:

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd pyvider-cty
    ```

2.  **Install dependencies**: It's highly recommended to use a virtual environment.
    ```bash
    # Create and activate a virtual environment
    python -m venv .venv
    source .venv/bin/activate

    # Install dependencies
    pip install -e .[dev]
    ```

3.  **Running Tests**:
    ```bash
    pytest
    ```

We look forward to your contributions!
