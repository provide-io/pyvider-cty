# Chapter 13: Configuration Variables

`pyvider.cty` is designed to be a library with minimal configuration. The core functionality of the library does not require any special setup. However, there are a few environment variables that can be used to control some aspects of the library's behavior, particularly for testing and debugging.

| Environment Variable Name | Type | Default Value | Description |
|---|---|---|---|
| `PYVIDER_CTY_TEST_BENCHMARK` | `bool` | `false` | If "true", enables performance benchmark tests. |
| `PYVIDER_CTY_LOG_LEVEL` | `str` | `INFO` | Logging level for `pyvider.telemetry`. |
