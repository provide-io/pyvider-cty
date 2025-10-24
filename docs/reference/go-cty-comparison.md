# Comparison with Go-Cty

`pyvider.cty` is a Python implementation of the `cty` type system, which was originally developed in Go as `go-cty` for use in HashiCorp's Terraform. While `pyvider.cty` aims to be a faithful implementation of the `cty` specification, there are some differences between the two libraries due to the differences between Python and Go.

## Key Differences

| Feature | `go-cty` | `pyvider.cty` | Notes |
|---|---|---|---|
| **Language** | Go | Python | The most obvious difference is the language. `go-cty` is written in Go, while `pyvider.cty` is written in Python. |
| **API** | The `go-cty` API is designed to be idiomatic Go. | The `pyvider.cty` API is designed to be idiomatic Python. | This means that the two APIs are not directly compatible, but the underlying concepts are the same. |
| **Extensibility** | `go-cty` can be extended with custom types and functions. | `pyvider.cty` can also be extended with custom types and functions. | The mechanism for extension is different in the two libraries. |
| **Performance** | `go-cty` is a compiled language, so it is generally faster than `pyvider.cty`. | `pyvider.cty` is an interpreted language, so it is generally slower than `go-cty`. | However, `pyvider.cty` is still fast enough for most use cases. |

## Feature Parity

`pyvider.cty` aims to have feature parity with `go-cty`, but there may be some features that are not yet implemented. If you find a feature that is missing, please open an issue on the project's GitHub repository.

## Conclusion

`pyvider.cty` is a powerful and flexible type system for Python that is based on the well-established `cty` specification. While there are some differences between `pyvider.cty` and `go-cty`, the two libraries are conceptually very similar. If you are familiar with `go-cty`, you should have no trouble learning how to use `pyvider.cty`.
