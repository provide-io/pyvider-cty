# Glossary

This glossary defines key terms and concepts used throughout the `pyvider.cty` documentation.

## Core Concepts

*   **Type**: A `pyvider.cty` type defines the shape and constraints of your data. Types act as schemas against which raw Python data is validated.
*   **Value**: A `pyvider.cty` value is an instance of a `cty` type. It holds the actual data and is immutable. Represented by the `CtyValue` class.
*   **Validation**: The process of checking if a raw Python value conforms to a given `cty` type. Validation returns a `CtyValue` if successful or raises a `CtyValidationError` if the data doesn't match the schema.
*   **Conversion**: The process of transforming values between different `cty` types or between `cty` values and raw Python values. More flexible than validation.

## Type Categories

*   **Primitive Type**: A basic building block of the type system, such as `CtyString`, `CtyNumber`, or `CtyBool`. Represents single, atomic values.
*   **Collection Type**: A type that represents a homogeneous collection of other types, such as `CtyList`, `CtySet`, or `CtyMap`. All elements in a collection must be of the same type.
*   **Structural Type**: A type that represents more complex, structured data with heterogeneous elements, such as `CtyObject` or `CtyTuple`. Different positions or attributes can have different types.
*   **Dynamic Type**: A special type (`CtyDynamic`) that can represent any type of value, with the actual type determined at runtime.
*   **Capsule**: A special type that allows you to encapsulate and protect foreign data types within the `cty` system. Useful for wrapping non-cty objects like file handles or database connections.

## Special Values

*   **Null**: A special value that represents the explicit absence of a value. Created with `CtyValue.null(type)`. Different from Python's `None`.
*   **Unknown**: A special value that represents a value that is not yet known but will be determined later. Created with `CtyValue.unknown(type)`. Common in Terraform for values computed during apply.

## Advanced Features

*   **Mark**: A piece of metadata that is attached to a `cty` value without modifying the value itself. Represented by the `CtyMark` class. Useful for tracking sensitive data or adding annotations.
*   **Function**: A `pyvider.cty` function is a built-in operation for manipulating `cty` values. All functions operate on and return `CtyValue` instances while maintaining immutability.
*   **Type Unification**: The process of finding the most specific type that can represent all given types. Used by the `unify()` function to determine compatible types.
*   **Path**: A sequence of steps (`CtyPath`) used to navigate through nested data structures. Used for precise error reporting and programmatic traversal.
*   **Recursion Detection**: A mechanism to prevent infinite loops when validating circular or deeply nested data structures. Implemented via the `@with_recursion_detection` decorator.

## Interoperability

*   **go-cty**: The Go implementation of the cty type system by HashiCorp. `pyvider.cty` is designed for compatibility with go-cty.
*   **MessagePack**: A binary serialization format used for cross-language data exchange. `pyvider.cty` uses MessagePack for go-cty compatibility.
*   **Terraform Type String**: A string representation of cty types used by Terraform (e.g., `"list(string)"`, `"object({name=string})"`). Can be parsed using `parse_tf_type_to_ctytype()`.
*   **NFC Normalization**: Unicode normalization form used for string values and object attribute names to ensure consistent comparison and hashing across different Unicode representations.
