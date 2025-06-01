# Compatibility Testing Framework for pyvider.cty

This directory contains tools and test cases for ensuring `pyvider.cty` maintains compatibility with the reference `go-cty` implementation. The framework uses `pytest` for test execution and `Hypothesis` for property-based test data generation.

## Overview

The testing strategy involves several components:

1.  **Test Case Definitions (YAML):**
    *   Located in the `tests/compatibility/testcases/` directory.
    *   Each `.yaml` file defines a single, manually specified test scenario, including the cty type, raw input data, and a descriptive name. These are useful for specific edge cases or complex structures that are hard to generate with Hypothesis initially.

2.  **Pytest Test Suite (`test_cty_compatibility.py`):**
    *   This is the main entry point for running tests.
    *   It contains:
        *   Tests that run the YAML-defined test cases by invoking the Python and Go generators and comparing their outputs.
        *   Property-based tests using Hypothesis to generate a wide variety of inputs for basic cty types (string, number, bool), collections (list, map), simple objects, and special values (null, unknown).

3.  **Data Generators (Refactored):**
    *   `py_cty_generator.py`: Python script, now refactored to process a *single* YAML test case file path provided as a command-line argument. It generates:
        *   `py_type.json`: A JSON representation of the `pyvider.cty.CtyType`.
        *   `py_value.json`: A JSON representation of the resulting `pyvider.cty.CtyValue`.
    *   `go_cty_generator.go`: Go program, also refactored to process a *single* YAML test case file path. It can write `go_type.json` and `go_value.json` to disk, or, if the `-stdout` flag is provided, it will print the `go_value.json` content to standard output (used by Hypothesis tests).
    *   For YAML-driven tests, generators output files into `tests/compatibility/output/<test_case_name>/`.
    *   The `*_value.json` files use a standardized format for representing cty values, including special handling for `unknown` and `null` values, to allow for direct comparison.

4.  **Hypothesis Strategies (in `test_cty_compatibility.py`):**
    *   Strategies are defined to generate Python data for various cty types and special values.
    *   This data is then used in property-based tests to drive both `pyvider.cty` and `go-cty` (via the Go generator).

5.  **Comparison Logic (in `test_cty_compatibility.py`):**
    *   Helper functions load and compare the JSON outputs from the Python and Go sides.
    *   `pytest` assertions are used to verify that the outputs match.

## Defining a New YAML Test Case (Manual Tests)

To add a new manually defined test case:

1.  Create a new YAML file in the `tests/compatibility/testcases/` directory (e.g., `my_new_test.yaml`).
2.  Follow this structure:

    ```yaml
    name: MyNewTest # Unique name (used for output directory if not using Hypothesis)
    description: "A brief description of what this test case covers."
    type_definition: "string"  # String representing the cty type (e.g., "list(number)")
    raw_input: "some data"     # Raw input. For null, use `null`. For unknown, use `"__unknown__"`.
    ```

3.  The `type_definition` string should be parsable by `parse_type_definition` in both Python and Go generators.

## Running the Tests

1.  **Prerequisites:**
    *   Ensure Python environment with `pytest`, `hypothesis`, and `pyyaml` is set up.
    *   Ensure Go is installed and `go-cty` & `yaml.v2` dependencies are available for the Go generator (run `go get` in `tests/compatibility` if needed).
    *   The `pyvider.cty` library must be installed or available in the `PYTHONPATH`.

2.  **Execute Pytest:**
    *   Navigate to the root of the `pyvider-cty` repository.
    *   Run pytest:
        ```bash
        pytest tests/compatibility/test_cty_compatibility.py
        ```
    *   Pytest will discover and run all tests:
        *   The YAML-based tests will invoke the Python and Go generators as subprocesses to create JSON files in the `tests/compatibility/output/` directory and then compare these files.
        *   The Hypothesis-based tests will generate data on the fly, run the Python `pyvider.cty` logic directly, invoke the Go generator (with data passed via a temporary YAML file and output captured from stdout), and compare the results.

## JSON Value Representation

To facilitate comparison, `*_value.json` files (and JSON captured from Go's stdout for Hypothesis tests) adhere to:

```json
{
  "type_name": "string", // Or "list(number)", "object({name=string})", etc.
  "value": "actual value here", // For collections, list/dict of structured items. Null if unknown/null.
  "is_unknown": false,
  "is_null": false,
  "marks": [] // List of stringified marks. Empty list `[]` if no marks.
}
```

*   For `unknown` values: `"is_unknown": true`, `"value": null`.
*   For `null` values: `"is_null": true`, `"value": null`.
*   Numbers are represented as strings to maintain precision.
