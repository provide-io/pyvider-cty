
# Pyvider CTY: Strong Typing System Requirements

I'm working on the `pyvider.cty` module, which is a Python implementation of the Go-CTY type system. This implementation has specific requirements that must be maintained:

## Core Principles

1. **Strong Typing at All Times**: The CTY implementation must maintain strong typing throughout. Type information is never lost or implicitly converted.

2. **Type Wrapping**: All values in the system are wrapped in their appropriate type containers (e.g., CtyString, CtyNumber, CtyList). These wrappers must remain intact throughout all operations.

3. **No Type Fallbacks**: Unlike typical Python code, the CTY system does not allow for implicit type conversions or fallbacks. If a method returns a CtyString, tests must expect a CtyString, not unwrap to a Python string.

4. **Immutability**: CTY values are immutable. Operations that would modify a value must instead return a new value instance.

## Testing Requirements

When writing or fixing tests for this system:

1. Tests must verify the correct typing is maintained, not just the correct values.
2. If a method returns a `CtyString`, tests should assert it is a `CtyString` and then check its `.value` attribute.
3. Do not change the type system to fit the tests. The tests must be adjusted to expect the proper strongly-typed behavior.
4. The focus is on verifying the CTY type system works correctly according to Go-CTY specifications.

## Common Issues

- Tests failing because they expect a Python primitive (str, int) when the system correctly returns a wrapped CTY value
- Tests trying to use Python's duck typing when CTY requires explicit type checking
- Tests expecting mutability when CTY values are immutable

The implementation must prioritize type safety and correctness over convenience or Python's typical dynamic typing flexibility.
