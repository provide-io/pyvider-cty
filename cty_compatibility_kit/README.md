# CTY Compatibility Test Kit

This directory contains a standalone test kit for `pyvider.cty` to ensure compatibility with the reference `go-cty` implementation.
It uses `pytest` for test execution and `Hypothesis` for property-based test data generation, covering JSON and Msgpack serialization formats.

## Structure

- `test_cty_compatibility.py`: The main pytest test suite. It includes tests for:
    - YAML-defined test cases (legacy).
    - Hypothesis-driven JSON value comparison between Python and Go.
    - Hypothesis-driven Python-side Msgpack serialization/deserialization roundtrip.
    - Hypothesis-driven cross-language Msgpack byte-level comparison.
    - Hypothesis-driven "Msgpack to JSON loaded" comparison (ensuring both languages interpret Python-generated Msgpack consistently).
- `py_cty_generator.py`: Python script to generate `pyvider.cty` type/value representations (primarily for older YAML tests).
- `go_src/`: Contains the Go cty data generator (`go_cty_generator.go`), its Go module files (`go.mod`, `go.sum`), and compiled binary after `go build`.
    - The Go generator now supports various command-line flags for controlling input and output formats.
- `testcases/`: Contains YAML files defining specific, non-Hypothesis test scenarios.
- `output/`: Default directory where YAML-based tests store their generated JSON files for comparison (can be cleaned).
- `hypothesis_temp_yaml/`: Directory where Hypothesis-based tests store temporary YAML and Msgpack files used to feed the Go generator.

## Go Generator (`go_src/go_cty_generator.go`)

The Go generator has been enhanced to support different input and output formats:

-   **Input Configuration:**
    -   `<path_to_testcase.yaml>`: (Positional argument) Path to a YAML file defining the test case name, cty type string, and raw input for Go. This is always required, though its `raw_input` may be ignored if `-inputFileFormat msgpack` is used.
    -   `-inputFileFormat <format>`: Specifies the format of the main input data.
        -   `yaml` (default): Uses `raw_input` from the positional YAML file.
        -   `msgpack`: Ignores `raw_input` from positional YAML. Instead, reads Msgpack data from the file specified by `-inputFile`.
    -   `-inputFile <path>`: Path to a pre-serialized Msgpack input file. Used when `-inputFileFormat msgpack`.
    -   `-targetTypeString <type_str>`: The target cty type string for interpreting the data from `-inputFile` when `-inputFileFormat msgpack`.

-   **Output Configuration:**
    -   `-stdout`: If present, outputs the primary result (JSON or Msgpack value) to standard output instead of a file. Type information (`go_type.json`) is still written to file unless input is Msgpack.
    -   `-format <format>`: Specifies the output format for the cty value.
        -   `json` (default): Outputs the value as a JSON object.
        -   `msgpack`: Outputs the value as Msgpack bytes.
    -   When `-inputFileFormat msgpack` is used, the Go generator is hardcoded to output the loaded value as JSON to stdout, facilitating the "Msgpack to JSON loaded" tests.

## Prerequisites

- Python 3.13+
- `pytest`, `hypothesis`, `pyyaml`, `msgpack` Python packages. (Ensure `msgpack` is installed: `pip install msgpack`)
- Go (latest stable version recommended, with `GOBIN` in `PATH` if running compiled binaries, or just `go` for `go run`). The test suite uses `go run`.
- `pyvider.cty` library installed or available in `PYTHONPATH`.
- The `github.com/vmihailenco/msgpack/v5` Go package (will be fetched by `go get` or `go mod tidy` via the test setup or manually in `go_src`).

## Running Tests

Navigate to the root of the repository and run:

```bash
python -m pytest cty_compatibility_kit/test_cty_compatibility.py
```
Or, if `cty_compatibility_kit` is added to `pythonpath` or `pytest` is configured to find it:
```bash
pytest cty_compatibility_kit
```

This will execute all tests, including the new Msgpack compatibility tests.
